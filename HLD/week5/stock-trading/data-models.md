# Stock Trading: Data Models

## PostgreSQL

```sql
CREATE TABLE orders (
  order_id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36),
  symbol VARCHAR(10),
  side ENUM('BUY', 'SELL'),
  order_type ENUM('MARKET', 'LIMIT', 'STOP_LOSS'),
  price DECIMAL(18,4),
  quantity INT,
  filled_quantity INT DEFAULT 0,
  status ENUM('PENDING', 'OPEN', 'FILLED', 'CANCELLED'),
  created_at TIMESTAMP(6),
  INDEX idx_user (user_id),
  INDEX idx_symbol (symbol)
);

CREATE TABLE trades (
  trade_id VARCHAR(36) PRIMARY KEY,
  buy_order_id VARCHAR(36),
  sell_order_id VARCHAR(36),
  symbol VARCHAR(10),
  price DECIMAL(18,4),
  quantity INT,
  executed_at TIMESTAMP(6),
  INDEX idx_symbol_time (symbol, executed_at)
);

CREATE TABLE portfolios (
  user_id VARCHAR(36),
  symbol VARCHAR(10),
  quantity INT,
  average_cost DECIMAL(18,4),
  PRIMARY KEY (user_id, symbol)
);
```

## InfluxDB (Time Series)

```
-- Market tick data
measurement: trades
tags: symbol
fields: price, volume, trade_id
time: nanosecond precision

-- OHLCV bars
measurement: ohlcv_1m
tags: symbol
fields: open, high, low, close, volume
time: 1-minute buckets
```

## Event Log (Custom Binary Format)

```
Fixed-size records for speed:
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Sequence │Timestamp │EventType │ Payload  │ Checksum │
│ 8 bytes  │ 8 bytes  │ 2 bytes  │200 bytes │ 4 bytes  │
└──────────┴──────────┴──────────┴──────────┴──────────┘
Total: 222 bytes/event

Sequential writes: 500 MB/sec on SSD = 2M events/sec
```
