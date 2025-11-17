# Uber: ETA Calculation

## Hybrid Approach

**Google Maps API**: Real-time traffic data (expensive, rate limited)
**ML Model**: Historical trip data (cheap, fast)

```python
async def calculate_eta(driver_location, pickup_location):
    # 1. Try ML model first (fast, cheap)
    ml_eta = await ml_model.predict_eta(
        origin=driver_location,
        destination=pickup_location,
        time_of_day=current_hour(),
        day_of_week=current_day()
    )
    
    # 2. If high confidence, return ML ETA
    if ml_eta['confidence'] > 0.8:
        return ml_eta['eta_minutes']
    
    # 3. Fallback to Google Maps for low confidence
    maps_eta = await google_maps.get_duration(
        origin=driver_location,
        destination=pickup_location,
        traffic_model='best_guess'
    )
    
    return maps_eta['duration_minutes']
```

**Why hybrid?** ML model handles 80% of cases (cheap). Google Maps handles edge cases (accurate).
