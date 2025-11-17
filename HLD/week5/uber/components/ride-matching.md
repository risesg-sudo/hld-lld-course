# Uber: Ride Matching

## Matching Algorithm

```python
async def match_driver(rider_id, pickup_location, ride_type):
    # 1. Find nearby available drivers
    nearby_drivers = await location_service.find_nearby(
        lat=pickup_location['lat'],
        lng=pickup_location['lng'],
        radius_km=5,
        vehicle_type=ride_type
    )
    
    # 2. Rank by distance and rating
    ranked_drivers = sorted(nearby_drivers, key=lambda d: (
        d['distance_km'],  # Primary: closest first
        -d['rating']       # Secondary: higher rating breaks ties
    ))
    
    # 3. Send request to top 3 drivers (parallel)
    for driver in ranked_drivers[:3]:
        await send_ride_request(driver['id'], ride_details, timeout=10)
    
    # 4. First to accept wins
    accepted_driver = await wait_for_acceptance(timeout=30)
    
    if accepted_driver:
        # Atomic driver status update (prevent double-booking)
        success = await claim_driver(accepted_driver['id'], rider_id)
        if success:
            return create_ride(rider_id, accepted_driver['id'])
        else:
            # Driver claimed by another rider, retry
            return match_driver(rider_id, pickup_location, ride_type)
    else:
        # No acceptance, expand radius and retry
        return match_driver(rider_id, pickup_location, radius_km=10)
```

## Preventing Double-Booking

**Atomic compare-and-swap**:
```python
async def claim_driver(driver_id, rider_id):
    # Atomic update: only succeed if driver is available
    result = await postgres.execute("""
        UPDATE drivers
        SET status = 'busy', current_ride_id = ?
        WHERE driver_id = ? AND status = 'available'
        RETURNING driver_id
    """, (ride_id, driver_id))
    
    return result.rowcount == 1  # True if claimed, False if already busy
```

**Why SQL?** ACID transactions guarantee atomicity. NoSQL eventual consistency could cause double-booking.
