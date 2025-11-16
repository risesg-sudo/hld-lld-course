# Stock Trading Platform System Design

## Table of Contents
1. [Requirements](#requirements)
2. [Capacity Estimation](#capacity-estimation)
3. [High-Level Architecture](#high-level-architecture)
4. [Component Design](#component-design)
5. [Data Models](#data-models)
6. [API Design](#api-design)
7. [Scalability](#scalability)
8. [Potential Bottlenecks](#potential-bottlenecks)

---

## Requirements

### Functional Requirements
1. **Order Placement**: Users can place buy/sell orders (market, limit, stop-loss)
2. **Order Matching**: Match buy orders with sell orders
3. **Order Book**: Maintain real-time order book for each security
4. **Trade Execution**: Execute matched orders
5. **Portfolio Management**: Track user holdings and positions
6. **Price Feeds**: Real-time price updates
7. **Market Data**: Historical prices, charts, analytics
8. **Risk Management**: Position limits, margin requirements
9. **Settlement**: Post-trade clearing and settlement
10. **Compliance**: Audit logs, regulatory reporting

### Non-Functional Requirements
1. **Ultra-Low Latency**: Order processing < 1 millisecond (μs)
2. **High Throughput**: Handle millions of orders/second
3. **Consistency**: Strong consistency (no duplicate trades)
4. **Availability**: 99.999% uptime during trading hours
5. **Fairness**: FIFO order matching (first-in-first-out)
6. **Durability**: No data loss (orders, trades)
7. **Security**: Prevent unauthorized access, market manipulation
8. **Deterministic**: Same input → same output (for audit)
9. **Scalability**: Handle market spikes (10x normal volume)

### Out of Scope (for this design)
- User authentication details
- Payment gateway integration
- Tax reporting
- Advanced order types (iceberg, algorithmic)
- Options, futures, derivatives
- Multi-asset class trading

---

## Capacity Estimation

### Assumptions
- **Active Users**: 1 million traders
- **Securities**: 10,000 stocks
- **Trading Hours**: 6.5 hours/day (9:30 AM - 4:00 PM EST)
- **Average Orders per User**: 10 orders/day
- **Peak to Average Ratio**: 10x (market open/close)
- **Order to Trade Ratio**: 5:1 (only 20% of orders execute)

### Traffic Estimates

#### Order Volume
```
Orders/day = 1M users × 10 orders = 10 million orders/day
Trading seconds = 6.5 hours × 3600 = 23,400 seconds
Average orders/sec = 10M / 23,400 ≈ 427 orders/sec

Peak (10x): 4,270 orders/sec
```

#### Trade Volume
```
Trades/day = 10M orders × 20% = 2 million trades/day
Average trades/sec = 2M / 23,400 ≈ 85 trades/sec
Peak: 850 trades/sec
```

#### Market Data Updates
```
Securities: 10,000
Update frequency: Every 100ms (10 updates/sec per security)
Price updates/sec = 10,000 × 10 = 100,000 updates/sec

Quote updates (bid/ask changes): 3x price updates = 300,000/sec
```

**Note**: High-frequency trading (HFT) firms can generate millions of orders/sec, but we'll design for 100K orders/sec peak.

### Storage Estimates

#### Orders (1 year retention)
```
Orders/day = 10M
Data per order: 200 bytes (symbol, type, price, quantity, user_id, timestamps)
Daily storage = 10M × 200 bytes = 2 GB/day
Yearly storage = 2 GB × 250 trading days = 500 GB/year

With audit logs (10x): 5 TB/year
```

#### Trades (7 years retention for compliance)
```
Trades/day = 2M
Data per trade: 300 bytes
Daily storage = 2M × 300 bytes = 600 MB/day
7-year storage = 600 MB × 250 × 7 = 1 TB

With audit logs: 10 TB
```

#### Market Data (tick data, 1 year)
```
Price updates/day = 100K/sec × 23,400 sec = 2.34 billion updates/day
Data per update: 50 bytes (symbol, price, volume, timestamp)
Daily storage = 2.34B × 50 bytes = 117 GB/day
Yearly storage = 117 GB × 250 = 29 TB
```

#### Portfolio Data
```
Users: 1M
Holdings per user: 20 stocks avg
Total positions: 20M
Data per position: 100 bytes
Total: 2 GB (negligible)
```

### Latency Requirements

**Industry Standards**:
- **Retail Trading**: < 100ms (acceptable)
- **Institutional**: < 10ms (competitive)
- **High-Frequency Trading (HFT)**: < 100 microseconds (critical)

**Our Target** (institutional):
- Order placement to acknowledgment: < 1ms
- Order matching: < 500 microseconds
- Price feed dissemination: < 1ms
- Market data update: < 100 microseconds

**Latency Budget** (1ms total):
```
Network (client to gateway): 200 μs
Gateway processing: 50 μs
Order validation: 100 μs
Matching engine: 500 μs
Trade confirmation: 100 μs
Response (gateway to client): 50 μs
Total: 1000 μs = 1ms
```

---

## High-Level Architecture

```
                          ┌─────────────────────────────────┐
                          │    Clients (Traders)            │
                          │  - Web/Mobile                   │
                          │  - FIX Protocol (institutions)  │
                          └──────────────┬──────────────────┘
                                         │
                                         │ Ultra-low latency network
                                         │
                          ┌──────────────▼──────────────────┐
                          │    Order Gateway (FIX Engine)   │
                          │  - Parse orders (FIX/JSON)      │
                          │  - Validation                   │
                          │  - Rate limiting                │
                          └──────────────┬──────────────────┘
                                         │
                                         │ Zero-copy, shared memory
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  Risk Manager   │           │ Matching Engine │           │  Market Data    │
│  - Pre-trade    │◄──────────│ (Core Component)│──────────►│  Distributor    │
│  - Position     │           │  LMAX Disruptor │           │                 │
│  - Margin       │           │  In-Memory      │           │                 │
└─────────────────┘           └────────┬────────┘           └────────┬────────┘
                                       │                             │
                                       │                             │
                              ┌────────▼────────┐                    │
                              │  Event Sourcing │                    │
                              │  (Append Log)   │                    │
                              │  - All events   │                    │
                              │  - Sequencer    │                    │
                              └────────┬────────┘                    │
                                       │                             │
                   ┌───────────────────┼─────────────────────────────┘
                   │                   │
                   ▼                   ▼
          ┌─────────────────┐  ┌─────────────────┐
          │  Persistence    │  │  Market Data DB │
          │  - PostgreSQL   │  │  - Time Series  │
          │  - Orders       │  │  - InfluxDB     │
          │  - Trades       │  │                 │
          │  - Positions    │  └─────────────────┘
          └─────────────────┘

          ┌─────────────────────────────────────────────┐
          │  Post-Trade Processing                      │
          │  - Settlement Service                       │
          │  - Clearing                                 │
          │  - Reporting (regulatory)                   │
          │  - Analytics                                │
          └─────────────────────────────────────────────┘
```

### Key Components

1. **Order Gateway**: Receives and validates orders
2. **Matching Engine**: Core component that matches orders
3. **Risk Manager**: Pre-trade and post-trade risk checks
4. **Market Data Distributor**: Broadcasts price updates
5. **Event Sourcing**: Immutable log of all events
6. **Persistence**: Durable storage for orders/trades
7. **Settlement**: Post-trade processing

---

## Component Design

### 1. Order Matching Engine (Core Component)

**The Most Critical Component** - Must be:
- Ultra-fast (microsecond latency)
- Deterministic (reproducible)
- Fair (FIFO)
- Consistent (no double execution)

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│              Matching Engine                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  LMAX Disruptor (Ring Buffer)                         │ │
│  │  - Lock-free data structure                           │ │
│  │  - Single-threaded event processing                   │ │
│  │  - Mechanical sympathy (cache-friendly)               │ │
│  └───────────────────┬───────────────────────────────────┘ │
│                      │                                      │
│                      ▼                                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Order Book (per security)                            │ │
│  │                                                        │ │
│  │  Buy Side (Bids)          Sell Side (Asks)            │ │
│  │  ┌────────────┐            ┌────────────┐             │ │
│  │  │ $100.50: 100           │ $100.55: 200│             │ │
│  │  │ $100.45: 500           │ $100.60: 300│             │ │
│  │  │ $100.40: 200           │ $100.65: 150│             │ │
│  │  └────────────┘            └────────────┘             │ │
│  │                                                        │ │
│  │  Data Structure: TreeMap (Red-Black Tree)             │ │
│  │  - O(log n) insert, delete, lookup                    │ │
│  │  - Sorted by price (descending for bids, asc asks)    │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Matching Logic                                       │ │
│  │                                                        │ │
│  │  1. Receive new order                                 │ │
│  │  2. Check opposite side of book                       │ │
│  │  3. Match if price crosses (bid ≥ ask)                │ │
│  │  4. Execute trade (FIFO)                              │ │
│  │  5. Update order book                                 │ │
│  │  6. Emit trade event                                  │ │
│  │  7. Broadcast market data update                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Order Book Data Structure**:
```java
class OrderBook {
    // Buy side: Higher prices first (priority queue)
    TreeMap<Double, Queue<Order>> bids = new TreeMap<>(Comparator.reverseOrder());

    // Sell side: Lower prices first
    TreeMap<Double, Queue<Order>> asks = new TreeMap<>();

    void addOrder(Order order) {
        if (order.side == BUY) {
            bids.computeIfAbsent(order.price, k -> new LinkedList<>()).add(order);
        } else {
            asks.computeIfAbsent(order.price, k -> new LinkedList<>()).add(order);
        }
    }

    List<Trade> matchOrder(Order incomingOrder) {
        List<Trade> trades = new ArrayList<>();

        if (incomingOrder.side == BUY) {
            // Match against asks (sell orders)
            while (!asks.isEmpty() && incomingOrder.remainingQuantity > 0) {
                Map.Entry<Double, Queue<Order>> bestAsk = asks.firstEntry();

                // Check if prices cross
                if (incomingOrder.price >= bestAsk.getKey()) {
                    Queue<Order> ordersAtPrice = bestAsk.getValue();
                    Order matchingOrder = ordersAtPrice.peek();

                    // Execute trade (FIFO)
                    int tradeQuantity = Math.min(
                        incomingOrder.remainingQuantity,
                        matchingOrder.remainingQuantity
                    );

                    Trade trade = new Trade(
                        incomingOrder.orderId,
                        matchingOrder.orderId,
                        bestAsk.getKey(),  // Price of resting order
                        tradeQuantity,
                        System.nanoTime()
                    );
                    trades.add(trade);

                    // Update quantities
                    incomingOrder.remainingQuantity -= tradeQuantity;
                    matchingOrder.remainingQuantity -= tradeQuantity;

                    // Remove fully filled order
                    if (matchingOrder.remainingQuantity == 0) {
                        ordersAtPrice.poll();
                        if (ordersAtPrice.isEmpty()) {
                            asks.pollFirstEntry();
                        }
                    }
                } else {
                    break;  // No more matches
                }
            }

            // Add remaining quantity to book
            if (incomingOrder.remainingQuantity > 0) {
                addOrder(incomingOrder);
            }
        }
        // Similar logic for SELL orders...

        return trades;
    }
}
```

**LMAX Disruptor Pattern**:
- **Problem**: Traditional queues use locks (slow)
- **Solution**: Lock-free ring buffer
- **Benefits**:
  - 6M messages/sec throughput
  - < 1 microsecond latency
  - Cache-friendly (sequential access)

```
Ring Buffer (size = 1024, power of 2):
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │...│1023│
└───┴───┴───┴───┴───┴───┴───┴───┘
  ▲                           ▲
  │                           │
Producer                  Consumer
(writes)                   (reads)

Sequence numbers prevent wrap-around collisions
```

**Single-Threaded Design**:
- **Why?** Eliminates locks, deterministic execution
- **Trade-off**: Can't use multiple cores per symbol
- **Solution**: Shard by symbol (one thread per symbol)

### 2. Risk Management Service

**Pre-Trade Checks** (before order enters matching engine):
1. **Balance Check**: User has sufficient funds/shares
2. **Position Limit**: User doesn't exceed position limits
3. **Order Size**: Order within acceptable size range
4. **Rate Limiting**: User not spamming orders
5. **Circuit Breaker**: Market-wide trading halt conditions

**Post-Trade Checks**:
1. **Margin Requirements**: Maintain margin for leveraged positions
2. **Risk Exposure**: Monitor portfolio risk
3. **Settlement**: Ensure settlement obligations can be met

**Implementation**:
```java
class RiskManager {
    // In-memory cache of user balances
    Map<String, Balance> userBalances = new ConcurrentHashMap<>();

    boolean validateOrder(Order order, User user) {
        // 1. Check balance
        if (order.side == BUY) {
            double requiredFunds = order.price * order.quantity;
            if (user.cashBalance < requiredFunds) {
                return false;  // Insufficient funds
            }
        } else {  // SELL
            if (user.holdings.get(order.symbol) < order.quantity) {
                return false;  // Insufficient shares
            }
        }

        // 2. Check position limits
        if (user.totalPositionValue() > user.positionLimit) {
            return false;
        }

        // 3. Rate limiting
        if (user.getOrdersLastSecond() > 100) {
            return false;  // Too many orders
        }

        return true;
    }

    void onTradeExecuted(Trade trade) {
        // Update balances (optimistic locking)
        // Buyer: decrease cash, increase holdings
        // Seller: increase cash, decrease holdings
    }
}
```

**Performance**:
- Risk checks must be < 100 microseconds
- In-memory data structures (no DB queries)
- Async updates to database

### 3. Market Data Distributor

**Responsibilities**:
- Broadcast price updates to all subscribers
- Throttle updates (prevent overwhelming clients)
- Support multiple protocols (WebSocket, FIX, etc.)

**Architecture**:
```
Matching Engine       Market Data Distributor        Clients
      │                        │                       │
      ├─ Trade executed────────►│                       │
      │                        ├─ Aggregate (100ms)────┤
      │                        │                       │
      │                        ├─ Broadcast────────────►│ (WebSocket)
      │                        │                       │
      │                        ├─ Broadcast────────────►│ (FIX)
      │                        │                       │
      │                        ├─ Broadcast────────────►│ (gRPC)
```

**Data Feed Types**:
1. **Level 1 (Top of Book)**: Best bid/ask only
   ```json
   {
     "symbol": "AAPL",
     "bid": 150.25,
     "ask": 150.27,
     "last_price": 150.26,
     "volume": 1000000
   }
   ```

2. **Level 2 (Depth of Book)**: Full order book (10 levels)
   ```json
   {
     "symbol": "AAPL",
     "bids": [
       {"price": 150.25, "quantity": 500},
       {"price": 150.24, "quantity": 1000},
       ...
     ],
     "asks": [
       {"price": 150.27, "quantity": 300},
       {"price": 150.28, "quantity": 800},
       ...
     ]
   }
   ```

3. **Level 3 (Full Order Book)**: Every order with IDs
   - Used by institutions
   - Highest bandwidth

**Conflation** (reducing data volume):
- Aggregate updates every 100ms (instead of every tick)
- Send only latest state (skip intermediate updates)
- Reduces bandwidth by 90%+

### 4. Event Sourcing & Sequencer

**Why Event Sourcing?**
- Auditability: Reconstruct any state
- Compliance: Regulatory requirements
- Debugging: Replay to find bugs
- Disaster Recovery: Rebuild from events

**Event Log Structure**:
```
Sequence   Event Type        Payload
────────────────────────────────────────────────────────
1000001    OrderPlaced       {order_id: "O1", symbol: "AAPL", ...}
1000002    OrderPlaced       {order_id: "O2", symbol: "AAPL", ...}
1000003    TradeExecuted     {trade_id: "T1", buyer: "O1", seller: "O2", ...}
1000004    OrderCancelled    {order_id: "O3", ...}
...
```

**Sequencer** (assigns monotonic sequence numbers):
- Ensures total ordering of events
- Single source of truth
- Replicas can replay in same order

**Implementation**:
```java
class EventSourcing {
    // Append-only log (memory-mapped file for speed)
    FileChannel eventLog;

    long sequence = 0;

    void appendEvent(Event event) {
        event.sequence = ++sequence;
        event.timestamp = System.nanoTime();

        // Serialize to bytes (Protobuf, FlatBuffers)
        byte[] bytes = serialize(event);

        // Append to log (sequential write, very fast)
        eventLog.write(ByteBuffer.wrap(bytes));

        // Fsync every 1000 events (batch)
        if (sequence % 1000 == 0) {
            eventLog.force(false);  // Flush to disk
        }
    }

    void replayEvents(long fromSequence) {
        // Read from log and rebuild state
        eventLog.position(fromSequence);
        while (eventLog.hasRemaining()) {
            Event event = deserialize(eventLog.read());
            applyEvent(event);
        }
    }
}
```

**Storage**:
- **Hot**: Last 1 day in memory-mapped file (fast replay)
- **Warm**: Last 30 days on SSD
- **Cold**: Archive to S3/Glacier

### 5. FIX Protocol Gateway

**FIX (Financial Information eXchange)** - Industry standard protocol

**Message Format**:
```
8=FIX.4.4|9=154|35=D|49=SENDER|56=TARGET|34=1|52=20240115-10:30:00|
11=ORDER123|55=AAPL|54=1|38=100|40=2|44=150.50|10=123|

Fields:
8  = FIX version (4.4)
35 = Message type (D = New Order)
11 = Client order ID
55 = Symbol (AAPL)
54 = Side (1=Buy, 2=Sell)
38 = Quantity (100)
40 = Order type (2=Limit)
44 = Price (150.50)
10 = Checksum
```

**Gateway Responsibilities**:
- Parse FIX messages
- Validate format
- Convert to internal format
- Send to matching engine
- Convert responses back to FIX

**Performance**:
- Zero-copy parsing (avoid allocations)
- Pre-allocated buffers
- Direct ByteBuffer manipulation

---

## Data Models

### 1. Orders (PostgreSQL)

```sql
CREATE TABLE orders (
  order_id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  symbol VARCHAR(10) NOT NULL,
  side ENUM('BUY', 'SELL') NOT NULL,
  order_type ENUM('MARKET', 'LIMIT', 'STOP_LOSS') NOT NULL,
  price DECIMAL(18, 4),  -- Limit price
  quantity INT NOT NULL,
  filled_quantity INT DEFAULT 0,
  remaining_quantity INT,
  status ENUM('PENDING', 'OPEN', 'PARTIALLY_FILLED', 'FILLED', 'CANCELLED') NOT NULL,
  time_in_force ENUM('DAY', 'GTC', 'IOC', 'FOK') DEFAULT 'DAY',
  created_at TIMESTAMP(6) NOT NULL,  -- Microsecond precision
  updated_at TIMESTAMP(6),
  INDEX idx_user_symbol (user_id, symbol),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);
```

### 2. Trades (PostgreSQL)

```sql
CREATE TABLE trades (
  trade_id VARCHAR(36) PRIMARY KEY,
  buy_order_id VARCHAR(36) NOT NULL,
  sell_order_id VARCHAR(36) NOT NULL,
  symbol VARCHAR(10) NOT NULL,
  price DECIMAL(18, 4) NOT NULL,
  quantity INT NOT NULL,
  executed_at TIMESTAMP(6) NOT NULL,
  buyer_user_id VARCHAR(36),
  seller_user_id VARCHAR(36),
  INDEX idx_symbol_time (symbol, executed_at),
  INDEX idx_buyer (buyer_user_id),
  INDEX idx_seller (seller_user_id)
);
```

### 3. Portfolios (PostgreSQL)

```sql
CREATE TABLE portfolios (
  user_id VARCHAR(36) NOT NULL,
  symbol VARCHAR(10) NOT NULL,
  quantity INT NOT NULL,
  average_cost DECIMAL(18, 4),  -- For P&L calculation
  updated_at TIMESTAMP(6),
  PRIMARY KEY (user_id, symbol)
);

CREATE TABLE account_balances (
  user_id VARCHAR(36) PRIMARY KEY,
  cash_balance DECIMAL(18, 2) NOT NULL,
  available_balance DECIMAL(18, 2),  -- Cash - pending orders
  margin_used DECIMAL(18, 2) DEFAULT 0,
  updated_at TIMESTAMP(6)
);
```

### 4. Market Data (InfluxDB - Time Series)

```sql
-- Trades (tick data)
CREATE TABLE market_trades (
  time TIMESTAMP,
  symbol TAG,
  price FIELD,
  volume FIELD,
  trade_id FIELD
);

-- OHLCV (Open, High, Low, Close, Volume) - 1 minute bars
CREATE TABLE ohlcv_1m (
  time TIMESTAMP,
  symbol TAG,
  open FIELD,
  high FIELD,
  low FIELD,
  close FIELD,
  volume FIELD
);
```

### 5. Event Log (Custom Format)

```
Binary Format (fixed-size records for speed):
┌────────────┬────────────┬────────────┬────────────┬────────────┐
│  Sequence  │ Timestamp  │Event Type  │  Payload   │  Checksum  │
│  8 bytes   │  8 bytes   │  2 bytes   │ 200 bytes  │  4 bytes   │
└────────────┴────────────┴────────────┴────────────┴────────────┘
Total: 222 bytes per event

Sequential writes: 1000 events = 222 KB
SSD write speed: 500 MB/sec → 2M events/sec write throughput
```

---

## API Design

### REST APIs (for retail clients)

#### 1. Place Order
```http
POST /api/v1/orders
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "symbol": "AAPL",
  "side": "BUY",
  "type": "LIMIT",
  "quantity": 100,
  "price": 150.50,
  "time_in_force": "DAY"
}

Response: 201 Created
{
  "order_id": "O123456",
  "status": "PENDING",
  "timestamp": "2024-01-15T10:30:00.123456Z"
}
```

#### 2. Get Order Status
```http
GET /api/v1/orders/{order_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "order_id": "O123456",
  "symbol": "AAPL",
  "side": "BUY",
  "type": "LIMIT",
  "quantity": 100,
  "filled_quantity": 50,
  "remaining_quantity": 50,
  "status": "PARTIALLY_FILLED",
  "average_fill_price": 150.48,
  "created_at": "2024-01-15T10:30:00.123456Z"
}
```

#### 3. Cancel Order
```http
DELETE /api/v1/orders/{order_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "order_id": "O123456",
  "status": "CANCELLED",
  "cancelled_at": "2024-01-15T10:31:00.456789Z"
}
```

#### 4. Get Portfolio
```http
GET /api/v1/portfolio
Authorization: Bearer {token}

Response: 200 OK
{
  "cash_balance": 50000.00,
  "available_balance": 45000.00,  // Cash - pending orders
  "total_value": 75000.00,
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "average_cost": 150.00,
      "current_price": 151.50,
      "market_value": 15150.00,
      "unrealized_pnl": 150.00
    }
  ]
}
```

### WebSocket APIs (for real-time updates)

#### Market Data Subscription
```javascript
const ws = new WebSocket('wss://trading.example.com/market-data');

// Subscribe to symbol
ws.send(JSON.stringify({
  type: 'subscribe',
  symbols: ['AAPL', 'GOOGL', 'MSFT'],
  level: 1  // Top of book
}));

// Receive updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  /*
  {
    "type": "quote",
    "symbol": "AAPL",
    "bid": 150.25,
    "ask": 150.27,
    "last": 150.26,
    "volume": 1000000,
    "timestamp": "2024-01-15T10:30:00.123Z"
  }
  */
};
```

#### Order Updates
```javascript
const ws = new WebSocket('wss://trading.example.com/orders');

// Authenticate
ws.send(JSON.stringify({
  type: 'auth',
  token: 'jwt_token'
}));

// Receive order updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  /*
  {
    "type": "order_update",
    "order_id": "O123456",
    "status": "FILLED",
    "filled_quantity": 100,
    "average_fill_price": 150.48
  }
  */
};
```

### FIX Protocol (for institutions)

See FIX Protocol Gateway section above.

---

## Scalability

### 1. Horizontal Scaling by Symbol

**Problem**: Single matching engine bottleneck

**Solution**: Shard by symbol
```
Matching Engine 1: AAPL, GOOGL, MSFT (tech stocks)
Matching Engine 2: JPM, BAC, GS (financials)
Matching Engine 3: XOM, CVX, COP (energy)
...

Hash(symbol) % num_engines = engine_id
```

**Benefits**:
- Each engine independent (no coordination)
- Scale by adding more engines
- Hot symbols on dedicated hardware

**Trade-off**:
- Can't optimize cross-symbol strategies
- Uneven load distribution (AAPL very active, others less)

### 2. Hardware Optimization

**Bare Metal Servers** (not cloud):
- Predictable latency (no virtualization overhead)
- CPU pinning (dedicated cores)
- NUMA awareness (memory locality)
- Kernel bypass networking (DPDK)

**Example Setup**:
```
Server: Dual Xeon 18-core @ 3.5 GHz
RAM: 256 GB DDR4 (low latency)
Network: 10 Gbps with RDMA (kernel bypass)
Storage: NVMe SSD (1M IOPS)
```

**CPU Pinning**:
```bash
# Pin matching engine to core 0
taskset -c 0 ./matching-engine

# Disable hyper-threading (more predictable)
echo off > /sys/devices/system/cpu/cpuX/online
```

### 3. Colocation

**Definition**: Place servers in same datacenter as exchange

**Benefits**:
- Lowest latency (< 1ms to exchange)
- No internet routing delays
- Direct fiber connection

**Use Case**: High-frequency trading firms

### 4. Read Scalability (Market Data)

**Problem**: Millions of clients requesting quotes

**Solution**:
- **Cache**: Redis with pub/sub
- **CDN**: CloudFlare for API responses (cached 100ms)
- **Read Replicas**: 10+ PostgreSQL replicas for historical data

```
Matching Engine → Redis Pub/Sub → 100 WebSocket Servers → 1M Clients
```

### 5. Database Scaling

**Orders/Trades (PostgreSQL)**:
- **Partitioning**: By date (1 partition per month)
  ```sql
  CREATE TABLE orders_2024_01 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
  ```
- **Archiving**: Move old data to cold storage (S3)
- **Indexing**: Careful index selection (trade-off write speed)

**Market Data (InfluxDB)**:
- **Retention Policy**: Keep 1 year of tick data
- **Downsampling**: Aggregate to OHLCV bars (reduce storage)
- **Sharding**: Shard by symbol

---

## Potential Bottlenecks

### 1. Matching Engine Throughput

**Problem**: Single-threaded engine limits throughput

**Current**: 100K orders/sec per engine
**Peak**: 1M orders/sec (flash crash, news event)

**Solutions**:
1. **Multiple Engines**: Shard by symbol (10 engines → 1M orders/sec)
2. **Batch Processing**: Process multiple orders together
3. **Hardware Upgrade**: Faster CPU, more cores
4. **Drop Orders**: Reject during extreme load (with warning)

### 2. Network Latency

**Problem**: Network round-trip adds latency

**Example**:
- Client in California
- Server in New York
- RTT: 70ms (speed of light limit)

**Solutions**:
1. **Colocation**: Client servers near exchange
2. **FIX Protocol**: More efficient than HTTP/JSON
3. **UDP**: Faster than TCP (but no reliability)
4. **Market Maker**: Place orders ahead of time

### 3. Database Write Bottleneck

**Problem**: Persisting every event to DB is slow

**Example**: 100K orders/sec → 100K DB writes/sec

**Solutions**:
1. **Async Writes**: Acknowledge order immediately, write later
2. **Batch Writes**: Write 1000 orders at once
3. **Write-Ahead Log**: Append to log (fast), update DB async
4. **In-Memory Database**: Keep recent data in memory

**Trade-off**: Risk of data loss if crash before write

### 4. Market Data Fan-out

**Problem**: Broadcasting to 1M clients is expensive

**Calculation**:
- 100K price updates/sec
- 1M clients
- Bandwidth: 100K × 1M = 100 billion messages/sec (impossible!)

**Solutions**:
1. **Conflation**: Aggregate updates (100ms window)
2. **Subscription Model**: Clients subscribe to specific symbols
3. **Multicast**: One message to many clients (UDP multicast)
4. **Rate Limiting**: Max 10 updates/sec per client

### 5. Flash Crash Scenario

**Problem**: Algorithmic trading creates feedback loop

**Example**: 2010 Flash Crash
- Dow Jones dropped 1000 points in minutes
- 1 trillion dollars in market value lost
- Recovered within 20 minutes

**Causes**:
- High-frequency trading algorithms
- Stop-loss orders triggered
- Cascading sell-off

**Protections**:
1. **Circuit Breakers**: Halt trading if 7% drop
2. **Limit Up/Down**: Max price move per time period
3. **Order Size Limits**: Prevent huge orders
4. **Kill Switch**: Emergency shutdown

### 6. Order Book Depth Bottleneck

**Problem**: Deep order books (thousands of price levels) slow

**Example**:
- Order book with 10,000 price levels
- TreeMap lookup: O(log 10,000) = 13 comparisons

**Solutions**:
1. **Price Buckets**: Round to nearest penny (less levels)
2. **Limit Depth**: Display only top 100 levels
3. **Optimized Data Structures**: Skip lists, B-trees

### 7. Settlement Bottleneck

**Problem**: T+2 settlement (trade today, settle in 2 days)

**Challenge**:
- Track unsettled trades
- Ensure delivery of securities and cash
- Handle failures (seller doesn't deliver)

**Solutions**:
1. **Netting**: Offset buy/sell (reduce transfers)
2. **Central Clearing**: Clearinghouse guarantees settlement
3. **Blockchain**: Instant settlement (future)

### 8. Regulatory Reporting

**Problem**: Must report every trade to regulators

**Example**: SEC requires trade reporting within 90 seconds

**Data Volume**: 2M trades/day × 300 bytes = 600 MB/day

**Solutions**:
1. **Async Reporting**: Queue trades, batch send
2. **Dedicated Service**: Separate from critical path
3. **Compliance Database**: Store all regulatory data

### 9. Disaster Recovery

**Problem**: Matching engine crashes → trading halts

**RTO (Recovery Time Objective)**: < 1 minute
**RPO (Recovery Point Objective)**: 0 (no data loss)

**Solutions**:
1. **Hot Standby**: Replica engine running in parallel
2. **Replay Events**: Rebuild state from event log
3. **Checkpointing**: Snapshot state every 1000 events
4. **Geographic Redundancy**: Failover to different datacenter

**Failover Procedure**:
```
1. Detect failure (heartbeat timeout)
2. Promote standby to primary
3. Redirect traffic (DNS/Load balancer)
4. Notify participants (FIX message)
5. Investigate root cause
```

### 10. Order Replay Attack

**Problem**: Attacker replays old order to manipulate market

**Example**:
- Attacker captures FIX message
- Replays same order multiple times
- Creates artificial demand

**Solutions**:
1. **Sequence Numbers**: Reject duplicate sequences
2. **Timestamps**: Reject old orders (> 1 second)
3. **Nonces**: Include random nonce in each order
4. **TLS**: Encrypt FIX messages (prevent capture)

---

## Additional Considerations

### 1. Order Types

**Market Order**: Execute immediately at best available price
- Pros: Guaranteed execution
- Cons: Price uncertainty

**Limit Order**: Execute only at specified price or better
- Pros: Price control
- Cons: May not execute

**Stop-Loss Order**: Trigger market order when price hits threshold
- Use: Limit losses on existing position

**Stop-Limit Order**: Trigger limit order when price hits threshold
- More control than stop-loss

### 2. Time-in-Force

**DAY**: Cancel at end of trading day
**GTC (Good-Till-Cancelled)**: Active until filled or cancelled
**IOC (Immediate-or-Cancel)**: Fill immediately, cancel remainder
**FOK (Fill-or-Kill)**: Fill entire order immediately or cancel

### 3. Price Improvement

**Definition**: Execute at better price than requested

**Example**:
- Buyer places limit order at $100.50
- Best ask is $100.45
- Trade executes at $100.45 (better for buyer)

**Benefit**: Improves execution quality

### 4. Dark Pools

**Definition**: Private exchanges for large institutional orders

**Benefit**: Hide large orders from public (prevent market impact)

**Trade-off**: Less transparency

### 5. Regulatory Compliance

**Requirements**:
- **MiFID II (Europe)**: Transaction reporting, best execution
- **Reg NMS (US)**: Order protection, market access
- **Dodd-Frank**: Swap reporting, clearing

**Audit Trail**:
- Every order, modification, cancellation logged
- Immutable (event sourcing)
- Queryable for 7+ years

### 6. Testing & Simulation

**Challenges**:
- Can't test in production (real money!)
- Need realistic market conditions

**Solutions**:
1. **Paper Trading**: Simulate orders without real execution
2. **Historical Replay**: Replay historical market data
3. **Chaos Engineering**: Inject failures (network delay, crashes)

---

## Summary

Stock trading platforms are among the most demanding systems:

**Key Design Decisions**:
1. **Ultra-Low Latency**: Every microsecond matters
2. **Single-Threaded Matching**: Deterministic, lock-free
3. **Event Sourcing**: Immutable audit trail
4. **Hardware Optimization**: Bare metal, CPU pinning, NUMA
5. **Synchronous Risk Checks**: Prevent invalid orders
6. **Async Persistence**: Acknowledge fast, persist later

**Scale Numbers**:
- 100K orders/sec per matching engine
- < 1ms end-to-end latency
- 100K price updates/sec
- 1M concurrent clients (market data)
- 99.999% uptime during trading hours

**Technology Stack**:
- **Matching Engine**: Java/C++ (LMAX Disruptor)
- **Database**: PostgreSQL (orders/trades), InfluxDB (market data)
- **Cache**: Redis (in-memory state)
- **Messaging**: FIX Protocol
- **Event Log**: Memory-mapped files
- **Hardware**: Bare metal, NVMe SSD, 10 Gbps RDMA

**Unique Challenges**:
- Microsecond latency requirements
- Strong consistency (no duplicate trades)
- Regulatory compliance (audit everything)
- Fairness (FIFO matching)
- Determinism (reproducible for audits)

This design showcases building a mission-critical, ultra-low-latency financial system!
