# Uber: Location Tracking

## Redis Geospatial

**Data structure**:
```redis
GEOADD driver_locations {lng} {lat} {driver_id}

# Query nearby drivers
GEORADIUS driver_locations {lng} {lat} 5 km WITHDIST
```

**Why Redis?** Sub-millisecond queries, built-in geospatial commands, auto-expiry via TTL.

## Location Update Flow

```python
async def update_driver_location(driver_id, lat, lng):
    # 1. Update Redis geospatial index
    await redis.geoadd('driver_locations', lng, lat, driver_id)
    await redis.expire('driver_locations', 60)  # Auto-expire stale
    
    # 2. Update driver status
    await redis.hset(f'driver:{driver_id}', {
        'lat': lat,
        'lng': lng,
        'updated_at': now()
    })
    
    # 3. Publish to Kafka for history
    await kafka.send('location.updates', {
        'driver_id': driver_id,
        'lat': lat,
        'lng': lng,
        'timestamp': now()
    })
    
    # 4. If in active ride, notify rider
    if await is_in_ride(driver_id):
        rider_id = await get_current_rider(driver_id)
        await websocket_send(rider_id, {
            'type': 'driver_location',
            'lat': lat,
            'lng': lng
        })
```

## Geospatial Query

```python
async def find_nearby_drivers(lat, lng, radius_km=5):
    # Query Redis for drivers within radius
    drivers = await redis.georadius(
        'driver_locations',
        longitude=lng,
        latitude=lat,
        radius=radius_km,
        unit='km',
        withdist=True,
        withcoord=True
    )
    
    # Filter by availability
    available_drivers = []
    for driver_id, distance, coords in drivers:
        status = await redis.get(f'driver:{driver_id}:status')
        if status == 'available':
            available_drivers.append({
                'driver_id': driver_id,
                'distance_km': distance,
                'location': coords
            })
    
    return sorted(available_drivers, key=lambda x: x['distance_km'])[:10]
```

## Alternative: QuadTree

For very dense areas:
```python
class QuadTree:
    # Divide space into quadrants recursively
    # Each leaf contains drivers in that region
    # Query: O(log n) instead of O(n)
    pass
```

**Trade-off**: QuadTree is faster for very dense regions but more complex to implement than Redis Geospatial.
