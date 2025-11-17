# Stock Trading: High-Level Architecture

## Core Component: Matching Engine

```
Client → FIX Gateway → Risk Manager → Matching Engine → Event Log → Database
                                            │
                                            ▼
                                     Market Data Feed
```

## Matching Engine Design

**Single-threaded by design**:
Why? Eliminates locks (too slow), provides deterministic execution, simplifies reasoning.

Trade-off: Can't use multiple cores per symbol. Solution: Shard by symbol (one engine per symbol or group).

**LMAX Disruptor Pattern**:
Lock-free ring buffer provides 6M messages/sec throughput with < 1μs latency.

**Order Book Data Structure**:
```java
TreeMap<Double, Queue<Order>> bids;  // Buy side: highest price first
TreeMap<Double, Queue<Order>> asks;  // Sell side: lowest price first
```

O(log n) insert/delete, sorted iteration for matching.

## Order Flow

1. **FIX Gateway**: Parse FIX protocol messages, validate format
2. **Risk Manager**: Pre-trade checks (balance, position limits)
3. **Matching Engine**: Match orders, execute trades
4. **Event Sourcing**: Append all events to immutable log
5. **Database**: Persist orders and trades (async)
6. **Market Data**: Broadcast price updates to subscribers

## Event Sourcing

All events logged to append-only file:
```
Sequence | Event Type     | Payload
1000001  | OrderPlaced    | {order_id, symbol, price, qty, ...}
1000002  | TradeExecuted  | {trade_id, buy_order, sell_order, price, qty}
1000003  | OrderCancelled | {order_id}
```

**Why?** Complete audit trail, ability to replay for debugging, disaster recovery.

## Hardware Optimization

**Bare Metal** (not cloud): Predictable latency, no virtualization overhead

**CPU Pinning**: Dedicate cores to matching engine, prevent context switching

**Kernel Bypass (DPDK)**: Network packets bypass kernel, reducing latency by 100μs

**NUMA Awareness**: Keep data on same CPU socket as processing thread

## Key Design Decisions

**Single-threaded matching**: Eliminates locks, provides determinism

**Event sourcing**: Provides audit trail and replay capability

**Sync risk checks**: Must validate before accepting order (prevent invalid trades)

**Async persistence**: Acknowledge fast, persist later (event log provides durability)

**Horizontal scaling**: Multiple matching engines (sharded by symbol)
