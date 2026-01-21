---
title: "Audit & Compliance Patterns"
description: "Implementing audit trails and regulatory compliance with Apache Cassandra. Covers immutable audit logs, data retention policies, consent management, access logging, and GDPR/HIPAA/SOX compliance patterns."
meta:
  - name: keywords
    content: "Cassandra audit trail, compliance, GDPR, HIPAA, SOX, data retention, consent management"
search:
  boost: 3
---

# Audit & Compliance Patterns

Regulated industries (finance, healthcare, government, and increasingly all industries handling personal data) require systems that can demonstrate what happened, when, and by whom. Audit and compliance patterns provide the technical foundation for meeting regulatory requirements while maintaining operational efficiency.

---

## The Compliance Imperative

Regulatory frameworks impose specific requirements on data management:

| Regulation | Scope | Key Requirements |
|------------|-------|------------------|
| **GDPR** | EU personal data | Consent tracking, right to erasure, data portability, breach notification |
| **HIPAA** | US healthcare | Access controls, audit trails, minimum necessary access, breach notification |
| **SOX** | US public companies | Internal controls, audit trails, data integrity, retention requirements |
| **PCI-DSS** | Payment card data | Access logging, encryption, retention limits, audit trails |
| **CCPA** | California consumer data | Right to know, right to delete, opt-out of sale |

These are not suggestions; they are legal requirements with significant penalties for non-compliance. Technical architecture must support compliance by design, not as an afterthought.

---

## Why Cassandra for Audit Data

Audit logs could be written to files, shipped to object storage, or streamed to a data lake. The reason to store audit data in Cassandra is that compliance requires more than storage; it requires queryable access to individual records.

**Compliance queries require individual record access:**

- "Show me all access to patient record X in the last 90 days"
- "List all actions performed by user Y during this investigation period"
- "Retrieve the complete audit trail for this transaction"
- "Find all failed login attempts from this IP address"

These queries must return results in seconds, not hours. When auditors or investigators request information, batch processing is not acceptable.

**Cassandra characteristics that align with audit requirements:**

| Requirement | Cassandra Capability |
|-------------|---------------------|
| Individual record lookup | Efficient primary key queries |
| Time-range queries | Clustering column ordering |
| High write throughput | Append-only writes, no read-before-write |
| Durability | Configurable replication factor |
| Retention flexibility | TTL or explicit deletion |
| Tamper resistance | Immutable once written (no in-place updates) |

File-based or object storage systems excel at batch analytics but lack the query flexibility compliance demands. Cassandra provides both: high-throughput ingestion for capturing every event, and efficient queries for investigating specific records.

---

## Immutable Audit Logs

The foundation of compliance is an immutable record of what happened.

### Audit Event Schema

```sql
CREATE TABLE audit_events (
    partition_key TEXT,           -- Year-month or tenant-month
    event_id TIMEUUID,
    event_type TEXT,
    event_time TIMESTAMP,
    actor_id UUID,
    actor_type TEXT,              -- USER, SERVICE, SYSTEM
    actor_ip TEXT,
    resource_type TEXT,
    resource_id TEXT,
    action TEXT,                  -- CREATE, READ, UPDATE, DELETE, LOGIN, etc.
    outcome TEXT,                 -- SUCCESS, FAILURE, DENIED
    previous_state BLOB,          -- For change tracking
    new_state BLOB,
    metadata MAP<TEXT, TEXT>,
    request_id UUID,              -- Correlation ID
    session_id UUID,
    PRIMARY KEY ((partition_key), event_id)
) WITH CLUSTERING ORDER BY (event_id DESC)
  AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
  };
```

**Design rationale**:

- **Time-based partition key**: Enables efficient range queries and partition management
- **TIMEUUID clustering**: Maintains chronological order with uniqueness
- **Previous/new state**: Supports full change tracking when needed
- **TWCS compaction**: Optimizes for time-ordered, append-only data
- **No TTL on audit table**: Retention is managed explicitly per compliance requirements

### Audit Event Capture

Integrate audit logging throughout the application:

```java
@Aspect
@Component
public class AuditAspect {

    private final AuditService auditService;

    @Around("@annotation(audited)")
    public Object auditOperation(ProceedingJoinPoint joinPoint,
                                  Audited audited) throws Throwable {
        AuditContext context = AuditContext.current();
        String resourceType = audited.resourceType();
        String action = audited.action();

        // Capture pre-state if tracking changes
        Object previousState = null;
        if (audited.trackChanges()) {
            previousState = captureCurrentState(joinPoint, audited);
        }

        Object result;
        String outcome;

        try {
            result = joinPoint.proceed();
            outcome = "SUCCESS";
        } catch (AccessDeniedException e) {
            outcome = "DENIED";
            throw e;
        } catch (Exception e) {
            outcome = "FAILURE";
            throw e;
        } finally {
            // Always log, even on failure
            auditService.logEvent(AuditEvent.builder()
                .eventType(action + "_" + resourceType)
                .actorId(context.getUserId())
                .actorType(context.getActorType())
                .actorIp(context.getClientIp())
                .resourceType(resourceType)
                .resourceId(extractResourceId(joinPoint, audited))
                .action(action)
                .outcome(outcome)
                .previousState(serialize(previousState))
                .newState(outcome.equals("SUCCESS") ?
                    serialize(captureNewState(joinPoint, result, audited)) : null)
                .requestId(context.getRequestId())
                .sessionId(context.getSessionId())
                .build());
        }

        return result;
    }
}

// Usage
@Audited(resourceType = "PATIENT_RECORD", action = "READ", trackChanges = false)
public PatientRecord getPatientRecord(UUID patientId) {
    return patientRepository.findById(patientId);
}

@Audited(resourceType = "PATIENT_RECORD", action = "UPDATE", trackChanges = true)
public PatientRecord updatePatientRecord(UUID patientId, PatientUpdate update) {
    // Implementation
}
```

### Tamper Evidence

Prevent undetected modification of audit records:

```java
public class TamperEvidentAuditService {

    public void logEvent(AuditEvent event) {
        // Get previous event's hash for chaining
        String previousHash = getLastEventHash(event.getPartitionKey());

        // Calculate hash including previous hash (blockchain-like chaining)
        String eventHash = calculateHash(event, previousHash);
        event.setEventHash(eventHash);
        event.setPreviousHash(previousHash);

        // Store event
        auditRepository.save(event);

        // Update hash index
        updateLastEventHash(event.getPartitionKey(), eventHash);
    }

    private String calculateHash(AuditEvent event, String previousHash) {
        String content = String.join("|",
            event.getEventId().toString(),
            event.getEventType(),
            event.getActorId().toString(),
            event.getResourceId(),
            event.getAction(),
            previousHash != null ? previousHash : "GENESIS"
        );

        return DigestUtils.sha256Hex(content);
    }

    public boolean verifyChainIntegrity(String partitionKey) {
        List<AuditEvent> events = auditRepository
            .findByPartitionKey(partitionKey);

        String expectedPreviousHash = null;

        for (AuditEvent event : events) {
            // Verify previous hash link
            if (!Objects.equals(event.getPreviousHash(), expectedPreviousHash)) {
                log.error("Chain broken at event {}", event.getEventId());
                return false;
            }

            // Verify event hash
            String calculatedHash = calculateHash(event, expectedPreviousHash);
            if (!calculatedHash.equals(event.getEventHash())) {
                log.error("Hash mismatch at event {}", event.getEventId());
                return false;
            }

            expectedPreviousHash = event.getEventHash();
        }

        return true;
    }
}
```

---

## Data Retention Management

Compliance requires both retaining data long enough and deleting it when required.

### Retention Policy Schema

```sql
CREATE TABLE retention_policies (
    policy_id UUID,
    data_category TEXT,          -- AUDIT_LOGS, TRANSACTION_DATA, PII, etc.
    retention_period_days INT,
    legal_hold_eligible BOOLEAN,
    deletion_strategy TEXT,      -- HARD_DELETE, SOFT_DELETE, ANONYMIZE
    regulatory_basis TEXT,       -- GDPR, HIPAA, SOX, etc.
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (policy_id)
);

CREATE TABLE data_retention_tracking (
    data_category TEXT,
    record_date DATE,
    record_id UUID,
    retention_policy_id UUID,
    retention_expires_at TIMESTAMP,
    legal_hold BOOLEAN,
    legal_hold_reason TEXT,
    deletion_scheduled_at TIMESTAMP,
    deletion_completed_at TIMESTAMP,
    PRIMARY KEY ((data_category, record_date), record_id)
) WITH default_time_to_live = 0;  -- No automatic expiry
```

### Retention Enforcement

```java
@Scheduled(cron = "0 0 2 * * *")  // Daily at 2 AM
public class RetentionEnforcer {

    public void enforceRetention() {
        List<RetentionPolicy> policies = policyRepository.findAll();

        for (RetentionPolicy policy : policies) {
            LocalDate cutoffDate = LocalDate.now()
                .minusDays(policy.getRetentionPeriodDays());

            // Find records eligible for deletion
            List<DataRetentionRecord> eligible = trackingRepository
                .findExpiredRecords(policy.getDataCategory(), cutoffDate);

            for (DataRetentionRecord record : eligible) {
                if (record.isLegalHold()) {
                    log.info("Skipping {} due to legal hold", record.getRecordId());
                    continue;
                }

                try {
                    applyDeletionStrategy(policy, record);
                    markDeletionComplete(record);
                } catch (Exception e) {
                    log.error("Failed to delete {}", record.getRecordId(), e);
                    alertRetentionFailure(record, e);
                }
            }

            metrics.recordRetentionRun(policy.getDataCategory(), eligible.size());
        }
    }

    private void applyDeletionStrategy(RetentionPolicy policy,
                                       DataRetentionRecord record) {
        switch (policy.getDeletionStrategy()) {
            case "HARD_DELETE":
                hardDelete(record);
                break;
            case "SOFT_DELETE":
                softDelete(record);
                break;
            case "ANONYMIZE":
                anonymize(record);
                break;
            default:
                throw new IllegalArgumentException(
                    "Unknown strategy: " + policy.getDeletionStrategy());
        }
    }
}
```

### Legal Hold

Suspend retention deletion for specific records:

```java
public void applyLegalHold(UUID recordId, String dataCategory,
                          String reason, String authorizedBy) {
    // Update retention tracking
    DataRetentionRecord record = trackingRepository.find(dataCategory, recordId);
    record.setLegalHold(true);
    record.setLegalHoldReason(reason);
    trackingRepository.save(record);

    // Audit the legal hold
    auditService.logEvent(AuditEvent.builder()
        .eventType("LEGAL_HOLD_APPLIED")
        .resourceType(dataCategory)
        .resourceId(recordId.toString())
        .action("LEGAL_HOLD")
        .metadata(Map.of(
            "reason", reason,
            "authorized_by", authorizedBy
        ))
        .build());
}
```

---

## Consent Management

GDPR and similar regulations require tracking user consent for data processing.

### Consent Schema

```sql
CREATE TABLE user_consents (
    user_id UUID,
    consent_type TEXT,            -- MARKETING, ANALYTICS, DATA_SHARING, etc.
    consent_version TEXT,
    granted BOOLEAN,
    granted_at TIMESTAMP,
    withdrawn_at TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    consent_text_hash TEXT,       -- Hash of the consent text shown
    PRIMARY KEY ((user_id), consent_type)
);

CREATE TABLE consent_history (
    user_id UUID,
    consent_type TEXT,
    event_time TIMESTAMP,
    event_type TEXT,              -- GRANTED, WITHDRAWN, UPDATED
    consent_version TEXT,
    ip_address TEXT,
    PRIMARY KEY ((user_id, consent_type), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);
```

### Consent Service

```java
public class ConsentService {

    public void grantConsent(UUID userId, ConsentRequest request) {
        Instant now = Instant.now();

        // Record current consent state
        UserConsent consent = new UserConsent();
        consent.setUserId(userId);
        consent.setConsentType(request.getConsentType());
        consent.setConsentVersion(request.getConsentVersion());
        consent.setGranted(true);
        consent.setGrantedAt(now);
        consent.setIpAddress(request.getIpAddress());
        consent.setUserAgent(request.getUserAgent());
        consent.setConsentTextHash(hashConsentText(request.getConsentText()));

        consentRepository.save(consent);

        // Record in history
        consentHistoryRepository.save(new ConsentHistory(
            userId, request.getConsentType(), now, "GRANTED",
            request.getConsentVersion(), request.getIpAddress()
        ));

        // Audit
        auditService.logEvent(AuditEvent.builder()
            .eventType("CONSENT_GRANTED")
            .actorId(userId)
            .resourceType("USER_CONSENT")
            .resourceId(request.getConsentType())
            .action("GRANT")
            .metadata(Map.of(
                "consent_version", request.getConsentVersion(),
                "ip_address", request.getIpAddress()
            ))
            .build());
    }

    public void withdrawConsent(UUID userId, String consentType, String reason) {
        UserConsent consent = consentRepository.find(userId, consentType);

        if (consent == null || !consent.isGranted()) {
            throw new ConsentNotFoundException(userId, consentType);
        }

        consent.setGranted(false);
        consent.setWithdrawnAt(Instant.now());
        consentRepository.save(consent);

        // Record in history
        consentHistoryRepository.save(new ConsentHistory(
            userId, consentType, Instant.now(), "WITHDRAWN",
            consent.getConsentVersion(), getCurrentIp()
        ));

        // Trigger downstream actions (stop processing, etc.)
        eventPublisher.publish(new ConsentWithdrawnEvent(userId, consentType));
    }

    public boolean hasConsent(UUID userId, String consentType) {
        UserConsent consent = consentRepository.find(userId, consentType);
        return consent != null && consent.isGranted();
    }
}
```

### Consent-Gated Processing

```java
public class ConsentGatedService {

    public void processUserData(UUID userId, String processingType) {
        String requiredConsent = consentMapping.get(processingType);

        if (!consentService.hasConsent(userId, requiredConsent)) {
            auditService.logEvent(AuditEvent.builder()
                .eventType("PROCESSING_BLOCKED")
                .actorId(userId)
                .resourceType("USER_DATA")
                .action(processingType)
                .outcome("DENIED")
                .metadata(Map.of(
                    "reason", "Missing consent: " + requiredConsent
                ))
                .build());

            throw new ConsentRequiredException(userId, requiredConsent);
        }

        // Proceed with processing
        doProcess(userId);
    }
}
```

---

## Access Logging

Track who accessed what data and when.

### Access Log Schema

```sql
CREATE TABLE data_access_log (
    date_bucket DATE,
    access_id TIMEUUID,
    user_id UUID,
    data_subject_id UUID,         -- Whose data was accessed
    resource_type TEXT,
    resource_id TEXT,
    access_type TEXT,             -- VIEW, DOWNLOAD, EXPORT, PRINT
    fields_accessed SET<TEXT>,    -- Which fields were accessed
    access_reason TEXT,           -- Required for HIPAA minimum necessary
    access_time TIMESTAMP,
    client_ip TEXT,
    user_agent TEXT,
    PRIMARY KEY ((date_bucket), access_id)
) WITH CLUSTERING ORDER BY (access_id DESC)
  AND default_time_to_live = 31536000;  -- 1 year
```

### Automatic Access Logging

```java
@Aspect
@Component
public class DataAccessLogger {

    @AfterReturning(pointcut = "@annotation(logAccess)", returning = "result")
    public void logDataAccess(JoinPoint joinPoint, LogAccess logAccess,
                              Object result) {
        AccessContext context = AccessContext.current();

        // Extract data subject from result
        UUID dataSubjectId = extractDataSubjectId(result, logAccess);

        // Determine which fields were accessed
        Set<String> fieldsAccessed = determineFieldsAccessed(result, logAccess);

        accessLogRepository.save(new DataAccessLog(
            LocalDate.now(),
            Uuids.timeBased(),
            context.getUserId(),
            dataSubjectId,
            logAccess.resourceType(),
            extractResourceId(joinPoint, logAccess),
            logAccess.accessType(),
            fieldsAccessed,
            context.getAccessReason(),
            Instant.now(),
            context.getClientIp(),
            context.getUserAgent()
        ));
    }
}

// Usage
@LogAccess(resourceType = "PATIENT_RECORD", accessType = "VIEW")
public PatientRecord viewPatientRecord(UUID patientId) {
    return patientRepository.findById(patientId);
}
```

---

## Right to Erasure (GDPR Article 17)

Implement the "right to be forgotten":

```java
public class ErasureService {

    public ErasureResult processErasureRequest(UUID userId, String requestReason) {
        // Validate request
        if (!canErase(userId)) {
            return ErasureResult.denied("Legal hold or retention requirement");
        }

        ErasureResult result = new ErasureResult(userId);

        // Find all user data across tables
        List<DataLocation> dataLocations = dataDiscoveryService
            .findUserData(userId);

        for (DataLocation location : dataLocations) {
            try {
                if (location.getRetentionPolicy().allowsErasure()) {
                    eraseData(location);
                    result.addErased(location);
                } else {
                    anonymizeData(location);
                    result.addAnonymized(location);
                }
            } catch (Exception e) {
                result.addFailed(location, e.getMessage());
            }
        }

        // Audit the erasure
        auditService.logEvent(AuditEvent.builder()
            .eventType("DATA_ERASURE")
            .actorId(getCurrentUserId())
            .resourceType("USER_DATA")
            .resourceId(userId.toString())
            .action("ERASE")
            .outcome(result.isComplete() ? "SUCCESS" : "PARTIAL")
            .metadata(Map.of(
                "request_reason", requestReason,
                "erased_count", String.valueOf(result.getErasedCount()),
                "anonymized_count", String.valueOf(result.getAnonymizedCount()),
                "failed_count", String.valueOf(result.getFailedCount())
            ))
            .build());

        return result;
    }

    private void anonymizeData(DataLocation location) {
        // Replace PII with anonymous values while preserving structure
        // for analytics and audit purposes
        switch (location.getDataType()) {
            case "EMAIL":
                updateField(location, "anonymized_" + hash(location.getValue()));
                break;
            case "NAME":
                updateField(location, "REDACTED");
                break;
            case "ADDRESS":
                // Keep country/region for analytics, remove specifics
                updateField(location, extractRegion(location.getValue()));
                break;
            // ... other PII types
        }
    }
}
```

---

## Compliance Reporting

Generate reports for auditors and regulators:

```java
public class ComplianceReportService {

    public AccessReport generateAccessReport(UUID dataSubjectId,
                                             LocalDate startDate,
                                             LocalDate endDate) {
        // All access to this person's data
        List<DataAccessLog> accesses = accessLogRepository
            .findByDataSubject(dataSubjectId, startDate, endDate);

        return AccessReport.builder()
            .dataSubjectId(dataSubjectId)
            .period(startDate, endDate)
            .totalAccesses(accesses.size())
            .uniqueAccessors(accesses.stream()
                .map(DataAccessLog::getUserId)
                .distinct()
                .count())
            .accessesByType(groupByAccessType(accesses))
            .accessesByResource(groupByResourceType(accesses))
            .details(accesses)
            .build();
    }

    public AuditTrailReport generateAuditTrail(String resourceType,
                                               String resourceId,
                                               LocalDate startDate,
                                               LocalDate endDate) {
        List<AuditEvent> events = auditRepository
            .findByResource(resourceType, resourceId, startDate, endDate);

        return AuditTrailReport.builder()
            .resourceType(resourceType)
            .resourceId(resourceId)
            .period(startDate, endDate)
            .events(events)
            .chainIntegrityVerified(verifyChainIntegrity(events))
            .build();
    }
}
```

---

## Monitoring Compliance

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `compliance.audit_events_per_second` | Audit log write rate | Below baseline |
| `compliance.retention_deletions` | Records deleted per day | Above normal |
| `compliance.legal_holds_active` | Current legal holds | Context-dependent |
| `compliance.consent_withdrawal_rate` | Consent withdrawals/day | Sudden increase |
| `compliance.access_denials` | Unauthorized access attempts | Any occurrence |
| `compliance.erasure_requests` | Data erasure requests | Trend monitoring |

### Compliance Health Check

```java
@Component
public class ComplianceHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        Map<String, Object> details = new HashMap<>();

        // Verify audit chain integrity (sample check)
        boolean chainHealthy = verifyRecentChainIntegrity();
        details.put("audit_chain_integrity", chainHealthy);

        // Check retention enforcement is running
        boolean retentionHealthy = retentionService.isRunning();
        details.put("retention_enforcement", retentionHealthy);

        // Check for overdue legal hold reviews
        int overdueHolds = legalHoldService.countOverdueReviews();
        details.put("overdue_legal_holds", overdueHolds);

        if (!chainHealthy || !retentionHealthy || overdueHolds > 0) {
            return Health.down().withDetails(details).build();
        }

        return Health.up().withDetails(details).build();
    }
}
```

---

## Summary

Compliance is not a feature to be added; it is an architectural constraint that shapes the entire system:

1. **Immutable audit logs** with tamper evidence provide the foundation
2. **Retention management** balances keeping data long enough with deleting it when required
3. **Consent tracking** ensures lawful basis for processing
4. **Access logging** answers "who saw what, when"
5. **Erasure capability** implements the right to be forgotten
6. **Compliance reporting** enables audit and regulatory response

Cassandra serves audit workloads effectively because compliance requires both high-throughput ingestion and efficient individual record queries. Unlike file-based systems optimized for batch processing, Cassandra enables the rapid lookups that auditors and investigators demand while handling the write volume of comprehensive event capture.

---

## Related Documentation

- [Event Sourcing](event-sourcing.md) - Complete event history
- [Ledger Pattern](ledger.md) - Financial audit requirements
- [Multi-Tenant Isolation](multi-tenant.md) - Tenant data separation
