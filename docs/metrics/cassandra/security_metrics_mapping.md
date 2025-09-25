# AxonOps Security Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Security dashboard and event sources.

## Dashboard Overview

The Security dashboard provides comprehensive security monitoring for Cassandra, including authentication tracking, authorization monitoring, and audit logging of DDL, DCL, and DML queries. It also tracks JMX access events for complete security visibility.

## Metrics Mapping

### Authentication Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_authentication_success` | Successful authentication attempts | `username`, `axonfunction` (rate), `dc`, `rack`, `host_id` |

## Event-Based Security Monitoring

Unlike other dashboards that primarily use metrics, the Security dashboard is heavily event-driven, using AxonOps' event collection and filtering capabilities.

### Event Types and Filters

| Event Type | Source | Level | Description | Panel Usage |
|------------|--------|-------|-------------|-------------|
| `authentication` | Cassandra | `error` | Failed authentication attempts | Failed Authentications (timeline & table) |
| `DDL_query` | Cassandra | all | Data Definition Language queries (CREATE, ALTER, DROP) | DDL queries (timeline & table) |
| `DCL_query` | Cassandra | all | Data Control Language queries (GRANT, REVOKE) | DCL queries (timeline & table) |
| `DML_query` | Cassandra | all | Data Manipulation Language queries (SELECT, INSERT, UPDATE, DELETE) | DML queries (timeline & table) |
| `authorization` | Cassandra | `error` | Failed authorization attempts | Failed Authorizations (timeline & table) |
| `jmx` | System | all | JMX access events | JMX (timeline & table) |

## Query Examples

### Authentication Metrics
```promql
// Successful Authentications by User (Rate)
sum(cas_authentication_success{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (username)
```

### Event Filters
```json
# Failed Authentications
{
  "host_id": "$host_id",
  "level": "error",
  "type": "authentication"
}

# DDL Queries
{
  "host_id": "$host_id",
  "source": "Cassandra",
  "type": "DDL_query"
}

# DCL Queries
{
  "source": "Cassandra",
  "type": "DCL_query"
}

# DML Queries
{
  "host_id": "$host_id",
  "source": "Cassandra",
  "type": "DML_query"
}

# Failed Authorizations
{
  "level": "error",
  "source": "Cassandra",
  "type": "authorization"
}

# JMX Events
{
  "host_id": "$host_id",
  "type": "jmx"
}
```

## Panel Organization

### Authentications Section
- **Failed Authentications** - Timeline view of authentication failures

- **Failed Authentications** - Table view with detailed event information

### Cassandra Queries Section
- **DDL queries** - Timeline of schema changes

- **DDL queries** - Table view of DDL operations

- **DCL queries** - Timeline of permission changes

- **DCL query** - Table view of DCL operations

- **DML queries** - Timeline of data modifications

- **DML queries** - Table view of DML operations

### Authorizations Section
- **Failed Authorizations** - Timeline of authorization failures

- **Failed Authorizations** - Table view with details

### JMX Section
- **JMX** - Timeline of JMX access events

- **JMX** - Table view of JMX operations

- **Successful Authentications by user (rate)** - Line chart showing authentication success rates per user

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **groupBy** - Dynamic grouping (dc, rack, host_id)

## Security Event Details

### Authentication Events
- **Failed Authentication**: Captured when invalid credentials are provided

- **Successful Authentication**: Tracked via metrics for rate analysis

- **Event Fields**: timestamp, host_id, username, source IP, error message

### DDL Query Events
- **CREATE**: Keyspace, table, index, user, role creation

- **ALTER**: Schema modifications

- **DROP**: Object deletion

- **Event Fields**: timestamp, host_id, username, query, keyspace, table

### DCL Query Events
- **GRANT**: Permission grants to users/roles

- **REVOKE**: Permission revocations

- **Event Fields**: timestamp, host_id, username, query, resource, permission

### DML Query Events
- **SELECT**: Data reads (when audit enabled)

- **INSERT/UPDATE**: Data modifications

- **DELETE**: Data removal

- **Event Fields**: timestamp, host_id, username, query, keyspace, table

### Authorization Events
- **Failed Authorization**: User lacks required permissions

- **Event Fields**: timestamp, host_id, username, resource, operation, required permission

### JMX Events
- **JMX Operations**: MBean access and modifications

- **Event Fields**: timestamp, host_id, operation, MBean, user

## Event Timeline vs Table Views

### Timeline Views (`events_timeline`)
- Visual representation of event frequency over time
- Quickly identify security incident patterns
- Useful for trend analysis and anomaly detection

### Table Views (`events_table`)
- Detailed event information
- Full query text and parameters
- User attribution and source information
- Sortable and searchable

## Security Best Practices

### Authentication Monitoring
**Monitor Failed Attempts**:

   - Set alerts for repeated failures
   - Identify brute force attempts
   - Track source IPs

**Track Success Rates**:

   - Monitor per-user authentication rates
   - Identify unusual access patterns
   - Detect compromised accounts

### Query Auditing
**DDL Monitoring**:

   - Track all schema changes
   - Maintain change history
   - Identify unauthorized modifications

**DCL Monitoring**:

   - Track permission changes
   - Audit role modifications
   - Ensure least privilege

**DML Monitoring** (if enabled):

   - Monitor sensitive data access
   - Track data modifications
   - Compliance reporting

### Authorization Monitoring
**Failed Authorization**:

   - Identify permission gaps
   - Detect privilege escalation attempts
   - Review access patterns

### JMX Security
**Access Monitoring**:

   - Track administrative operations
   - Monitor configuration changes
   - Audit system modifications

## Configuration Requirements

### Enable Security Features
- **Authentication**: Set `authenticator` in cassandra.yaml

- **Authorization**: Set `authorizer` in cassandra.yaml

- **Audit Logging**: Configure audit log settings

### AxonOps Agent Configuration
1. Enable event collection
2. Configure event retention
3. Set appropriate event filters

## Compliance and Reporting

### Audit Trail
- Complete record of security events
- User attribution for all actions
- Timestamp precision for forensics

### Compliance Support
- PCI DSS: Track access to cardholder data
- HIPAA: Monitor PHI access
- GDPR: Audit data access and modifications
- SOX: Track financial data access

### Reporting Capabilities
- Export event data for analysis
- Generate compliance reports
- Security incident investigation

## Troubleshooting

### No Events Showing
1. Verify security features enabled in Cassandra
2. Check AxonOps agent event collection
3. Confirm event filters match your setup

### Missing Authentication Metrics
1. Ensure authentication is enabled
2. Verify metrics collection is active
3. Check user activity exists

### Performance Impact
1. DML auditing can impact performance
2. Consider sampling for high-volume systems
3. Adjust event retention policies

## Notes

- Event-based panels don't show metrics queries
- Filters use exact matching for event fields
- Some panels filter by `$host_id`, others show cluster-wide
- Timeline and table views often paired for same event type
- The dashboard emphasizes security event visibility over performance metrics