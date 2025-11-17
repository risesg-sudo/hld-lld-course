# Stock Trading: Order Book Management

## Order Book Levels

**Level 1** (Top of Book): Best bid and ask only
**Level 2** (Market Depth): Top 10-20 price levels
**Level 3** (Full Book): Every order with IDs

## Real-Time Market Data

```python
class MarketDataPublisher:
    def on_trade_executed(self, trade):
        # Publish Level 1 update
        level1 = {
            'symbol': trade.symbol,
            'last_price': trade.price,
            'bid': order_book.best_bid(),
            'ask': order_book.best_ask(),
            'volume': order_book.total_volume()
        }
        
        self.publish_to_subscribers(level1)
    
    def on_order_book_change(self):
        # Publish Level 2 update (top 10 levels)
        level2 = {
            'symbol': self.symbol,
            'bids': order_book.get_bids(10),
            'asks': order_book.get_asks(10)
        }
        
        self.publish_to_subscribers(level2)
```

## Conflation

Reduce data volume by aggregating updates:

```python
# Instead of 1000 updates/sec, send batched update every 100ms
buffer = []
while True:
    update = await get_market_data_update()
    buffer.append(update)
    
    if time_since_last_send() > 100:  # ms
        aggregated = aggregate_updates(buffer)
        send_to_subscribers(aggregated)
        buffer.clear()
```

**Why?** Reduces bandwidth by 90%+. Retail clients don't need microsecond updates.
