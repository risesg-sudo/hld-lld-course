# Uber: Surge Pricing

## Dynamic Pricing Formula

```python
def calculate_fare(distance_km, duration_min, surge_multiplier):
    base_rate = 2.00
    per_km_rate = 1.50
    per_min_rate = 0.30
    
    base_fare = base_rate + (distance_km * per_km_rate) + (duration_min * per_min_rate)
    final_fare = base_fare * surge_multiplier
    
    return round(final_fare, 2)
```

## Surge Calculation

```python
def calculate_surge(area_id):
    # Get supply/demand ratio
    active_rides = count_active_rides(area_id)
    available_drivers = count_available_drivers(area_id)
    pending_requests = count_pending_requests(area_id)
    
    demand = active_rides + pending_requests
    supply = available_drivers + active_rides
    
    ratio = demand / supply
    
    # Map ratio to surge multiplier
    if ratio < 1.0:
        return 1.0  # No surge
    elif ratio < 1.5:
        return 1.25
    elif ratio < 2.0:
        return 1.5
    else:
        return min(2.0, ratio)  # Cap at 2x
```

**Why surge pricing?** Balances supply and demand. High surge attracts more drivers to high-demand areas.
