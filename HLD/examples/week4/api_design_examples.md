# RESTful API Design Examples

This guide provides comprehensive examples of well-designed RESTful APIs following industry best practices.

## Table of Contents
1. [E-Commerce API](#e-commerce-api)
2. [Social Media API](#social-media-api)
3. [Blog Platform API](#blog-platform-api)
4. [Error Handling Examples](#error-handling-examples)
5. [Versioning Strategies](#versioning-strategies)
6. [Common Patterns](#common-patterns)

---

## E-Commerce API

A comprehensive e-commerce API design covering products, orders, payments, and more.

### Base URL
```
https://api.shopify.example.com/v1
```

### Authentication
```
Authorization: Bearer {access_token}
```

### Resources

#### 1. Products

**List Products**
```http
GET /products?page=1&limit=20&sort=-created_at&category=electronics&min_price=100&max_price=1000

Response: 200 OK
{
  "data": [
    {
      "id": "prod_123",
      "name": "Wireless Headphones",
      "description": "Premium noise-cancelling headphones",
      "price": 299.99,
      "currency": "USD",
      "category": "electronics",
      "stock": 150,
      "images": [
        {
          "url": "https://cdn.example.com/images/prod_123_main.jpg",
          "alt": "Main product image",
          "type": "main"
        }
      ],
      "rating": 4.5,
      "reviews_count": 1250,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-15T14:30:00Z",
      "_links": {
        "self": { "href": "/products/prod_123" },
        "reviews": { "href": "/products/prod_123/reviews" },
        "related": { "href": "/products/prod_123/related" }
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_pages": 50,
    "total_items": 1000,
    "has_next": true,
    "has_prev": false
  },
  "_links": {
    "self": { "href": "/products?page=1&limit=20" },
    "next": { "href": "/products?page=2&limit=20" },
    "first": { "href": "/products?page=1&limit=20" },
    "last": { "href": "/products?page=50&limit=20" }
  }
}
```

**Get Single Product**
```http
GET /products/prod_123

Response: 200 OK
{
  "id": "prod_123",
  "name": "Wireless Headphones",
  "description": "Premium noise-cancelling headphones with 30-hour battery life",
  "long_description": "...",
  "price": 299.99,
  "currency": "USD",
  "category": "electronics",
  "subcategory": "audio",
  "brand": "TechBrand",
  "sku": "WH-1000XM5",
  "stock": 150,
  "images": [...],
  "specifications": {
    "battery_life": "30 hours",
    "bluetooth_version": "5.2",
    "weight": "250g"
  },
  "rating": 4.5,
  "reviews_count": 1250,
  "tags": ["wireless", "bluetooth", "noise-cancelling"],
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

**Create Product** (Admin only)
```http
POST /products
Content-Type: application/json

{
  "name": "Smart Watch",
  "description": "Fitness tracking smartwatch",
  "price": 199.99,
  "currency": "USD",
  "category": "electronics",
  "stock": 100,
  "images": [...]
}

Response: 201 Created
Location: /products/prod_124

{
  "id": "prod_124",
  "name": "Smart Watch",
  "description": "Fitness tracking smartwatch",
  "price": 199.99,
  "currency": "USD",
  "category": "electronics",
  "stock": 100,
  "created_at": "2025-01-16T10:00:00Z",
  "updated_at": "2025-01-16T10:00:00Z"
}
```

**Update Product** (Admin only)
```http
PATCH /products/prod_123
Content-Type: application/json

{
  "price": 279.99,
  "stock": 175
}

Response: 200 OK
{
  "id": "prod_123",
  "name": "Wireless Headphones",
  "price": 279.99,  // Updated
  "stock": 175,     // Updated
  "updated_at": "2025-01-16T11:00:00Z"
}
```

**Delete Product** (Admin only)
```http
DELETE /products/prod_123

Response: 204 No Content
```

#### 2. Product Reviews

**List Reviews**
```http
GET /products/prod_123/reviews?page=1&limit=10&sort=-rating

Response: 200 OK
{
  "data": [
    {
      "id": "rev_456",
      "product_id": "prod_123",
      "user_id": "user_789",
      "user_name": "John Doe",
      "rating": 5,
      "title": "Excellent headphones!",
      "comment": "Best headphones I've ever owned. Great sound quality.",
      "verified_purchase": true,
      "helpful_count": 25,
      "images": [],
      "created_at": "2025-01-10T15:30:00Z"
    }
  ],
  "pagination": {...}
}
```

**Create Review**
```http
POST /products/prod_123/reviews
Content-Type: application/json

{
  "rating": 5,
  "title": "Great product!",
  "comment": "Exceeded my expectations"
}

Response: 201 Created
```

#### 3. Shopping Cart

**Get Cart**
```http
GET /cart

Response: 200 OK
{
  "id": "cart_abc",
  "user_id": "user_789",
  "items": [
    {
      "product_id": "prod_123",
      "product_name": "Wireless Headphones",
      "quantity": 1,
      "unit_price": 299.99,
      "total_price": 299.99,
      "image": "https://cdn.example.com/images/prod_123_thumb.jpg"
    }
  ],
  "subtotal": 299.99,
  "tax": 24.00,
  "shipping": 10.00,
  "total": 333.99,
  "currency": "USD",
  "updated_at": "2025-01-16T10:00:00Z"
}
```

**Add to Cart**
```http
POST /cart/items
Content-Type: application/json

{
  "product_id": "prod_123",
  "quantity": 1
}

Response: 201 Created
{
  "id": "cart_abc",
  "items": [...],
  "total": 333.99
}
```

**Update Cart Item**
```http
PATCH /cart/items/prod_123
Content-Type: application/json

{
  "quantity": 2
}

Response: 200 OK
```

**Remove from Cart**
```http
DELETE /cart/items/prod_123

Response: 204 No Content
```

**Clear Cart**
```http
DELETE /cart

Response: 204 No Content
```

#### 4. Orders

**List Orders**
```http
GET /orders?status=completed&from_date=2025-01-01&to_date=2025-01-31

Response: 200 OK
{
  "data": [
    {
      "id": "ord_xyz",
      "order_number": "ORD-2025-001234",
      "status": "completed",
      "items": [
        {
          "product_id": "prod_123",
          "product_name": "Wireless Headphones",
          "quantity": 1,
          "unit_price": 299.99,
          "total_price": 299.99
        }
      ],
      "subtotal": 299.99,
      "tax": 24.00,
      "shipping": 10.00,
      "total": 333.99,
      "currency": "USD",
      "payment_method": "credit_card",
      "payment_status": "paid",
      "shipping_address": {
        "name": "John Doe",
        "street": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102",
        "country": "US"
      },
      "tracking_number": "1Z999AA10123456784",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-16T14:00:00Z",
      "_links": {
        "self": { "href": "/orders/ord_xyz" },
        "tracking": { "href": "/orders/ord_xyz/tracking" },
        "invoice": { "href": "/orders/ord_xyz/invoice" }
      }
    }
  ],
  "pagination": {...}
}
```

**Create Order**
```http
POST /orders
Content-Type: application/json

{
  "items": [
    {
      "product_id": "prod_123",
      "quantity": 1
    }
  ],
  "shipping_address": {
    "name": "John Doe",
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94102",
    "country": "US"
  },
  "payment_method": "credit_card",
  "payment_details": {
    "token": "tok_visa_1234"
  }
}

Response: 201 Created
Location: /orders/ord_xyz

{
  "id": "ord_xyz",
  "order_number": "ORD-2025-001234",
  "status": "pending",
  "total": 333.99,
  "created_at": "2025-01-16T10:00:00Z"
}
```

**Get Order Status**
```http
GET /orders/ord_xyz

Response: 200 OK
{
  "id": "ord_xyz",
  "status": "shipped",
  "tracking_number": "1Z999AA10123456784",
  "estimated_delivery": "2025-01-20T18:00:00Z"
}
```

**Cancel Order**
```http
POST /orders/ord_xyz/cancel

Response: 200 OK
{
  "id": "ord_xyz",
  "status": "cancelled",
  "refund_status": "processing"
}
```

#### 5. Users

**Get User Profile**
```http
GET /users/me

Response: 200 OK
{
  "id": "user_789",
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-555-1234",
  "addresses": [
    {
      "id": "addr_001",
      "type": "shipping",
      "is_default": true,
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94102",
      "country": "US"
    }
  ],
  "created_at": "2024-01-01T10:00:00Z",
  "email_verified": true
}
```

**Update User Profile**
```http
PATCH /users/me
Content-Type: application/json

{
  "first_name": "Johnny",
  "phone": "+1-555-5678"
}

Response: 200 OK
```

#### 6. Search

**Search Products**
```http
GET /search?q=wireless+headphones&category=electronics&min_price=200&max_price=500&sort=relevance

Response: 200 OK
{
  "query": "wireless headphones",
  "filters": {
    "category": "electronics",
    "min_price": 200,
    "max_price": 500
  },
  "results": [
    {
      "id": "prod_123",
      "name": "Wireless Headphones",
      "price": 299.99,
      "relevance_score": 0.95,
      "highlight": "Premium <em>wireless headphones</em> with noise cancellation"
    }
  ],
  "total_results": 150,
  "search_time_ms": 45
}
```

---

## Social Media API

Twitter/Facebook-like API design.

### Base URL
```
https://api.social.example.com/v1
```

### Resources

#### 1. Posts

**Create Post**
```http
POST /posts
Content-Type: application/json

{
  "content": "Just launched my new project! 🚀",
  "media": [
    {
      "type": "image",
      "url": "https://cdn.example.com/img123.jpg"
    }
  ],
  "visibility": "public"
}

Response: 201 Created
{
  "id": "post_abc123",
  "content": "Just launched my new project! 🚀",
  "author": {
    "id": "user_789",
    "username": "johndoe",
    "display_name": "John Doe",
    "avatar": "https://cdn.example.com/avatars/johndoe.jpg"
  },
  "media": [...],
  "visibility": "public",
  "likes_count": 0,
  "comments_count": 0,
  "shares_count": 0,
  "created_at": "2025-01-16T10:00:00Z",
  "_links": {
    "self": { "href": "/posts/post_abc123" },
    "likes": { "href": "/posts/post_abc123/likes" },
    "comments": { "href": "/posts/post_abc123/comments" }
  }
}
```

**Get Feed**
```http
GET /feed?type=home&cursor=abc123&limit=20

Response: 200 OK
{
  "data": [
    {
      "id": "post_abc123",
      "content": "Just launched my new project! 🚀",
      "author": {...},
      "likes_count": 150,
      "comments_count": 25,
      "has_liked": false,
      "created_at": "2025-01-16T10:00:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "xyz789",
    "has_more": true
  }
}
```

**Like Post**
```http
POST /posts/post_abc123/likes

Response: 201 Created
{
  "liked": true,
  "likes_count": 151
}
```

**Unlike Post**
```http
DELETE /posts/post_abc123/likes

Response: 200 OK
{
  "liked": false,
  "likes_count": 150
}
```

#### 2. Comments

**Add Comment**
```http
POST /posts/post_abc123/comments
Content-Type: application/json

{
  "content": "Congratulations! 🎉"
}

Response: 201 Created
{
  "id": "cmt_456",
  "post_id": "post_abc123",
  "content": "Congratulations! 🎉",
  "author": {...},
  "likes_count": 0,
  "created_at": "2025-01-16T10:05:00Z"
}
```

**Get Comments**
```http
GET /posts/post_abc123/comments?sort=top&limit=10

Response: 200 OK
{
  "data": [
    {
      "id": "cmt_456",
      "content": "Congratulations! 🎉",
      "author": {...},
      "likes_count": 5,
      "created_at": "2025-01-16T10:05:00Z"
    }
  ],
  "total_count": 25
}
```

#### 3. Users & Followers

**Follow User**
```http
POST /users/user_123/follow

Response: 201 Created
{
  "following": true,
  "follower_count": 1001
}
```

**Unfollow User**
```http
DELETE /users/user_123/follow

Response: 200 OK
{
  "following": false,
  "follower_count": 1000
}
```

**Get Followers**
```http
GET /users/user_123/followers?cursor=abc&limit=50

Response: 200 OK
{
  "data": [
    {
      "id": "user_456",
      "username": "janedoe",
      "display_name": "Jane Doe",
      "avatar": "...",
      "bio": "Software Engineer",
      "is_following": true,
      "follows_you": false
    }
  ],
  "pagination": {...}
}
```

---

## Blog Platform API

Medium/WordPress-like API design.

### Base URL
```
https://api.blog.example.com/v1
```

### Resources

#### 1. Articles

**List Articles**
```http
GET /articles?status=published&tag=javascript&author=johndoe&sort=-published_at

Response: 200 OK
{
  "data": [
    {
      "id": "art_123",
      "slug": "introduction-to-rest-apis",
      "title": "Introduction to REST APIs",
      "subtitle": "A comprehensive guide",
      "excerpt": "Learn the fundamentals of RESTful API design...",
      "author": {
        "id": "user_789",
        "username": "johndoe",
        "display_name": "John Doe",
        "avatar": "..."
      },
      "cover_image": "https://cdn.example.com/covers/art_123.jpg",
      "tags": ["javascript", "api", "rest"],
      "reading_time": 8,
      "likes_count": 250,
      "comments_count": 45,
      "views_count": 1500,
      "status": "published",
      "published_at": "2025-01-15T10:00:00Z",
      "_links": {
        "self": { "href": "/articles/art_123" },
        "html": { "href": "https://blog.example.com/introduction-to-rest-apis" }
      }
    }
  ],
  "pagination": {...}
}
```

**Get Article**
```http
GET /articles/art_123

Response: 200 OK
{
  "id": "art_123",
  "slug": "introduction-to-rest-apis",
  "title": "Introduction to REST APIs",
  "subtitle": "A comprehensive guide",
  "content": "# Introduction\n\nREST APIs are...",
  "content_html": "<h1>Introduction</h1><p>REST APIs are...</p>",
  "author": {...},
  "cover_image": "...",
  "tags": ["javascript", "api", "rest"],
  "reading_time": 8,
  "likes_count": 250,
  "comments_count": 45,
  "views_count": 1500,
  "has_liked": false,
  "has_bookmarked": false,
  "status": "published",
  "published_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

**Create Draft**
```http
POST /articles
Content-Type: application/json

{
  "title": "My New Article",
  "content": "# Introduction\n\nThis is my article...",
  "tags": ["tutorial", "programming"],
  "status": "draft"
}

Response: 201 Created
Location: /articles/art_124

{
  "id": "art_124",
  "title": "My New Article",
  "status": "draft",
  "created_at": "2025-01-16T10:00:00Z"
}
```

**Publish Article**
```http
POST /articles/art_124/publish

Response: 200 OK
{
  "id": "art_124",
  "status": "published",
  "published_at": "2025-01-16T10:05:00Z"
}
```

#### 2. Collections/Series

**Create Collection**
```http
POST /collections
Content-Type: application/json

{
  "name": "API Design Series",
  "description": "A series about API design best practices",
  "articles": ["art_123", "art_124"]
}

Response: 201 Created
```

**Get Collection**
```http
GET /collections/col_456

Response: 200 OK
{
  "id": "col_456",
  "name": "API Design Series",
  "description": "...",
  "articles": [
    {
      "id": "art_123",
      "title": "Introduction to REST APIs",
      "order": 1
    }
  ],
  "articles_count": 5,
  "followers_count": 120
}
```

---

## Error Handling Examples

### Standard Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters",
        "code": "TOO_SHORT"
      }
    ],
    "request_id": "req_abc123",
    "timestamp": "2025-01-16T10:00:00Z"
  }
}
```

### Error Examples

**400 Bad Request - Validation Error**
```http
POST /users
Content-Type: application/json

{
  "email": "invalid-email",
  "password": "123"
}

Response: 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      }
    ]
  }
}
```

**401 Unauthorized**
```http
GET /profile

Response: 401 Unauthorized
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": "Missing or invalid authentication token"
  }
}
```

**403 Forbidden**
```http
DELETE /products/prod_123

Response: 403 Forbidden
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions",
    "details": "Admin role required for this operation"
  }
}
```

**404 Not Found**
```http
GET /products/prod_nonexistent

Response: 404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": "Product with ID 'prod_nonexistent' does not exist"
  }
}
```

**409 Conflict**
```http
POST /users
Content-Type: application/json

{
  "username": "existing_user",
  "email": "new@example.com"
}

Response: 409 Conflict
{
  "error": {
    "code": "CONFLICT",
    "message": "Resource already exists",
    "details": "Username 'existing_user' is already taken"
  }
}
```

**422 Unprocessable Entity**
```http
POST /orders
Content-Type: application/json

{
  "items": [
    {
      "product_id": "prod_123",
      "quantity": 1000
    }
  ]
}

Response: 422 Unprocessable Entity
{
  "error": {
    "code": "UNPROCESSABLE_ENTITY",
    "message": "Cannot process request",
    "details": "Insufficient stock for product 'prod_123'. Available: 150, Requested: 1000"
  }
}
```

**429 Too Many Requests**
```http
POST /api/posts

Response: 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705406400
Retry-After: 60

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": "Rate limit of 100 requests per hour exceeded. Try again in 60 seconds."
  }
}
```

**500 Internal Server Error**
```http
GET /products

Response: 500 Internal Server Error
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "details": "Please try again later. If the problem persists, contact support.",
    "request_id": "req_abc123"
  }
}
```

**503 Service Unavailable**
```http
GET /api/data

Response: 503 Service Unavailable
Retry-After: 120

{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service temporarily unavailable",
    "details": "System is undergoing maintenance. Please try again in 2 minutes."
  }
}
```

---

## Versioning Strategies

### 1. URL Path Versioning (Recommended)

```http
GET https://api.example.com/v1/products
GET https://api.example.com/v2/products
```

**Pros:**
- Clear and explicit
- Easy to route
- Easy to deprecate old versions

**Cons:**
- URL changes between versions
- Version proliferation

### 2. Header Versioning

```http
GET https://api.example.com/products
Accept: application/vnd.example.v1+json

GET https://api.example.com/products
Accept: application/vnd.example.v2+json
```

**Pros:**
- Clean URLs
- RESTful

**Cons:**
- Less visible
- Harder to test in browser

### 3. Query Parameter Versioning

```http
GET https://api.example.com/products?version=1
GET https://api.example.com/products?api_version=2
```

**Pros:**
- Simple
- Easy to implement

**Cons:**
- Pollutes query parameters
- Less clean

### Version Migration Example

**V1 Response:**
```json
{
  "id": "prod_123",
  "name": "Product Name",
  "price": 99.99
}
```

**V2 Response (Breaking changes):**
```json
{
  "id": "prod_123",
  "name": "Product Name",
  "pricing": {
    "amount": 99.99,
    "currency": "USD",
    "discount": null
  }
}
```

**Deprecation Notice:**
```http
GET /v1/products
Deprecation: version="v1"
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Link: <https://api.example.com/v2/products>; rel="successor-version"

{
  "data": [...],
  "_meta": {
    "deprecated": true,
    "sunset_date": "2025-12-31T23:59:59Z",
    "migration_guide": "https://docs.example.com/migration/v1-to-v2"
  }
}
```

---

## Common Patterns

### 1. Batch Operations

**Batch Create**
```http
POST /products/batch
Content-Type: application/json

{
  "products": [
    { "name": "Product 1", "price": 10.00 },
    { "name": "Product 2", "price": 20.00 }
  ]
}

Response: 207 Multi-Status
{
  "results": [
    {
      "index": 0,
      "status": 201,
      "data": { "id": "prod_001", "name": "Product 1" }
    },
    {
      "index": 1,
      "status": 400,
      "error": { "message": "Invalid price" }
    }
  ]
}
```

### 2. Partial Responses (Field Selection)

```http
GET /products/prod_123?fields=id,name,price

Response: 200 OK
{
  "id": "prod_123",
  "name": "Product Name",
  "price": 99.99
}
```

### 3. Bulk Updates

```http
PATCH /products
Content-Type: application/json

{
  "updates": [
    {
      "id": "prod_123",
      "changes": { "price": 89.99 }
    },
    {
      "id": "prod_124",
      "changes": { "stock": 100 }
    }
  ]
}
```

### 4. Async Operations

```http
POST /reports/generate
Content-Type: application/json

{
  "type": "sales",
  "from_date": "2025-01-01",
  "to_date": "2025-01-31"
}

Response: 202 Accepted
Location: /jobs/job_123

{
  "job_id": "job_123",
  "status": "processing",
  "created_at": "2025-01-16T10:00:00Z",
  "_links": {
    "status": { "href": "/jobs/job_123" }
  }
}
```

**Check Status:**
```http
GET /jobs/job_123

Response: 200 OK
{
  "id": "job_123",
  "status": "completed",
  "result": {
    "download_url": "https://cdn.example.com/reports/sales_jan2025.pdf"
  },
  "created_at": "2025-01-16T10:00:00Z",
  "completed_at": "2025-01-16T10:05:00Z"
}
```

### 5. Webhooks

**Register Webhook**
```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://myapp.com/webhooks/orders",
  "events": ["order.created", "order.shipped"],
  "secret": "whsec_abc123"
}

Response: 201 Created
{
  "id": "wh_456",
  "url": "https://myapp.com/webhooks/orders",
  "events": ["order.created", "order.shipped"],
  "active": true,
  "created_at": "2025-01-16T10:00:00Z"
}
```

**Webhook Payload:**
```json
POST https://myapp.com/webhooks/orders
X-Webhook-ID: wh_456
X-Webhook-Signature: sha256=abc123...
Content-Type: application/json

{
  "event": "order.created",
  "data": {
    "id": "ord_789",
    "total": 299.99,
    "created_at": "2025-01-16T10:00:00Z"
  },
  "timestamp": "2025-01-16T10:00:01Z"
}
```

---

## Best Practices Summary

1. **Use nouns for resources, not verbs**
   - ✅ GET /products
   - ❌ GET /getProducts

2. **Use HTTP methods correctly**
   - GET: Read
   - POST: Create
   - PUT: Replace
   - PATCH: Update
   - DELETE: Delete

3. **Use proper status codes**
   - 2xx: Success
   - 4xx: Client error
   - 5xx: Server error

4. **Always paginate collections**
   - Include total count
   - Provide next/previous links

5. **Version your API**
   - Plan for changes
   - Deprecate gracefully

6. **Provide filtering, sorting, searching**
   - Make APIs flexible
   - Use query parameters

7. **Use consistent error format**
   - Include error code
   - Provide helpful messages

8. **Implement rate limiting**
   - Protect your service
   - Communicate limits in headers

9. **Document everything**
   - OpenAPI/Swagger
   - Examples for every endpoint

10. **Use HTTPS everywhere**
    - Security is not optional

---

**Remember:** Good API design is about making developers' lives easier. Be consistent, predictable, and well-documented.
