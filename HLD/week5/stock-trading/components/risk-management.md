# Stock Trading: Risk Management

## Pre-Trade Risk Checks

```python
class RiskManager:
    def validate_order(self, user_id, order):
        # 1. Balance check
        if order.side == 'BUY':
            required = order.price * order.quantity
            if self.get_cash_balance(user_id) < required:
                return False, "Insufficient funds"
        else:  # SELL
            if self.get_holdings(user_id, order.symbol) < order.quantity:
                return False, "Insufficient shares"
        
        # 2. Position limit check
        if self.get_position_value(user_id) > user.position_limit:
            return False, "Position limit exceeded"
        
        # 3. Rate limiting
        if self.get_orders_last_second(user_id) > 100:
            return False, "Rate limit exceeded"
        
        return True, "OK"
```

## Post-Trade Updates

```python
def on_trade_executed(self, trade):
    # Update buyer
    buyer_cash = self.get_cash_balance(trade.buyer_id)
    buyer_holdings = self.get_holdings(trade.buyer_id, trade.symbol)
    
    self.update_balance(trade.buyer_id, buyer_cash - trade.amount)
    self.update_holdings(trade.buyer_id, trade.symbol, buyer_holdings + trade.quantity)
    
    # Update seller (opposite)
    seller_cash = self.get_cash_balance(trade.seller_id)
    seller_holdings = self.get_holdings(trade.seller_id, trade.symbol)
    
    self.update_balance(trade.seller_id, seller_cash + trade.amount)
    self.update_holdings(trade.seller_id, trade.symbol, seller_holdings - trade.quantity)
```

**Why in-memory?** Risk checks must be < 100μs. Database queries too slow. Keep balances cached in memory.
