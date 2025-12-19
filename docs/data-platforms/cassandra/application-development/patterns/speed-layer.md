---
title: "Speed Layer Pattern"
description: "Implementing high-performance data access layers with Apache Cassandra. Covers bank account transactions, session management, hot data caching, and low-latency query patterns for real-time applications."
meta:
  - name: keywords
    content: "Cassandra speed layer, bank account data, low-latency, hot data, mobile banking, Lambda architecture"
---

# Speed Layer Pattern

The speed layer provides low-latency access to frequently-accessed data: account balances, recent transactions, sessions, and real-time state. While Cassandra serves as both the speed layer and the system of record, optimal performance requires understanding which data is "hot" and designing schemas and access patterns accordingly.

---

## Speed Layer Architecture

Mobile banking has fundamentally changed how customers interact with their accounts. Where customers once checked balances monthly via statements, they now check multiple times daily via mobile apps. This shift has increased read throughput requirements by orders of magnitude—volumes that mainframe systems were never designed to handle.

In enterprise banking environments, Cassandra commonly serves as a speed layer in front of core banking systems. The mainframe remains the system of record for transactions and regulatory compliance, while Cassandra provides low-latency reads for mobile and web applications. CDC (Change Data Capture) keeps the speed layer synchronized.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam rectangle {
    BackgroundColor #F5F5F5
    BorderColor #333333
}
skinparam database {
    BackgroundColor #E8E8E8
    BorderColor #666666
}
skinparam queue {
    BackgroundColor #E3F2FD
    BorderColor #1976D2
}

title Banking Speed Layer Architecture

rectangle "Mobile/Web Apps" as app
database "Cassandra\n(Speed Layer)" as cass
database "Core Banking\n(Mainframe)\n(System of Record)" as legacy
queue "CDC Stream\n(Kafka/Debezium)" as cdc

app --> cass : Balance checks,\nrecent transactions\n(sub-ms latency)
app --> legacy : Transfers,\npayments
legacy --> cdc : Transaction events
cdc --> cass : Replicate changes

note bottom of cass
Mobile banking reality:
- Millions of balance checks per minute
- Mainframe handles 100s of TPS, not 100,000s
- CDC captures transactions in near real-time
- Cassandra serves read-heavy mobile traffic
- Core banking handles writes and compliance
end note
@enduml
```

---

## CDC Pipeline

When the core banking system is a mainframe, Cassandra provides a high-performance read layer for account balances and transaction history while CDC keeps data synchronized after each transaction.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
    ParticipantBorderColor #333333
}

title CDC Pipeline: Core Banking to Speed Layer

participant "Core Banking\n(CICS/DB2)" as mf
participant "CDC Agent\n(Connect CDC,\nDebezium)" as cdc
queue "Kafka" as kafka
participant "Stream\nProcessor" as proc
database "Cassandra\n(Speed Layer)" as cass
participant "Mobile App" as app

== Transaction Processing ==
mf -> mf : Debit/Credit\n(UPDATE balance)
mf -> cdc : Transaction log
cdc -> kafka : Change event\n{account, amount,\nnew_balance, txn_id}

== Transformation & Load ==
kafka -> proc : Consume changes
proc -> proc : Transform to\nCassandra schema
proc -> cass : Update balance,\nappend transaction

== Mobile App Reads ==
app -> cass : GET /accounts/{id}/balance\n(sub-ms latency)
cass --> app : Current balance

app -> cass : GET /accounts/{id}/transactions\n(recent 30 days)
cass --> app : Transaction list

note over mf, cass
Latency: typically 100ms-2s end-to-end
Customer sees updated balance within seconds of transaction
Mainframe handles ~500 TPS for transactions
Cassandra handles ~500,000 TPS for balance checks
end note
@enduml
```

### CDC Consumer Implementation

```java
@KafkaListener(topics = "corebanking.transactions")
public class TransactionCDCConsumer {

    private final CqlSession session;

    // Single INSERT updates static columns (balance) AND adds transaction row
    private final PreparedStatement insertTransaction = session.prepare(
        """
        INSERT INTO account_transactions (
            account_id, transaction_date, transaction_id,
            current_balance, available_balance, last_updated,
            transaction_time, transaction_type, amount,
            balance_after, description, merchant_name, category
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    );

    public void handleTransaction(TransactionEvent event) {
        // Single write: updates static balance + inserts transaction row
        session.execute(insertTransaction.bind(
            event.getAccountId(),
            event.getTransactionDate(),
            event.getTransactionId(),
            // Static columns (balance) - updated with each insert
            event.getNewBalance(),
            event.getAvailableBalance(),
            event.getTimestamp(),
            // Transaction row columns
            event.getTimestamp(),
            event.getTransactionType(),
            event.getAmount(),
            event.getNewBalance(),
            event.getDescription(),
            event.getMerchantName(),
            event.getCategory()
        ));
    }
}
```

### Handling CDC Lag

CDC introduces latency between the core banking system and speed layer. For most balance checks, sub-second staleness is acceptable. For operations like initiating a transfer, the application may need to verify against the source.

```java
public class AccountSpeedLayer {

    private final CqlSession cassandraSession;
    private final CoreBankingClient coreBankingClient;

    public AccountBalance getBalance(String accountId, BalanceCheckContext context) {
        // Read from speed layer (handles 99.9% of requests)
        AccountBalance cached = readFromCassandra(accountId);

        if (cached == null) {
            // New account not yet replicated - fall back to source
            return readFromCoreBanking(accountId);
        }

        // For display purposes (balance check), cached is fine
        if (context.isPureRead()) {
            return cached;
        }

        // For transfers/payments, verify against source if stale
        if (context.isTransactionInitiation()) {
            Instant sourceTimestamp = getSourceTimestamp(accountId);
            if (cached.getLastUpdated().isBefore(sourceTimestamp)) {
                return readFromCoreBanking(accountId);
            }
        }

        return cached;
    }
}
```

### Write-Through to Core Banking

Transactions (transfers, payments) always go through the core banking system. The speed layer is read-only for balance and transaction history:

```java
public class TransferService {

    public TransferResult initiateTransfer(TransferRequest request) {
        // Transactions MUST go through core banking for:
        // - Regulatory compliance (audit trail)
        // - Fraud detection
        // - Overdraft protection
        // - Inter-bank settlement
        TransferResult result = coreBankingClient.executeTransfer(
            request.getFromAccount(),
            request.getToAccount(),
            request.getAmount()
        );

        // CDC will propagate the balance change to Cassandra
        // within 1-2 seconds. No direct write to speed layer.

        return result;
    }
}
```

---

## The Hot Data Problem

Not all banking data is accessed equally. In a typical mobile banking application:

- **Current balance**: Checked on every app open, often multiple times per day
- **Recent transactions**: Last 7-30 days, accessed frequently
- **Session data**: Read/written multiple times per second during active sessions
- **Historical transactions**: Older than 90 days, accessed occasionally for statements

Treating all data identically leads to either over-provisioning (expensive) or under-serving hot data (slow). The speed layer pattern optimizes for the hot path while maintaining access to the full dataset.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam rectangle {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title Banking Hot Data Access Pattern

rectangle "Mobile App Requests" as app

rectangle "Hot Data (~5% of dataset)" as hot #FFCDD2 {
    rectangle "Current Balances" as bal #EF9A9A
    rectangle "Last 7 Days Transactions" as recent #EF9A9A
    rectangle "Active Sessions" as sess #EF9A9A
}

rectangle "Warm Data (~15%)" as warm #FFF9C4 {
    rectangle "30-90 Day Transactions" as trans #FFF59D
    rectangle "Pending Payments" as pend #FFF59D
}

rectangle "Cold Data (~80%)" as cold #E3F2FD {
    rectangle "Historical Transactions" as hist #90CAF9
    rectangle "Closed Accounts" as arch #90CAF9
}

app --> hot : **95% of reads**\n(sub-ms latency required)
app --> warm : 4% of reads
app --> cold : 1% of reads

note bottom of hot
Speed layer optimizes for this tier:
- Current balance always cached
- Recent transactions denormalized
- LOCAL_ONE consistency for reads
end note
@enduml
```

---

## Bank Account Data Architecture

Bank account data is the canonical speed layer use case: accessed constantly, latency-sensitive, and critical to application function. The schema separates current balances (hot) from transaction history (warm/cold).

### Schema Design

```sql
-- Account with transactions (static columns for account-level data)
CREATE TABLE account_transactions (
    account_id TEXT,
    transaction_date DATE,
    transaction_id TEXT,
    -- Static columns: shared across all rows in partition (the account)
    customer_id TEXT STATIC,
    account_type TEXT STATIC,       -- CHECKING, SAVINGS, CREDIT
    currency TEXT STATIC,
    current_balance DECIMAL STATIC,
    available_balance DECIMAL STATIC,
    last_updated TIMESTAMP STATIC,
    -- Per-transaction columns
    transaction_time TIMESTAMP,
    transaction_type TEXT,          -- DEBIT, CREDIT, TRANSFER, FEE
    amount DECIMAL,
    balance_after DECIMAL,
    description TEXT,
    merchant_name TEXT,
    category TEXT,
    PRIMARY KEY ((account_id), transaction_date, transaction_id)
) WITH CLUSTERING ORDER BY (transaction_date DESC, transaction_id DESC)
  AND default_time_to_live = 7776000;  -- 90-day TTL on transactions

-- Customer's accounts (for account list view)
CREATE TABLE accounts_by_customer (
    customer_id TEXT,
    account_id TEXT,
    account_type TEXT,
    account_name TEXT,              -- "Main Checking", "Savings"
    current_balance DECIMAL,
    PRIMARY KEY ((customer_id), account_type, account_id)
);
```

**Design rationale**:

- **Static columns for balance**: Current balance stored once per partition, returned with every transaction query—single read gets balance + transactions
- **TTL on transactions only**: Static columns (balance) are not affected by row TTL; only transaction rows expire
- **Date-clustered transactions**: Partition per account, clustered by date DESC for recent-first queries
- **Denormalized balance in accounts_by_customer**: Dashboard view gets all accounts in one query

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam database {
    BackgroundColor #E8E8E8
    BorderColor #666666
}

title Banking Speed Layer Tables

rectangle "Mobile App" as app {
    rectangle "Dashboard\n(all accounts)" as dash
    rectangle "Account Detail\n(balance + txns)" as detail
    rectangle "Transaction Search\n(by date range)" as search
}

database "accounts_by_customer" as tbl1 {
}
database "account_transactions\n(static: balance, account_type)\n(rows: transactions)" as tbl2 {
}

dash --> tbl1 : O(1) lookup\n(all accounts + balances)

detail --> tbl2 : Single query returns:\n- Static cols (balance)\n- Recent transaction rows
search --> tbl2 : Range query\n(date range within partition)

note bottom of tbl2
Static columns (balance) stored once per partition.
Transaction rows clustered by date DESC.
Single read returns balance + transactions.
90-day TTL expires transactions, not balance.
end note
@enduml
```

### Optimized Read Path

```java
public class AccountSpeedLayer {

    private final CqlSession session;
    private final LoadingCache<String, AccountBalance> balanceCache;
    private final LoadingCache<String, List<AccountSummary>> customerAccountsCache;

    // Single query gets static columns (balance) + transaction rows
    private final PreparedStatement selectAccountWithTransactions = session.prepare(
        "SELECT * FROM account_transactions WHERE account_id = ? LIMIT ?"
    );

    public AccountSpeedLayer(CqlSession session) {
        this.session = session;

        // Balance cache - very aggressive caching for hot data
        this.balanceCache = Caffeine.newBuilder()
            .maximumSize(1_000_000)            // 1M accounts
            .expireAfterWrite(Duration.ofSeconds(30))
            .refreshAfterWrite(Duration.ofSeconds(5))
            .buildAsync(this::loadBalance);

        // Customer accounts cache - for dashboard view
        this.customerAccountsCache = Caffeine.newBuilder()
            .maximumSize(500_000)              // 500K customers
            .expireAfterWrite(Duration.ofMinutes(1))
            .buildAsync(this::loadCustomerAccounts);
    }

    public AccountWithTransactions getAccountDetail(String accountId, int txnLimit) {
        // Single query returns static cols (balance) + transaction rows
        List<Row> rows = session.execute(
            selectAccountWithTransactions.bind(accountId, txnLimit)
                .setConsistencyLevel(ConsistencyLevel.LOCAL_ONE)
        ).all();

        if (rows.isEmpty()) {
            return null;
        }

        // Static columns are the same on every row
        Row first = rows.get(0);
        AccountBalance balance = new AccountBalance(
            first.getBigDecimal("current_balance"),
            first.getBigDecimal("available_balance"),
            first.getInstant("last_updated")
        );

        // Map transaction rows
        List<Transaction> transactions = rows.stream()
            .filter(row -> row.getString("transaction_id") != null)
            .map(this::mapToTransaction)
            .toList();

        return new AccountWithTransactions(balance, transactions);
    }

    public CompletableFuture<AccountBalance> getBalance(String accountId) {
        return balanceCache.get(accountId);
    }
}
```

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
    ParticipantBorderColor #333333
}

title Balance Check: Read Path

participant "Mobile App" as app
participant "In-Memory Cache\n(Caffeine)" as cache
database "Cassandra\n(Speed Layer)" as cass

== Cache Hit (Common Case) ==
app -> cache : getBalance(accountId)
cache --> app : Balance (< 1ms)

== Cache Miss ==
app -> cache : getBalance(accountId)
cache -> cache : miss
cache -> cass : SELECT * FROM account_balances\nWHERE account_id = ?
cass --> cache : Row
cache -> cache : populate cache
cache --> app : Balance (~2-5ms)

note over cache
Cache configuration:
- 1M accounts cached
- 30 sec TTL (balances change frequently)
- 5 sec refresh interval
- Async refresh (stale-while-revalidate)
end note
@enduml
```

### CDC-Driven Cache Invalidation

Unlike traditional write-through, the speed layer is updated via CDC from core banking. Cache invalidation is event-driven:

```java
@KafkaListener(topics = "corebanking.transactions")
public class BalanceCacheInvalidator {

    private final AccountSpeedLayer speedLayer;

    public void onTransaction(TransactionEvent event) {
        // Invalidate cached balance when transaction occurs
        speedLayer.invalidateBalance(event.getAccountId());

        // Also invalidate customer accounts cache
        // (balances shown in account list)
        speedLayer.invalidateCustomerAccounts(event.getCustomerId());
    }
}
```

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
    ParticipantBorderColor #333333
}

title CDC-Driven Cache Invalidation

participant "Core Banking" as core
queue "Kafka" as kafka
participant "CDC Consumer" as cdc
participant "In-Memory Cache" as cache
database "Cassandra" as cass

== Transaction Occurs ==
core -> kafka : TransactionEvent\n{accountId, newBalance}
kafka -> cdc : Consume event

== Update Speed Layer ==
cdc -> cass : UPDATE account_balances\nSET current_balance = ?
cdc -> cache : invalidate(accountId)
cache -> cache : remove entry

== Next Balance Check ==
note over cache
Next getBalance() will:
1. Miss cache
2. Load fresh data from Cassandra
3. Return updated balance
end note

@enduml
```

---

## Session Management

Sessions require even lower latency than user data and have unique access patterns.

### Session Schema

```sql
CREATE TABLE sessions (
    session_id TEXT,
    user_id UUID,
    created_at TIMESTAMP,
    last_accessed_at TIMESTAMP,
    expires_at TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    data MAP<TEXT, TEXT>,
    PRIMARY KEY (session_id)
) WITH default_time_to_live = 86400;  -- 24-hour default TTL

-- Sessions by user (for "logout all devices")
CREATE TABLE sessions_by_user (
    user_id UUID,
    session_id TEXT,
    created_at TIMESTAMP,
    last_accessed_at TIMESTAMP,
    device_info TEXT,
    PRIMARY KEY ((user_id), created_at, session_id)
) WITH CLUSTERING ORDER BY (created_at DESC)
  AND default_time_to_live = 86400;
```

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam state {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title Session Lifecycle

[*] --> Created : Login

state Created {
    Created : session_id generated
    Created : written to sessions + sessions_by_user
    Created : cached in memory
}

Created --> Active : First request

state Active {
    Active : last_accessed_at updated
    Active : cache entry refreshed
    Active : TTL reset on access
}

Active --> Active : Request\n(touch session)
Active --> Expired : TTL exceeded
Active --> Destroyed : Logout

state Expired {
    Expired : Cassandra TTL removes row
    Expired : Cache eviction
}

state Destroyed {
    Destroyed : Explicit DELETE
    Destroyed : Cache invalidation
}

Expired --> [*]
Destroyed --> [*]

note right of Active
On every authenticated request:
1. Check cache (< 1ms)
2. Validate not expired
3. Async touch (update last_accessed_at)
end note
@enduml
```

### Session Service

```java
public class SessionSpeedLayer {

    private final CqlSession session;
    private final Cache<String, SessionData> sessionCache;

    public SessionSpeedLayer(CqlSession session) {
        this.session = session;

        // Very aggressive caching for sessions
        this.sessionCache = Caffeine.newBuilder()
            .maximumSize(500_000)              // 500K active sessions
            .expireAfterAccess(Duration.ofMinutes(15))
            .build();
    }

    public SessionData getSession(String sessionId) {
        // Check cache first
        SessionData cached = sessionCache.getIfPresent(sessionId);
        if (cached != null) {
            if (cached.isExpired()) {
                sessionCache.invalidate(sessionId);
                return null;
            }
            return cached;
        }

        // Load from Cassandra
        Row row = session.execute(
            selectSession.bind(sessionId)
                .setConsistencyLevel(ConsistencyLevel.LOCAL_ONE)
        ).one();

        if (row == null) {
            return null;
        }

        SessionData sessionData = mapToSession(row);

        if (sessionData.isExpired()) {
            return null;
        }

        sessionCache.put(sessionId, sessionData);
        return sessionData;
    }

    public String createSession(UUID userId, SessionRequest request) {
        String sessionId = generateSessionId();
        Instant now = Instant.now();
        Instant expiresAt = now.plus(Duration.ofHours(24));

        // Write to both tables
        BatchStatement batch = BatchStatement.newInstance(BatchType.LOGGED)
            .add(insertSession.bind(
                sessionId, userId, now, now, expiresAt,
                request.getIpAddress(), request.getUserAgent(),
                new HashMap<>()
            ))
            .add(insertSessionByUser.bind(
                userId, sessionId, now, now,
                request.getDeviceInfo()
            ));

        session.execute(batch.setConsistencyLevel(ConsistencyLevel.LOCAL_QUORUM));

        SessionData sessionData = new SessionData(
            sessionId, userId, now, expiresAt, new HashMap<>());
        sessionCache.put(sessionId, sessionData);

        return sessionId;
    }

    public void touchSession(String sessionId) {
        Instant now = Instant.now();

        // Update last accessed time
        session.executeAsync(
            updateSessionAccess.bind(now, sessionId)
                .setConsistencyLevel(ConsistencyLevel.LOCAL_ONE)
        );

        // Update cache
        SessionData cached = sessionCache.getIfPresent(sessionId);
        if (cached != null) {
            cached.setLastAccessedAt(now);
        }
    }

    public void destroySession(String sessionId) {
        SessionData sessionData = getSession(sessionId);

        if (sessionData != null) {
            // Delete from both tables
            BatchStatement batch = BatchStatement.newInstance(BatchType.LOGGED)
                .add(deleteSession.bind(sessionId))
                .add(deleteSessionByUser.bind(
                    sessionData.getUserId(),
                    sessionData.getCreatedAt(),
                    sessionId
                ));

            session.execute(batch);
        }

        sessionCache.invalidate(sessionId);
    }

    public void destroyAllUserSessions(UUID userId) {
        // Get all sessions for user
        List<Row> sessions = session.execute(
            selectSessionsByUser.bind(userId)
        ).all();

        // Delete each session
        for (Row row : sessions) {
            destroySession(row.getString("session_id"));
        }
    }
}
```

---

## Real-Time Counters and Aggregates

Some speed layer data is derived: counters, aggregates, and computed values that support real-time features.

### Counter Tables

```sql
-- Real-time user statistics
CREATE TABLE user_stats (
    user_id UUID,
    stat_name TEXT,
    stat_value COUNTER,
    PRIMARY KEY ((user_id), stat_name)
);

-- Global feature counters
CREATE TABLE feature_counters (
    feature_name TEXT,
    time_bucket TEXT,           -- Hour or day bucket
    counter_value COUNTER,
    PRIMARY KEY ((feature_name, time_bucket))
);
```

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
    ParticipantBorderColor #333333
}

title Real-Time Counter Pattern

participant "Application" as app
database "user_stats\n(counter table)" as stats
database "feature_counters\n(time-bucketed)" as feat

== Fire-and-Forget Increment ==
app ->> stats : UPDATE user_stats\nSET stat_value = stat_value + 1\n(async, LOCAL_ONE)
note right: No response needed\nEventual accuracy

== Time-Bucketed Counters ==
app -> app : bucket = hour(now)
app ->> feat : UPDATE feature_counters\nSET counter_value += 1\nWHERE feature = 'login'\nAND time_bucket = '2024-01-15-14'
note right
Time buckets prevent
unbounded growth.
Enable time-series queries.
end note

== Reading Counters ==
app -> stats : SELECT * FROM user_stats\nWHERE user_id = ?
stats --> app : {logins: 42, posts: 7, ...}
@enduml
```

### Counter Service

```java
public class UserStatsService {

    public void incrementStat(UUID userId, String statName) {
        session.executeAsync(
            incrementUserStat.bind(userId, statName)
                .setConsistencyLevel(ConsistencyLevel.LOCAL_ONE)
        );
    }

    public Map<String, Long> getUserStats(UUID userId) {
        return session.execute(
            selectUserStats.bind(userId)
                .setConsistencyLevel(ConsistencyLevel.LOCAL_ONE)
        ).all().stream()
            .collect(Collectors.toMap(
                row -> row.getString("stat_name"),
                row -> row.getLong("stat_value")
            ));
    }
}
```

---

## Materialized Speed Views

Pre-compute expensive queries into speed-optimized views:

### View Schema

```sql
-- Pre-computed user dashboard data
CREATE TABLE user_dashboard (
    user_id UUID,
    last_computed_at TIMESTAMP,
    unread_notifications INT,
    pending_tasks INT,
    recent_activity_summary TEXT,
    recommended_items LIST<UUID>,
    PRIMARY KEY (user_id)
) WITH default_time_to_live = 300;  -- 5-minute TTL forces refresh
```

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
    ParticipantBorderColor #333333
}

title Materialized Speed View Refresh

participant "Scheduler\n(Background)" as sched
database "Source Tables\n(notifications,\ntasks, activity)" as source
database "Speed View\n(user_dashboard)" as view
participant "Application" as app

== Background Pre-computation (every minute) ==
sched -> sched : Get active users\n(last 15 min)
loop for each active user
    sched -> source : COUNT notifications\nCOUNT tasks\nAggregate activity
    source --> sched : Raw data
    sched -> sched : Compute aggregates
    sched -> view : INSERT dashboard\n(with 5 min TTL)
end

== Application Read (fast path) ==
app -> view : SELECT * FROM user_dashboard
alt Fresh data exists
    view --> app : Pre-computed dashboard\n(< 2ms)
else Stale or missing
    app -> source : Compute real-time\n(50-200ms)
    source --> app : Computed data
end

note over sched, view
TTL ensures stale views expire automatically.
Background job keeps active user views fresh.
Inactive users fall back to real-time computation.
end note
@enduml
```

### Background Computation

```java
@Scheduled(fixedDelay = 60000)  // Every minute
public void refreshDashboards() {
    // Get users with recent activity
    List<UUID> activeUsers = getRecentlyActiveUsers(Duration.ofMinutes(15));

    for (UUID userId : activeUsers) {
        try {
            refreshDashboard(userId);
        } catch (Exception e) {
            log.warn("Failed to refresh dashboard for {}", userId, e);
        }
    }
}

private void refreshDashboard(UUID userId) {
    // Compute expensive aggregates
    int unreadNotifications = countUnreadNotifications(userId);
    int pendingTasks = countPendingTasks(userId);
    String activitySummary = computeActivitySummary(userId);
    List<UUID> recommendations = computeRecommendations(userId);

    // Write to speed view
    session.execute(insertDashboard.bind(
        userId, Instant.now(),
        unreadNotifications, pendingTasks,
        activitySummary, recommendations
    ));
}
```

### Reading Speed Views

```java
public class DashboardService {

    public UserDashboard getDashboard(UUID userId) {
        // Try speed view first
        Row row = session.execute(
            selectDashboard.bind(userId)
                .setConsistencyLevel(ConsistencyLevel.LOCAL_ONE)
        ).one();

        if (row != null && isRecent(row.getTimestamp("last_computed_at"))) {
            return mapToDashboard(row);
        }

        // Fall back to real-time computation
        return computeDashboardRealTime(userId);
    }

    private boolean isRecent(Instant lastComputed) {
        return lastComputed != null &&
               lastComputed.isAfter(Instant.now().minus(Duration.ofMinutes(5)));
    }
}
```

---

## Consistency Considerations

Speed layer trades consistency for latency. Understanding the trade-offs is essential.

### Consistency Level Selection

| Data Type | Read CL | Write CL | Rationale |
|-----------|---------|----------|-----------|
| Session validation | LOCAL_ONE | LOCAL_QUORUM | Fast reads, durable writes |
| User profile display | LOCAL_ONE | LOCAL_QUORUM | Stale data acceptable |
| Authentication | LOCAL_QUORUM | LOCAL_QUORUM | Security-critical |
| Counters | LOCAL_ONE | LOCAL_ONE | Approximate is acceptable |
| Dashboard data | LOCAL_ONE | LOCAL_ONE | Pre-computed, non-critical |

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam rectangle {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title Consistency vs Latency Trade-offs

rectangle "Latency" as lat #transparent;line:transparent
rectangle "Consistency" as cons #transparent;line:transparent

rectangle "LOCAL_ONE\n(~1-2ms)" as l1 #C8E6C9
rectangle "LOCAL_QUORUM\n(~3-5ms)" as lq #FFF9C4
rectangle "QUORUM\n(~10-50ms)" as q #FFCDD2
rectangle "ALL\n(~50-200ms)" as all #EF9A9A

l1 -[hidden]-> lq
lq -[hidden]-> q
q -[hidden]-> all

note bottom of l1
Speed layer default
Stale reads possible
Best for: sessions, dashboards
end note

note bottom of lq
Balanced choice
Strong within DC
Best for: user updates
end note

note bottom of q
Cross-DC consistency
Higher latency
Best for: authentication
end note

note bottom of all
Full consistency
Availability trade-off
Best for: rare critical ops
end note
@enduml
```

### Stale Read Handling

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam activity {
    BackgroundColor #F5F5F5
    BorderColor #333333
    DiamondBackgroundColor #FFF9C4
}

title Stale Read Decision Flow

start
:Read from cache;

if (Cache hit?) then (yes)
    :Calculate data age;

    if (age <= maxStaleness) then (yes)
        #C8E6C9:Return cached data;
        note right: Fresh enough\n(fast path)
    elseif (age <= 2x maxStaleness) then (yes)
        #FFF9C4:Return stale data;
        :Trigger async refresh;
        note right: Stale-while-revalidate\n(background refresh)
    else (too old)
        #FFCDD2:Load fresh from DB;
        note right: Must wait for\nfresh data
    endif
else (no)
    #FFCDD2:Load fresh from DB;
endif

stop
@enduml
```

```java
public class StaleDataHandler {

    public User getUserWithStaleness(UUID userId, Duration maxStaleness) {
        // Get from cache with staleness check
        CacheEntry<User> entry = userCache.getEntry(userId);

        if (entry != null) {
            Duration age = Duration.between(entry.getLoadedAt(), Instant.now());

            if (age.compareTo(maxStaleness) <= 0) {
                return entry.getValue();
            }

            // Data too stale - refresh
            if (age.compareTo(maxStaleness.multipliedBy(2)) <= 0) {
                // Return stale data but trigger async refresh
                refreshAsync(userId);
                return entry.getValue();
            }
        }

        // Must load fresh
        return loadUser(userId);
    }
}
```

---

## Cache Invalidation Strategies

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam rectangle {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title Cache Invalidation Strategies Comparison

rectangle "Event-Driven" as event #C8E6C9 {
    rectangle "Kafka event\ntriggers invalidation" as e1
}

rectangle "TTL-Based" as ttl #FFF9C4 {
    rectangle "Time-based\nexpiration + refresh" as t1
}

rectangle "Versioned" as ver #E3F2FD {
    rectangle "Only invalidate\nolder versions" as v1
}

note bottom of event
Pros: Immediate consistency
Cons: Requires event infrastructure
Use: User updates, session changes
end note

note bottom of ttl
Pros: Simple, self-healing
Cons: Stale window possible
Use: Profile data, preferences
end note

note bottom of ver
Pros: Prevents race conditions
Cons: Version tracking overhead
Use: Concurrent update scenarios
end note
@enduml
```

### Event-Driven Invalidation

```java
@KafkaListener(topics = "user-events")
public void handleUserEvent(UserEvent event) {
    switch (event.getType()) {
        case USER_UPDATED:
            speedLayer.invalidateUser(event.getUserId());
            break;
        case USER_DELETED:
            speedLayer.invalidateUser(event.getUserId());
            speedLayer.invalidateEmail(event.getEmail());
            break;
        case PASSWORD_CHANGED:
            // Invalidate all sessions
            speedLayer.invalidateUserSessions(event.getUserId());
            break;
    }
}
```

### TTL-Based Refresh

```java
// Cache configuration with automatic refresh
Cache<UUID, User> userCache = Caffeine.newBuilder()
    .maximumSize(100_000)
    .expireAfterWrite(Duration.ofMinutes(5))
    .refreshAfterWrite(Duration.ofMinutes(1))
    .build(userId -> loadUser(userId));
```

### Versioned Invalidation

```java
public class VersionedCache {

    private final ConcurrentMap<UUID, VersionedEntry<User>> cache;

    public void put(UUID userId, User user, long version) {
        cache.compute(userId, (id, existing) -> {
            if (existing == null || existing.getVersion() < version) {
                return new VersionedEntry<>(user, version);
            }
            return existing;  // Keep newer version
        });
    }

    public void invalidateIfOlder(UUID userId, long version) {
        cache.computeIfPresent(userId, (id, existing) -> {
            if (existing.getVersion() <= version) {
                return null;  // Remove
            }
            return existing;  // Keep newer version
        });
    }
}
```

---

## Monitoring Speed Layer Performance

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `speed_layer.cache_hit_ratio` | Cache hit percentage | < 90% |
| `speed_layer.read_latency_p99` | 99th percentile read latency | > 10ms |
| `speed_layer.cache_size` | Current cache entries | Near maximum |
| `speed_layer.eviction_rate` | Cache evictions per second | Sustained high |
| `speed_layer.stale_reads` | Reads returning stale data | > 5% |

### Health Check

```java
@Component
public class SpeedLayerHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        Map<String, Object> details = new HashMap<>();

        // Check cache hit ratio
        double hitRatio = getCacheHitRatio();
        details.put("cache_hit_ratio", hitRatio);

        // Check read latency
        double p99Latency = getP99ReadLatency();
        details.put("p99_read_latency_ms", p99Latency);

        // Check Cassandra connectivity
        boolean cassandraHealthy = checkCassandraHealth();
        details.put("cassandra_healthy", cassandraHealthy);

        if (hitRatio < 0.8 || p99Latency > 50 || !cassandraHealthy) {
            return Health.down().withDetails(details).build();
        }

        return Health.up().withDetails(details).build();
    }
}
```

---

## Summary

The speed layer pattern enables mobile banking at scale by separating read-heavy workloads from transaction processing:

1. **Core banking remains system of record** - All transactions processed by mainframe for compliance, fraud detection, and settlement
2. **CDC synchronization** - Transaction events flow to Cassandra within seconds via Kafka
3. **Schema design for access patterns** - Balances (hot) separated from transactions (warm), denormalized for each query pattern
4. **Aggressive caching** - In-memory cache serves balance checks in sub-millisecond
5. **Appropriate consistency levels** - LOCAL_ONE for reads; staleness is acceptable for display
6. **TTL-based lifecycle** - Older transactions expire from speed layer, served from archival storage

This architecture allows a mainframe handling hundreds of TPS for transactions to support millions of mobile balance checks per minute through the Cassandra speed layer.

---

## Related Documentation

- [CQRS Pattern](cqrs.md) - Separating read and write models
- [Multi-Tenant Isolation](multi-tenant.md) - Per-tenant speed layers
- [Time-Series Data](time-series.md) - Hot vs cold data tiering
