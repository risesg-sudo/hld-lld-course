# Uber System Design

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
1. **Rider Requests Ride**: User requests a ride from location A to B
2. **Driver Matching**: System matches nearby available drivers
3. **Real-time Location Tracking**: Track driver and rider locations in real-time
4. **ETA Calculation**: Estimate arrival time and trip duration
5. **Pricing**: Calculate ride price based on distance, time, surge
6. **Payment Processing**: Handle payment at trip completion
7. **Ride History**: Store trip history for riders and drivers
8. **Ratings**: Users rate drivers and vice versa
9. **Notifications**: Push notifications for ride updates
10. **Multiple Ride Types**: UberX, UberXL, UberBlack, etc.

### Non-Functional Requirements
1. **Scalability**: Support millions of rides per day globally
2. **Low Latency**: Match drivers in < 2 seconds
3. **High Availability**: 99.99% uptime (critical service)
4. **Accuracy**: Precise location tracking and ETA
5. **Consistency**: Ensure no double-booking of drivers
6. **Real-time**: Location updates every 3-5 seconds
7. **Fault Tolerance**: Handle failures gracefully
8. **Security**: Secure payment and user data
9. **Global**: Support 10,000+ cities worldwide

### Out of Scope (for this design)
- UberEats (food delivery)
- Fraud detection details
- Driver onboarding/background checks
- Marketing and promotions
- Customer support system

---

## Capacity Estimation

### Assumptions
- **Total Drivers**: 5 million globally
- **Total Riders**: 100 million
- **Daily Active Drivers**: 1 million (20% of total)
- **Daily Active Riders**: 20 million (20% of total)
- **Rides per day**: 15 million
- **Average ride duration**: 20 minutes
- **Concurrent rides**: Variable by time/city
- **Location update frequency**: Every 4 seconds

### Traffic Estimates

#### Ride Requests
```
Ride requests/day = 15 million
Requests per second (avg) = 15M / 86,400 ≈ 174 requests/sec
Peak (rush hour, 3x avg) = 522 requests/sec
```

#### Location Updates

**Driver Location Updates**:
```
Active drivers: 1 million
Update frequency: 4 seconds
Updates/second = 1M / 4 = 250,000 updates/sec

During ride (more frequent, every 3 seconds):
Active rides (avg): 15M rides/day × 20 min / 1440 min = ~208,000 concurrent rides
Updates/second = 208K / 3 ≈ 70,000 updates/sec

Total driver updates/sec = 250K + 70K = 320,000 updates/sec
```

**Rider Location Updates** (during ride):
```
Concurrent riders: 208,000
Update frequency: 5 seconds (less frequent than drivers)
Updates/second = 208K / 5 ≈ 42,000 updates/sec
```

**Total location updates/sec** = 320K + 42K = **362,000 updates/sec**

#### Read Requests

**Driver Looking for Rides**:
```
Available drivers polling: 1M
Poll frequency: Every 10 seconds
Requests/second = 1M / 10 = 100,000 req/sec
```

**Rider Tracking Driver**:
```
Active riders: 208,000
Poll frequency: Every 3 seconds (real-time tracking)
Requests/second = 208K / 3 ≈ 70,000 req/sec
```

**Total read requests** = 100K + 70K = **170,000 req/sec**

### Storage Estimates

#### Location Data (30 days retention)
```
Location updates/day = 362K/sec × 86,400 sec = 31.3 billion updates/day
Data per update: 50 bytes (lat, lng, timestamp, user_id, accuracy)
Daily storage = 31.3B × 50 bytes = 1.56 TB/day
Monthly storage = 1.56 TB × 30 = 46.8 TB/month

With replication (3x): 140 TB
```

#### Ride Data (5 years retention)
```
Rides/day = 15 million
Data per ride: 1 KB (route, fare, times, IDs)
Daily storage = 15M × 1 KB = 15 GB/day
Yearly storage = 15 GB × 365 = 5.5 TB/year
5-year storage = 27.5 TB

With replication (3x): 82.5 TB
```

#### User Data
```
Drivers: 5M × 5 KB = 25 GB
Riders: 100M × 2 KB = 200 GB
Total: 225 GB (negligible)
```

### Bandwidth Estimates

#### Incoming (Writes)
```
Location updates: 362K/sec × 50 bytes = 18.1 MB/sec
Ride requests: 174/sec × 500 bytes = 87 KB/sec
Total incoming: ~18.2 MB/sec = 145 Mbps
```

#### Outgoing (Reads)
```
Location queries: 170K/sec × 500 bytes = 85 MB/sec
Driver matching responses: 174/sec × 10 KB (list of drivers) = 1.74 MB/sec
Total outgoing: ~87 MB/sec = 696 Mbps
```

### Memory/Cache Estimates
```
Active driver locations: 1M × 100 bytes = 100 MB
Active rider locations: 208K × 100 bytes = 21 MB
Driver availability status: 1M × 50 bytes = 50 MB
Geospatial index (QuadTree): ~500 MB (estimated)
Ride state (active rides): 208K × 500 bytes = 104 MB

Total cache: ~1 GB per region (distributed globally)
Global cache: 100 regions × 1 GB = 100 GB
```

---

## High-Level Architecture

```
                                    ┌────────────────────┐
                                    │   Load Balancer    │
                                    │   (API Gateway)    │
                                    └─────────┬──────────┘
                                              │
                         ┌────────────────────┼────────────────────┐
                         │                    │                    │
                         ▼                    ▼                    ▼
                ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
                │  Ride Service   │  │ Location Service│  │ Payment Service │
                │  (Request/Match)│  │ (Track/Update)  │  │                 │
                └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                         │                    │                    │
                         │                    │                    │
                         ▼                    ▼                    ▼
                ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
                │ Matching Engine │  │  Redis Cluster  │  │   Stripe/Braint │
                │  (Geo + Algo)   │  │ (Geospatial)    │  │                 │
                └────────┬────────┘  └────────┬────────┘  └─────────────────┘
                         │                    │
                         │                    │
                         ▼                    ▼
                ┌─────────────────────────────────────────┐
                │           Kafka (Event Stream)          │
                │  - LocationUpdates                      │
                │  - RideRequests                         │
                │  - RideStatusChanges                    │
                └─────────┬───────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
  ┌────────────────┐ ┌────────────┐ ┌──────────────┐
  │   PostgreSQL   │ │  Cassandra │ │   S3/GCS     │
  │  (Users/Rides) │ │ (Locations)│ │  (Receipts)  │
  └────────────────┘ └────────────┘ └──────────────┘


  ┌────────────────────────────────────────────────────────┐
  │         Additional Services                            │
  ├────────────────────────────────────────────────────────┤
  │  - Notification Service (Push/SMS)                     │
  │  - Pricing Service (Surge calculation)                 │
  │  - ETA Service (Route calculation)                     │
  │  - Maps Service (Google Maps API)                      │
  │  - Analytics (BigQuery/Redshift)                       │
  └────────────────────────────────────────────────────────┘


  ┌────────────────────────────────────────────────────────┐
  │         WebSocket Servers                              │
  │  (Real-time updates to riders/drivers)                 │
  └────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Location Service

**Responsibilities**:
- Receive location updates from drivers and riders
- Store locations in geospatial index
- Query nearby drivers
- Real-time location streaming

**Architecture**:
```
┌──────────────────────────────────────────────────────────┐
│              Location Service                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Location Ingestion API                            │ │
│  │  - POST /location/update                           │ │
│  │  - Validate coordinates                            │ │
│  │  - Rate limiting (prevent spam)                    │ │
│  └────────────┬───────────────────────────────────────┘ │
│               │                                          │
│               ▼                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Kafka Producer                                    │ │
│  │  - Publish to LocationUpdates topic                │ │
│  │  - Async (low latency)                             │ │
│  └────────────┬───────────────────────────────────────┘ │
│               │                                          │
│               ▼                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Redis Geospatial (GEORADIUS)                      │ │
│  │  - Key: driver_locations                           │ │
│  │  - GEOADD driver_locations {lng} {lat} {driver_id} │ │
│  │  - TTL: 60 seconds (auto-expire stale locations)   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Nearby Drivers Query API                          │ │
│  │  - GET /drivers/nearby?lat=X&lng=Y&radius=5km      │ │
│  │  - GEORADIUS query                                 │ │
│  │  - Filter by availability, vehicle type            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘

Background Workers:
  - Kafka Consumer → Store in Cassandra (historical data)
  - Cleanup stale locations (Redis expiry)
```

**Redis Geospatial**:
```redis
# Add driver location
GEOADD driver_locations -122.4194 37.7749 driver_123

# Find drivers within 5km
GEORADIUS driver_locations -122.4194 37.7749 5 km WITHDIST

# Result:
# 1) "driver_123"
#    "0.5 km"
# 2) "driver_456"
#    "2.3 km"
```

**Alternative: QuadTree/S2 Cells**:
- Divide world into cells
- Each cell contains list of drivers
- Efficient for dense areas (cities)

```
QuadTree Example:
Level 0: Entire world (1 cell)
Level 1: 4 quadrants
Level 2: 16 quadrants
...
Level 12: City block-level (~1 km²)

Cell ID: geohash or S2 cell
Lookup: O(log n) instead of O(n)
```

### 2. Ride Matching Service

**Responsibilities**:
- Receive ride requests
- Find nearby available drivers
- Match rider with best driver
- Handle ride lifecycle (requested → matched → started → completed)

**Matching Algorithm**:
```python
def match_driver(rider_location, ride_type, preferences):
    # 1. Find nearby drivers
    nearby_drivers = location_service.get_nearby_drivers(
        lat=rider_location.lat,
        lng=rider_location.lng,
        radius=5_km,
        vehicle_type=ride_type  # UberX, UberXL, etc.
    )

    # 2. Filter available drivers
    available_drivers = [
        d for d in nearby_drivers
        if d.status == 'available' and d.vehicle_type == ride_type
    ]

    # 3. Rank drivers
    ranked_drivers = rank_drivers(
        drivers=available_drivers,
        rider_location=rider_location,
        preferences=preferences
    )

    # 4. Send ride request to top 3 drivers (parallel)
    for driver in ranked_drivers[:3]:
        send_ride_request(driver, ride_details, timeout=10_seconds)

    # 5. First to accept wins
    accepted_driver = wait_for_acceptance(timeout=30_seconds)

    if accepted_driver:
        return create_ride(rider, accepted_driver)
    else:
        # Expand search radius and retry
        return match_driver(rider_location, ride_type, radius=10_km)
```

**Ranking Factors**:
1. **Distance**: Closest drivers ranked higher (primary)
2. **Driver Rating**: Higher-rated drivers preferred
3. **Acceptance Rate**: Drivers who accept more often
4. **ETA**: Estimated time to pick up rider
5. **Driver Preferences**: Language, accessibility, etc.

**Matching Flow**:
```
Rider                Matching Service           Driver
  │                        │                      │
  ├─1. Request ride────────►│                      │
  │                        ├─2. Find nearby───────►│
  │                        │   (geospatial query) │
  │                        │                      │
  │                        ├─3. Send request──────►│
  │                        │   (top 3 drivers)    │
  │                        │                      │
  │                        │◄─4. Accept───────────┤
  │                        │                      │
  │◄─5. Driver matched─────┤                      │
  │                        ├─6. Reject others─────►│
  │                        │                      │
  ├─7. Track driver────────►│                      │
  │   (WebSocket)          │                      │
```

**Concurrency Handling**:
- **Problem**: Two riders request same driver simultaneously
- **Solution**: Atomic compare-and-swap (CAS) on driver status
  ```sql
  UPDATE drivers
  SET status = 'busy', current_ride_id = 'ride_123'
  WHERE driver_id = 'driver_456' AND status = 'available';

  -- If affected_rows = 0, driver already taken
  ```

### 3. ETA Calculation Service

**Responsibilities**:
- Calculate estimated time of arrival
- Estimate trip duration
- Suggest optimal routes

**Data Sources**:
- Google Maps Distance Matrix API
- Historical trip data (ML model)
- Real-time traffic data

**Calculation**:
```python
def calculate_eta(driver_location, pickup_location, dropoff_location):
    # 1. Driver to pickup ETA
    pickup_eta = maps_api.get_duration(
        origin=driver_location,
        destination=pickup_location,
        mode='driving',
        traffic_model='best_guess'
    )

    # 2. Trip duration estimate
    trip_duration = ml_model.predict(
        pickup=pickup_location,
        dropoff=dropoff_location,
        time_of_day=current_time(),
        day_of_week=current_day(),
        historical_data=query_historical_trips()
    )

    return {
        'pickup_eta_minutes': pickup_eta,
        'trip_duration_minutes': trip_duration,
        'total_time_minutes': pickup_eta + trip_duration
    }
```

**ML Model**:
- Features: Distance, time of day, day of week, weather, events
- Algorithm: Gradient Boosting (XGBoost)
- Training data: Millions of historical trips
- Accuracy: ±10% of actual time

**Real-time Updates**:
- Recalculate ETA every 30 seconds during trip
- Notify rider of significant changes (>5 min delay)

### 4. Pricing Service (Surge Pricing)

**Responsibilities**:
- Calculate base fare
- Apply surge multiplier
- Handle promotions and discounts

**Base Fare Formula**:
```
base_fare = base_rate + (distance_km × per_km_rate) + (duration_min × per_min_rate)

Example:
base_rate = $2.00
per_km_rate = $1.50/km
per_min_rate = $0.30/min

10 km trip, 20 min duration:
base_fare = $2.00 + (10 × $1.50) + (20 × $0.30) = $23.00
```

**Surge Pricing**:
- **Supply/Demand**: More riders than drivers → surge
- **Calculation**:
  ```python
  def calculate_surge(area_id, time):
      active_rides = get_active_rides(area_id)
      available_drivers = get_available_drivers(area_id)
      pending_requests = get_pending_requests(area_id)

      demand = active_rides + pending_requests
      supply = available_drivers + active_rides

      ratio = demand / supply

      if ratio < 1.0:
          surge_multiplier = 1.0  # No surge
      elif ratio < 1.5:
          surge_multiplier = 1.25
      elif ratio < 2.0:
          surge_multiplier = 1.5
      else:
          surge_multiplier = min(2.0, ratio)  # Cap at 2x

      return surge_multiplier
  ```

**Geohashing for Surge Areas**:
- Divide city into hexagonal grids (H3)
- Calculate surge per grid
- Smooth transitions between grids

```
City divided into hexagons:
┌─────┬─────┬─────┐
│ 1.0x│ 1.5x│ 1.2x│
├─────┼─────┼─────┤
│ 1.0x│ 2.0x│ 1.5x│  ← High demand area
├─────┼─────┼─────┤
│ 1.0x│ 1.0x│ 1.0x│
└─────┴─────┴─────┘
```

### 5. Payment Service

**Responsibilities**:
- Process payments at trip end
- Handle refunds and disputes
- Support multiple payment methods

**Payment Flow**:
```
Ride Completed        Payment Service         Stripe API       Database
      │                      │                     │               │
      ├─1. Trip ended────────►│                     │               │
      │                      ├─2. Calculate fare────┤               │
      │                      │   (pricing service)  │               │
      │                      │                     │               │
      │                      ├─3. Charge card───────►│               │
      │                      │                     │               │
      │                      │◄─4. Success──────────┤               │
      │                      │                     │               │
      │                      ├─5. Update ride───────┼──────────────►│
      │                      │   status: 'paid'    │               │
      │                      │                     │               │
      │◄─6. Receipt sent─────┤                     │               │
      │   (email + in-app)   │                     │               │
```

**Retry Logic**:
- Payment failure → retry 3 times with exponential backoff
- Still fails → mark as pending, retry later
- Persistent failure → notify user, request alternate payment

**Idempotency**:
- Use idempotency key to prevent duplicate charges
- Key: `ride_id + attempt_number`
- Stripe deduplicates requests with same key

### 6. Notification Service

**Responsibilities**:
- Push notifications (mobile)
- SMS notifications
- In-app notifications

**Notification Types**:
- Driver matched
- Driver arriving (2 min ETA)
- Driver arrived
- Trip started
- Trip completed
- Payment receipt

**Architecture**:
```
Trigger Event         Notification Service      Push Provider
      │                      │                     │
      ├─1. Event (Kafka)─────►│                     │
      │   (driver matched)   │                     │
      │                      ├─2. Lookup device────┤
      │                      │   tokens (Redis)    │
      │                      │                     │
      │                      ├─3. Send push────────►│
      │                      │   (FCM/APNS)        │
      │                      │                     │
      │                      │◄─4. Delivery status─┤
```

**Providers**:
- **iOS**: Apple Push Notification Service (APNS)
- **Android**: Firebase Cloud Messaging (FCM)
- **SMS**: Twilio

---

## Data Models

### 1. User Service (PostgreSQL)

```sql
-- Users table (riders and drivers)
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  user_type ENUM('rider', 'driver', 'both'),
  created_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_phone (phone_number)
);

-- Driver profiles
CREATE TABLE drivers (
  driver_id UUID PRIMARY KEY REFERENCES users(user_id),
  vehicle_type ENUM('economy', 'premium', 'xl', 'black'),
  license_number VARCHAR(50),
  vehicle_make VARCHAR(50),
  vehicle_model VARCHAR(50),
  vehicle_year INT,
  license_plate VARCHAR(20),
  rating DECIMAL(3, 2) DEFAULT 5.00,
  total_rides INT DEFAULT 0,
  status ENUM('available', 'busy', 'offline') DEFAULT 'offline',
  current_location POINT,  -- PostGIS
  last_location_update TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_location USING GIST (current_location)
);

-- Rider profiles
CREATE TABLE riders (
  rider_id UUID PRIMARY KEY REFERENCES users(user_id),
  rating DECIMAL(3, 2) DEFAULT 5.00,
  total_rides INT DEFAULT 0,
  default_payment_method_id UUID
);

-- Payment methods
CREATE TABLE payment_methods (
  payment_method_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id),
  type ENUM('credit_card', 'debit_card', 'paypal', 'cash'),
  stripe_payment_method_id VARCHAR(255),
  last_four_digits VARCHAR(4),
  is_default BOOLEAN DEFAULT FALSE,
  INDEX idx_user (user_id)
);
```

### 2. Ride Service (PostgreSQL)

```sql
-- Rides table
CREATE TABLE rides (
  ride_id UUID PRIMARY KEY,
  rider_id UUID REFERENCES users(user_id),
  driver_id UUID REFERENCES users(user_id),
  status ENUM('requested', 'matched', 'arrived', 'started', 'completed', 'cancelled'),
  ride_type ENUM('economy', 'premium', 'xl', 'black'),

  -- Locations
  pickup_lat DECIMAL(10, 8),
  pickup_lng DECIMAL(11, 8),
  dropoff_lat DECIMAL(10, 8),
  dropoff_lng DECIMAL(11, 8),
  pickup_address TEXT,
  dropoff_address TEXT,

  -- Times
  requested_at TIMESTAMP DEFAULT NOW(),
  matched_at TIMESTAMP,
  driver_arrived_at TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,

  -- Pricing
  estimated_fare DECIMAL(10, 2),
  actual_fare DECIMAL(10, 2),
  surge_multiplier DECIMAL(3, 2) DEFAULT 1.00,
  distance_km DECIMAL(8, 2),
  duration_minutes INT,

  -- Payment
  payment_method_id UUID,
  payment_status ENUM('pending', 'paid', 'failed', 'refunded'),

  -- Ratings
  rider_rating INT CHECK (rider_rating BETWEEN 1 AND 5),
  driver_rating INT CHECK (driver_rating BETWEEN 1 AND 5),

  INDEX idx_rider (rider_id, requested_at),
  INDEX idx_driver (driver_id, requested_at),
  INDEX idx_status (status)
);

-- Ride routes (GPS trail)
CREATE TABLE ride_routes (
  ride_id UUID REFERENCES rides(ride_id),
  sequence_number INT,
  lat DECIMAL(10, 8),
  lng DECIMAL(11, 8),
  timestamp TIMESTAMP,
  PRIMARY KEY (ride_id, sequence_number)
);
```

### 3. Location Service (Cassandra)

**Why Cassandra?**
- High write throughput (362K updates/sec)
- Time-series data
- Horizontal scalability

```cql
-- Driver locations (time-series)
CREATE TABLE driver_locations (
  driver_id UUID,
  timestamp TIMESTAMP,
  lat DECIMAL,
  lng DECIMAL,
  accuracy_meters INT,
  speed_kmh DECIMAL,
  heading_degrees INT,
  PRIMARY KEY (driver_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Rider locations (during trip)
CREATE TABLE rider_locations (
  rider_id UUID,
  timestamp TIMESTAMP,
  lat DECIMAL,
  lng DECIMAL,
  accuracy_meters INT,
  PRIMARY KEY (rider_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

### 4. Redis (Cache)

```redis
# Current driver location (fast lookup)
Key: driver:location:{driver_id}
Value: {
  "lat": 37.7749,
  "lng": -122.4194,
  "timestamp": 1699999999,
  "status": "available"
}
TTL: 60 seconds

# Geospatial index (nearby drivers)
Key: drivers:geo:{region_id}
Type: Geospatial
GEOADD drivers:geo:sf -122.4194 37.7749 driver_123

# Driver availability
Key: driver:status:{driver_id}
Value: "available" | "busy" | "offline"
TTL: 60 seconds

# Active ride state
Key: ride:{ride_id}
Value: {
  "rider_id": "...",
  "driver_id": "...",
  "status": "started",
  "pickup": {...},
  "dropoff": {...}
}
TTL: 24 hours

# User session
Key: session:{user_id}
Value: {
  "device_token": "...",
  "auth_token": "...",
  "device_type": "ios"
}
TTL: 30 days
```

---

## API Design

### REST APIs

#### 1. Request Ride
```http
POST /api/v1/rides/request
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "rider_id": "uuid",
  "pickup": {
    "lat": 37.7749,
    "lng": -122.4194,
    "address": "123 Market St, San Francisco"
  },
  "dropoff": {
    "lat": 37.8044,
    "lng": -122.2712,
    "address": "456 Broadway, Oakland"
  },
  "ride_type": "economy",
  "payment_method_id": "uuid"
}

Response: 201 Created
{
  "ride_id": "uuid",
  "status": "requested",
  "estimated_fare": 25.50,
  "surge_multiplier": 1.5,
  "estimated_wait_time_minutes": 3
}
```

#### 2. Get Ride Status
```http
GET /api/v1/rides/{ride_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "ride_id": "uuid",
  "status": "started",
  "driver": {
    "driver_id": "uuid",
    "name": "John Doe",
    "rating": 4.85,
    "vehicle": "Toyota Camry",
    "license_plate": "ABC123",
    "photo_url": "...",
    "phone_number": "+1234567890"
  },
  "current_location": {
    "lat": 37.7850,
    "lng": -122.4100
  },
  "eta_minutes": 12,
  "distance_remaining_km": 5.2
}
```

#### 3. Update Driver Location
```http
POST /api/v1/drivers/location
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "driver_id": "uuid",
  "lat": 37.7749,
  "lng": -122.4194,
  "accuracy_meters": 10,
  "timestamp": 1699999999
}

Response: 204 No Content
```

#### 4. Get Nearby Drivers (for map visualization)
```http
GET /api/v1/drivers/nearby?lat=37.7749&lng=-122.4194&radius=5
Authorization: Bearer {token}

Response: 200 OK
{
  "drivers": [
    {
      "lat": 37.7750,
      "lng": -122.4200,
      "vehicle_type": "economy"
    },
    {
      "lat": 37.7760,
      "lng": -122.4180,
      "vehicle_type": "premium"
    }
  ]
}
```

#### 5. Complete Ride
```http
POST /api/v1/rides/{ride_id}/complete
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "final_location": {
    "lat": 37.8044,
    "lng": -122.2712
  },
  "distance_km": 12.5,
  "duration_minutes": 22
}

Response: 200 OK
{
  "ride_id": "uuid",
  "status": "completed",
  "actual_fare": 26.75,
  "payment_status": "paid",
  "receipt_url": "https://uber.com/receipts/..."
}
```

#### 6. Rate Driver
```http
POST /api/v1/rides/{ride_id}/rate
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "rating": 5,
  "feedback": "Great driver, very friendly!",
  "tips_amount": 5.00
}

Response: 200 OK
```

### WebSocket APIs (Real-time Updates)

#### Connection
```javascript
const ws = new WebSocket('wss://uber.com/ws');

// Authenticate
ws.send(JSON.stringify({
  type: 'auth',
  token: 'jwt_token',
  user_id: 'uuid'
}));
```

#### Receive Driver Location Updates (Rider)
```javascript
// Server → Rider
{
  type: 'driver_location_update',
  ride_id: 'uuid',
  driver_location: {
    lat: 37.7749,
    lng: -122.4194
  },
  eta_minutes: 3
}
```

#### Receive Ride Updates
```javascript
// Server → Rider/Driver
{
  type: 'ride_status_update',
  ride_id: 'uuid',
  status: 'driver_arrived'
}
```

#### Driver Accepts Ride
```javascript
// Driver → Server
{
  type: 'accept_ride',
  ride_id: 'uuid',
  driver_id: 'uuid'
}

// Server → Rider
{
  type: 'driver_matched',
  ride_id: 'uuid',
  driver: {
    name: 'John Doe',
    rating: 4.85,
    ...
  }
}
```

---

## Scalability

### 1. Geographic Partitioning (Sharding by Region)

**Problem**: Global service requires low latency everywhere

**Solution**: Deploy region-specific clusters

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   US West        │   │   US East        │   │   Europe         │
│   (San Francisco)│   │   (New York)     │   │   (London)       │
├──────────────────┤   ├──────────────────┤   ├──────────────────┤
│ - API Servers    │   │ - API Servers    │   │ - API Servers    │
│ - Redis          │   │ - Redis          │   │ - Redis          │
│ - PostgreSQL     │   │ - PostgreSQL     │   │ - PostgreSQL     │
│ - Cassandra      │   │ - Cassandra      │   │ - Cassandra      │
└──────────────────┘   └──────────────────┘   └──────────────────┘

Cross-region replication (eventual consistency):
- User profiles: Async replication
- Ride history: Replicated for analytics
- Real-time data: Regional only (no replication needed)
```

**Routing**:
- GeoDNS: Route users to nearest region
- Users traveling: Cross-region ride (rare, handled specially)

### 2. Database Scaling

#### PostgreSQL (Users/Rides)
- **Read Replicas**: 10+ per master (read-heavy workload)
- **Sharding**: By city or user_id
  ```
  Shard 1: San Francisco, Oakland
  Shard 2: Los Angeles, San Diego
  Shard 3: New York, Boston
  ```
- **Connection Pooling**: PgBouncer (reduce connection overhead)

#### Cassandra (Locations)
- **Nodes**: 100+ nodes per region
- **Replication Factor**: 3
- **Consistency**: QUORUM (balance consistency and availability)
- **Partitioning**: By driver_id (even distribution)

### 3. Redis Scaling

- **Cluster Mode**: 50-100 shards
- **Geospatial Data**: Sharded by region
- **Replication**: 2 replicas per shard
- **Persistence**: RDB snapshots (not critical if lost)

### 4. Kafka Scaling

- **Brokers**: 20+ per region
- **Topics**:
  - `location_updates`: 100 partitions
  - `ride_requests`: 50 partitions
  - `ride_status_changes`: 50 partitions
- **Retention**: 7 days (replay capability)

### 5. Auto-Scaling

**Metrics**:
- API requests/second
- WebSocket connections
- Database query latency
- Cache hit rate

**Scaling Rules**:
```yaml
api_servers:
  scale_up: cpu > 70% OR requests/sec > 10K
  scale_down: cpu < 30% AND requests/sec < 3K

websocket_servers:
  scale_up: connections > 40K per server
  scale_down: connections < 10K per server
```

---

## Potential Bottlenecks

### 1. Location Update Storm

**Problem**: 1M drivers sending updates every 4 seconds = 250K writes/sec

**Bottleneck**: Database write capacity

**Solutions**:
1. **Write-through Cache**: Write to Redis first, async to Cassandra
2. **Batching**: Batch 100 updates into one Cassandra write
3. **Sampling**: Store every 10th update (for analytics, not real-time)
4. **TTL**: Auto-expire old locations (30 days retention)

### 2. Hot Spot Problem

**Problem**: Major event (e.g., concert) → thousands of riders in same area

**Example**: Stadium concert ends at 10 PM
- 50,000 people request rides simultaneously
- All in 1 km² area
- Only 1,000 drivers nearby

**Bottleneck**:
- Matching service overwhelmed
- Database hotspot (same geohash)
- Surge pricing spikes to 5x

**Solutions**:
1. **Priority Queue**: VIP users, accessibility needs first
2. **Batching**: Match multiple riders to same driver route (UberPool)
3. **Pre-positioning**: Incentivize drivers to area before event ends
4. **Alternative Transportation**: Suggest public transit, walking
5. **Rate Limiting**: Prevent spam requests

### 3. Payment Processing Bottleneck

**Problem**: Payment gateway rate limits (Stripe: 100 req/sec)

**Scale**: 15M rides/day = 174 rides/sec → 174 payments/sec

**Bottleneck**: Exceeds payment gateway limits

**Solutions**:
1. **Multiple Accounts**: Distribute load across accounts
2. **Batching**: Batch payments every 5 minutes (delayed charging)
3. **Retry Queue**: Failed payments retried later
4. **Alternative Gateways**: Failover to backup (Braintree, Adyen)

### 4. ETA Calculation Bottleneck

**Problem**: Google Maps API expensive and has rate limits

**Cost**: $0.005 per request × 30M requests/day (pickup + trip ETA) = $150K/day

**Solutions**:
1. **Cache ETA**: Same route within 15 minutes → reuse ETA
2. **ML Model**: Train model on historical data (cheaper than API)
3. **Batch Requests**: Matrix API (multiple origins/destinations in one call)
4. **Rate Limiting**: Only recalculate when significant location change

### 5. Driver Availability Race Condition

**Problem**: Two riders request same driver simultaneously

**Scenario**:
```
Time  | Rider A Thread         | Rider B Thread
0.0s  | Check driver available | Check driver available
0.1s  | Driver is available ✓  | Driver is available ✓
0.2s  | Match rider A          | Match rider B
0.3s  | Update driver = busy   | Update driver = busy
```
Result: Double booking!

**Solutions**:
1. **Optimistic Locking**:
   ```sql
   UPDATE drivers
   SET status = 'busy', version = version + 1
   WHERE driver_id = '...' AND version = 5;

   -- Returns 0 rows if version mismatch (already updated)
   ```

2. **Pessimistic Locking**:
   ```sql
   SELECT * FROM drivers
   WHERE driver_id = '...'
   FOR UPDATE;  -- Lock row
   ```

3. **Redis Atomic Operations**:
   ```redis
   WATCH driver:status:123
   if status == 'available':
       MULTI
       SET driver:status:123 'busy'
       EXEC
   ```

### 6. WebSocket Connection Limit

**Problem**: 1M concurrent connections × 2 (riders + drivers) = 2M connections

**Bottleneck**: Each server limited to 50K-100K connections (OS limits)

**Solutions**:
1. **Horizontal Scaling**: 20-40 WebSocket servers
2. **Increase OS Limits**:
   ```bash
   ulimit -n 1000000  # File descriptors
   sysctl -w net.core.somaxconn=4096
   ```
3. **Connection Pooling**: Reuse connections
4. **Fallback to Polling**: If WebSocket unavailable

### 7. Geospatial Query Performance

**Problem**: GEORADIUS query slow with millions of drivers

**Example**: 1M drivers in NYC → query takes 100ms+

**Solutions**:
1. **Sharding**: Shard geospatial index by city/region
   ```
   drivers:geo:nyc
   drivers:geo:sf
   drivers:geo:la
   ```

2. **Grid-based Index**: Divide into smaller grids
   ```
   Grid NYC_MANHATTAN: 10K drivers
   Grid NYC_BROOKLYN: 8K drivers
   ```

3. **QuadTree/S2**: Hierarchical spatial index (O(log n) lookup)

4. **Limit Results**: Only return top 20 drivers (pagination)

### 8. Kafka Consumer Lag

**Problem**: Location updates producing faster than consuming

**Example**:
- Producers: 362K updates/sec
- Consumers: 300K updates/sec
- Lag: 62K messages/sec accumulation

**Bottleneck**: Cassandra write speed

**Solutions**:
1. **Add Consumer Instances**: Parallel consumption
2. **Batch Writes**: Write 1000 messages at once
3. **Sampling**: Don't store every location (store every 10th)
4. **TTL**: Auto-expire old messages in Kafka (reduce lag)

### 9. Database Connection Exhaustion

**Problem**: 1000 API servers × 100 connections each = 100K connections

**PostgreSQL default**: 100 max connections → exhausted!

**Solutions**:
1. **Connection Pooling**: PgBouncer (reuse connections)
   ```
   1000 servers → 10 connection pools → 100 connections to DB
   ```

2. **Read Replicas**: Distribute reads across replicas

3. **Increase Max Connections**:
   ```sql
   ALTER SYSTEM SET max_connections = 1000;
   ```
   (But expensive, more overhead)

### 10. Cross-Region Consistency

**Problem**: User travels from SF to NYC

**Scenario**:
- User profile in SF region
- Requests ride in NYC region
- NYC region doesn't have user data

**Solutions**:
1. **Global User Service**: Replicate user data globally
2. **Cache User Profile**: On first request, fetch and cache
3. **Cross-Region Query**: Fallback to SF region if not found
4. **Eventual Consistency**: Accept slight lag (seconds)

---

## Additional Considerations

### 1. Safety Features

- **Emergency Button**: SOS button → alert police
- **Share Trip**: Share live location with friends/family
- **Background Check**: Verify driver identity
- **Two-Way Ratings**: Riders and drivers rate each other
- **GPS Tracking**: Entire trip recorded

### 2. Fraud Detection

- **Fake GPS**: Detect spoofed locations
- **Route Deviation**: Alert if driver goes off route
- **Multiple Accounts**: Prevent abuse (same payment method)
- **Surge Manipulation**: Drivers creating fake demand

**ML Models**:
- Anomaly detection on driver behavior
- Fraudulent payment patterns

### 3. Accessibility

- **Wheelchair Access**: Riders can request accessible vehicles
- **Service Animals**: Drivers must accommodate
- **Hearing/Visual Impairment**: Text-based communication

### 4. Multi-City Support

**Challenge**: Each city has different:
- Traffic patterns
- Pricing
- Regulations
- Popular locations

**Solution**:
- **City-specific Configuration**: Pricing, surge, geofences
- **Localization**: Languages, currencies
- **Compliance**: Different regulations (e.g., NYC TLC)

### 5. Disaster Recovery

**Backup Strategy**:
- **Databases**: Daily snapshots + WAL archiving
- **Cross-Region Replication**: Failover to another region
- **RTO**: 1 hour (how fast to recover)
- **RPO**: 5 minutes (how much data loss acceptable)

**Failover Plan**:
1. Detect failure (health checks)
2. Promote read replica to master
3. Redirect traffic (DNS update)
4. Investigate root cause

---

## Summary

Uber is a complex distributed system requiring:

**Key Design Decisions**:
1. **Geospatial Indexing**: Redis GEORADIUS or QuadTree/S2
2. **Real-time Updates**: WebSockets for live tracking
3. **Event-Driven**: Kafka for async processing
4. **Geographic Sharding**: Region-specific deployments
5. **Eventual Consistency**: Accept for non-critical data
6. **Surge Pricing**: Dynamic pricing based on supply/demand

**Scale Numbers**:
- 15M rides/day
- 1M active drivers
- 362K location updates/sec
- 170K read requests/sec
- < 2 second matching latency

**Technology Stack**:
- **Databases**: PostgreSQL (users/rides), Cassandra (locations), Redis (cache/geo)
- **Messaging**: Kafka (event streaming)
- **Real-time**: WebSockets
- **Maps**: Google Maps API, ML for ETA
- **Payments**: Stripe, Braintree
- **Notifications**: FCM, APNS, Twilio

This design showcases building a globally distributed, real-time, location-based service at massive scale!
