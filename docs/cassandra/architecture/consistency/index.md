# Consistency

For detailed information about consistency in Cassandra, see [Distributed Data - Consistency](../distributed-data/consistency.md).

## Overview

Cassandra provides tunable consistency, allowing applications to choose the trade-off between consistency, availability, and performance on a per-operation basis.

## Key Concepts

- **Consistency Levels** - Configure how many replicas must respond
- **Read Repair** - Automatic consistency repair during reads
- **Hinted Handoff** - Temporary storage for unavailable replicas
- **Anti-Entropy Repair** - Background consistency verification

## Related Documentation

- [Distributed Data - Consistency](../distributed-data/consistency.md) - Detailed consistency documentation
- [Replication](../distributed-data/replication.md) - How replication affects consistency
