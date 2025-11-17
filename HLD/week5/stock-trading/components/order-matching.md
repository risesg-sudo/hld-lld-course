# Stock Trading: Order Matching Engine

## Order Book Structure

```java
class OrderBook {
    // Buy orders: Higher prices first (max heap behavior)
    TreeMap<Double, LinkedList<Order>> bids = new TreeMap<>(Comparator.reverseOrder());
    
    // Sell orders: Lower prices first (min heap behavior)
    TreeMap<Double, LinkedList<Order>> asks = new TreeMap<>();
    
    List<Trade> matchOrder(Order incoming) {
        if (incoming.side == BUY) {
            return matchBuyOrder(incoming);
        } else {
            return matchSellOrder(incoming);
        }
    }
    
    List<Trade> matchBuyOrder(Order buyOrder) {
        List<Trade> trades = new ArrayList<>();
        
        while (!asks.isEmpty() && buyOrder.remainingQty > 0) {
            Map.Entry<Double, LinkedList<Order>> bestAsk = asks.firstEntry();
            
            // Price crossing check
            if (buyOrder.price >= bestAsk.getKey()) {
                LinkedList<Order> ordersAtPrice = bestAsk.getValue();
                Order sellOrder = ordersAtPrice.peek();
                
                // Execute trade (FIFO at price level)
                int tradeQty = Math.min(buyOrder.remainingQty, sellOrder.remainingQty);
                
                trades.add(new Trade(
                    buyOrder.orderId,
                    sellOrder.orderId,
                    bestAsk.getKey(),  // Price of resting order
                    tradeQty,
                    System.nanoTime()
                ));
                
                buyOrder.remainingQty -= tradeQty;
                sellOrder.remainingQty -= tradeQty;
                
                if (sellOrder.remainingQty == 0) {
                    ordersAtPrice.poll();
                    if (ordersAtPrice.isEmpty()) {
                        asks.pollFirstEntry();
                    }
                }
            } else {
                break;
            }
        }
        
        // Add remaining to book
        if (buyOrder.remainingQty > 0) {
            bids.computeIfAbsent(buyOrder.price, k -> new LinkedList<>()).add(buyOrder);
        }
        
        return trades;
    }
}
```

## Why This Design

**TreeMap for price levels**: O(log n) access to best bid/ask, sorted iteration.

**LinkedList at each price**: FIFO ordering (regulatory requirement).

**Immediate execution**: Process each order completely before next (deterministic).

**Price-time priority**: Best price executes first. At same price, earliest order executes first (FIFO).
