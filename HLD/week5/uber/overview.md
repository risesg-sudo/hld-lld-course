# Uber: Overview and Requirements

## What Are We Designing?

Uber is a real-time ride-sharing platform that matches riders with drivers based on location. The core challenge is matching supply (drivers) with demand (riders) with sub-second latency while tracking millions of moving vehicles in real-time.

## The Real-Time Challenge

When a rider requests a ride:
- System must find nearby available drivers within 2 seconds
- Track driver location updates every 4 seconds (360K updates/sec globally)
- Calculate accurate ETA considering traffic
- Handle concurrent requests without double-booking drivers
- Provide real-time updates to both rider and driver

## Functional Requirements

**Ride Request**: Users request ride from point A to B, system finds and matches driver.

**Real-Time Tracking**: Both rider and driver see each other's live location during trip.

**Pricing**: Calculate fare based on distance, time, and surge multiplier.

**ETA Calculation**: Estimate pickup time and trip duration accurately.

**Payment**: Process payment securely at trip completion.

**Ratings**: Two-way rating system (riders rate drivers, drivers rate riders).

## Non-Functional Requirements

**Scale**: 15 million rides per day, 1 million concurrent drivers, 20 million DAU

**Low Latency**: Driver matching in under 2 seconds

**Real-Time**: Location updates every 3-5 seconds

**Accuracy**: Precise geospatial queries within meter-level precision

**Consistency**: No double-booking of drivers (strong consistency required)

**Availability**: 99.99% uptime (critical service for safety)

## Why These Are Challenging

**Geospatial at scale**: Querying "drivers within 5km" among millions requires specialized data structures (QuadTree, S2).

**Real-time updates**: 360K location updates/second must be processed, stored, and made queryable instantly.

**Race conditions**: Two riders requesting same driver simultaneously must be handled atomically.

**Global deployment**: City-specific pricing, regulations, traffic patterns require regional deployments.

**Mobile-first**: Must work on spotty networks common in developing markets.
