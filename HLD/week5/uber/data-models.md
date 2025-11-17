# Uber: Data Models

## PostgreSQL (Transactional Data)

```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  phone_number VARCHAR(20) UNIQUE,
  user_type ENUM('rider', 'driver', 'both'),
  rating DECIMAL(3,2),
  created_at TIMESTAMP
);

CREATE TABLE drivers (
  driver_id UUID PRIMARY KEY REFERENCES users(user_id),
  vehicle_type ENUM('economy', 'premium', 'xl'),
  license_plate VARCHAR(20),
  status ENUM('available', 'busy', 'offline'),
  current_ride_id UUID,
  INDEX idx_status (status)
);

CREATE TABLE rides (
  ride_id UUID PRIMARY KEY,
  rider_id UUID REFERENCES users(user_id),
  driver_id UUID REFERENCES users(user_id),
  status ENUM('requested', 'matched', 'started', 'completed', 'cancelled'),
  pickup_lat DECIMAL(10,8),
  pickup_lng DECIMAL(11,8),
  dropoff_lat DECIMAL(10,8),
  dropoff_lng DECIMAL(11,8),
  estimated_fare DECIMAL(10,2),
  actual_fare DECIMAL(10,2),
  surge_multiplier DECIMAL(3,2),
  requested_at TIMESTAMP,
  completed_at TIMESTAMP,
  INDEX idx_rider (rider_id),
  INDEX idx_driver (driver_id)
);
```

## Redis (Cache & Geospatial)

```
# Driver locations (geospatial index)
GEOADD driver_locations {lng} {lat} {driver_id}

# Driver status
Key: driver:status:{driver_id}
Value: "available" | "busy" | "offline"
TTL: 60 seconds

# Active ride state
Key: ride:{ride_id}
Value: {rider_id, driver_id, status, ...}
TTL: 24 hours
```

## Cassandra (Location History)

```cql
CREATE TABLE driver_locations (
  driver_id UUID,
  timestamp TIMESTAMP,
  lat DECIMAL,
  lng DECIMAL,
  PRIMARY KEY (driver_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```
