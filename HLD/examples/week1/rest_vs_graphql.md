# REST vs GraphQL - Detailed Comparison

## Overview

This document provides a comprehensive comparison between REST and GraphQL with practical code examples, use cases, and decision criteria.

---

## 1. Basic Concepts

### REST (Representational State Transfer)

REST is an architectural style that uses HTTP methods to interact with resources through multiple endpoints.

**Key Principles:**
- Resource-based (nouns, not verbs)
- Stateless
- Uniform interface
- Multiple endpoints
- HTTP methods define operations

### GraphQL

GraphQL is a query language for APIs that allows clients to request exactly the data they need through a single endpoint.

**Key Principles:**
- Single endpoint
- Client-specified queries
- Strongly typed schema
- Hierarchical structure
- Introspective

---

## 2. Example Scenario: Blog Platform

Let's compare REST and GraphQL for a blog platform with users, posts, and comments.

### Data Model

```javascript
User {
  id: 1,
  name: "Alice",
  email: "alice@example.com",
  posts: [...]
}

Post {
  id: 101,
  title: "GraphQL vs REST",
  content: "...",
  author: User,
  comments: [...]
}

Comment {
  id: 1001,
  text: "Great post!",
  author: User,
  post: Post
}
```

---

## 3. REST Implementation

### REST API Endpoints

```
# Users
GET    /api/users           # List all users
GET    /api/users/:id       # Get specific user
POST   /api/users           # Create user
PUT    /api/users/:id       # Update user
DELETE /api/users/:id       # Delete user

# Posts
GET    /api/posts           # List all posts
GET    /api/posts/:id       # Get specific post
POST   /api/posts           # Create post
PUT    /api/posts/:id       # Update post
DELETE /api/posts/:id       # Delete post
GET    /api/users/:id/posts # Get user's posts

# Comments
GET    /api/posts/:id/comments    # Get post's comments
POST   /api/posts/:id/comments    # Add comment
PUT    /api/comments/:id          # Update comment
DELETE /api/comments/:id          # Delete comment
```

### REST Request/Response Examples

#### Example 1: Get a Post with Author and Comments

**Problem: Multiple Requests Needed (N+1 Problem)**

```bash
# Request 1: Get post
GET /api/posts/101
```

```json
{
  "id": 101,
  "title": "GraphQL vs REST",
  "content": "Full content here...",
  "authorId": 1,
  "createdAt": "2025-01-15"
}
```

```bash
# Request 2: Get author
GET /api/users/1
```

```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com"
}
```

```bash
# Request 3: Get comments
GET /api/posts/101/comments
```

```json
[
  {
    "id": 1001,
    "text": "Great post!",
    "authorId": 2,
    "createdAt": "2025-01-16"
  },
  {
    "id": 1002,
    "text": "Thanks for sharing",
    "authorId": 3,
    "createdAt": "2025-01-16"
  }
]
```

```bash
# Request 4: Get comment author 1
GET /api/users/2

# Request 5: Get comment author 2
GET /api/users/3
```

**Total: 5 requests!**

#### Example 2: Get Just Post Titles

**Problem: Over-fetching**

```bash
GET /api/posts
```

```json
[
  {
    "id": 101,
    "title": "GraphQL vs REST",
    "content": "Full content here...",  // Don't need this
    "authorId": 1,
    "createdAt": "2025-01-15",
    "updatedAt": "2025-01-15",
    "tags": ["api", "comparison"],      // Don't need this
    "metadata": {...}                   // Don't need this
  },
  // ... more posts
]
```

**Received much more data than needed!**

### REST Python Server Implementation

```python
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory database
users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"}
}

posts = {
    101: {
        "id": 101,
        "title": "GraphQL vs REST",
        "content": "Content here...",
        "authorId": 1,
        "createdAt": "2025-01-15"
    },
    102: {
        "id": 102,
        "title": "Introduction to APIs",
        "content": "More content...",
        "authorId": 1,
        "createdAt": "2025-01-14"
    }
}

comments = {
    1001: {"id": 1001, "text": "Great post!", "authorId": 2, "postId": 101},
    1002: {"id": 1002, "text": "Thanks!", "authorId": 1, "postId": 101}
}

# Users endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# Posts endpoints
@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(list(posts.values()))

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = posts.get(post_id)
    if post:
        return jsonify(post)
    return jsonify({"error": "Post not found"}), 404

@app.route('/api/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    user_posts = [p for p in posts.values() if p['authorId'] == user_id]
    return jsonify(user_posts)

# Comments endpoints
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    post_comments = [c for c in comments.values() if c['postId'] == post_id]
    return jsonify(post_comments)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 4. GraphQL Implementation

### GraphQL Schema

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  createdAt: String!
}

type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
  createdAt: String!
}

type Query {
  user(id: ID!): User
  users: [User!]!
  post(id: ID!): Post
  posts: [Post!]!
}

type Mutation {
  createPost(title: String!, content: String!, authorId: ID!): Post!
  createComment(text: String!, postId: ID!, authorId: ID!): Comment!
  updatePost(id: ID!, title: String, content: String): Post!
  deletePost(id: ID!): Boolean!
}
```

### GraphQL Query Examples

#### Example 1: Get Post with Author and Comments (Single Request!)

```graphql
query GetPostWithDetails {
  post(id: "101") {
    id
    title
    content
    author {
      name
      email
    }
    comments {
      text
      author {
        name
      }
      createdAt
    }
  }
}
```

**Response:**

```json
{
  "data": {
    "post": {
      "id": "101",
      "title": "GraphQL vs REST",
      "content": "Full content here...",
      "author": {
        "name": "Alice",
        "email": "alice@example.com"
      },
      "comments": [
        {
          "text": "Great post!",
          "author": {
            "name": "Bob"
          },
          "createdAt": "2025-01-16"
        },
        {
          "text": "Thanks for sharing",
          "author": {
            "name": "Charlie"
          },
          "createdAt": "2025-01-16"
        }
      ]
    }
  }
}
```

**Total: 1 request!**

#### Example 2: Get Just Post Titles (No Over-fetching!)

```graphql
query GetPostTitles {
  posts {
    id
    title
  }
}
```

**Response:**

```json
{
  "data": {
    "posts": [
      {
        "id": "101",
        "title": "GraphQL vs REST"
      },
      {
        "id": "102",
        "title": "Introduction to APIs"
      }
    ]
  }
}
```

**Exactly what we need!**

### GraphQL Python Server Implementation

```python
import graphene
from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS

# In-memory database
users_db = {
    "1": {"id": "1", "name": "Alice", "email": "alice@example.com"},
    "2": {"id": "2", "name": "Bob", "email": "bob@example.com"}
}

posts_db = {
    "101": {"id": "101", "title": "GraphQL vs REST", "content": "Content...", "authorId": "1"},
    "102": {"id": "102", "title": "Intro to APIs", "content": "More...", "authorId": "1"}
}

comments_db = {
    "1001": {"id": "1001", "text": "Great!", "authorId": "2", "postId": "101"},
    "1002": {"id": "1002", "text": "Thanks!", "authorId": "1", "postId": "101"}
}

# GraphQL Types
class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
    posts = graphene.List(lambda: Post)

    def resolve_posts(self, info):
        return [Post(**p) for p in posts_db.values() if p['authorId'] == self.id]

class Post(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    author = graphene.Field(User)
    comments = graphene.List(lambda: Comment)

    def resolve_author(self, info):
        user_data = users_db.get(self.authorId)
        return User(**user_data) if user_data else None

    def resolve_comments(self, info):
        return [Comment(**c) for c in comments_db.values() if c['postId'] == self.id]

class Comment(graphene.ObjectType):
    id = graphene.ID()
    text = graphene.String()
    author = graphene.Field(User)
    post = graphene.Field(Post)

    def resolve_author(self, info):
        user_data = users_db.get(self.authorId)
        return User(**user_data) if user_data else None

    def resolve_post(self, info):
        post_data = posts_db.get(self.postId)
        return Post(**post_data) if post_data else None

# Query Root
class Query(graphene.ObjectType):
    user = graphene.Field(User, id=graphene.ID(required=True))
    users = graphene.List(User)
    post = graphene.Field(Post, id=graphene.ID(required=True))
    posts = graphene.List(Post)

    def resolve_user(self, info, id):
        user_data = users_db.get(id)
        return User(**user_data) if user_data else None

    def resolve_users(self, info):
        return [User(**u) for u in users_db.values()]

    def resolve_post(self, info, id):
        post_data = posts_db.get(id)
        return Post(**post_data) if post_data else None

    def resolve_posts(self, info):
        return [Post(**p) for p in posts_db.values()]

# Mutations
class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        author_id = graphene.ID(required=True)

    post = graphene.Field(Post)

    def mutate(self, info, title, content, author_id):
        post_id = str(max([int(k) for k in posts_db.keys()]) + 1)
        new_post = {
            "id": post_id,
            "title": title,
            "content": content,
            "authorId": author_id
        }
        posts_db[post_id] = new_post
        return CreatePost(post=Post(**new_post))

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Flask App
app = Flask(__name__)
CORS(app)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 5. Detailed Comparison

### Over-fetching and Under-fetching

| Scenario | REST | GraphQL |
|----------|------|---------|
| **Get post titles only** | Returns full post objects (over-fetching) | Request only `id` and `title` fields |
| **Get post with author and comments** | Need 3+ requests (under-fetching) | Single request with nested fields |
| **Mobile app (bandwidth limited)** | Wastes bandwidth | Optimized payload |

### Versioning

**REST:**
```
/api/v1/users
/api/v2/users  # New version
```
- Need to maintain multiple versions
- Breaking changes require new version
- Deprecation strategy complex

**GraphQL:**
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  fullName: String! @deprecated(reason: "Use 'name' instead")
}
```
- Schema evolution
- Deprecate fields, don't remove
- Single endpoint
- Backward compatible

### Caching

**REST:**
- HTTP caching works out of the box
- Cache by URL
- ETags, Cache-Control headers
- CDN friendly

**GraphQL:**
- More complex (POST requests, single endpoint)
- Need custom caching (Apollo Cache, DataLoader)
- Can cache by query hash
- Persisted queries help

### Error Handling

**REST:**
```json
// HTTP 404
{
  "error": "User not found",
  "code": "USER_NOT_FOUND"
}
```
- Uses HTTP status codes
- Clear error semantics

**GraphQL:**
```json
// HTTP 200 (even with errors!)
{
  "data": {
    "user": null
  },
  "errors": [
    {
      "message": "User not found",
      "path": ["user"],
      "extensions": {
        "code": "USER_NOT_FOUND"
      }
    }
  ]
}
```
- Always returns 200 (usually)
- Errors in response body
- Partial results possible

### File Uploads

**REST:**
```bash
curl -X POST -F "file=@photo.jpg" /api/upload
```
- Native multipart/form-data support
- Straightforward

**GraphQL:**
```graphql
mutation UploadFile($file: Upload!) {
  uploadFile(file: $file) {
    url
  }
}
```
- Requires additional spec (Apollo Upload)
- More complex setup

---

## 6. Performance Comparison

### Payload Size Example

**REST - Get 10 Posts with Authors:**
```
Request 1: GET /api/posts?limit=10
  Size: ~5KB (full post objects)

Request 2-11: GET /api/users/:id (for each author)
  Size: ~2KB total

Total: ~7KB, 11 requests
```

**GraphQL - Same Data:**
```graphql
query {
  posts(limit: 10) {
    title
    author { name }
  }
}

Total: ~1KB, 1 request
```

**Savings: ~86% less data, 90% fewer requests!**

---

## 7. Real-World Use Cases

### Use REST When:

1. **Simple CRUD Application**
   - Blog, CMS
   - Standard operations
   - Small team

2. **Public API**
   - Third-party developers
   - Need wide compatibility
   - Documentation important

3. **Caching Critical**
   - CDN usage
   - Static content
   - High traffic

4. **File Operations**
   - File uploads/downloads
   - Streaming

### Use GraphQL When:

1. **Complex Data Requirements**
   - E-commerce (products, categories, reviews)
   - Social media (posts, comments, likes, friends)
   - Analytics dashboards

2. **Multiple Client Types**
   - Web, iOS, Android
   - Different data needs
   - Rapid iteration

3. **Real-time Features**
   - Subscriptions
   - Live updates
   - Collaborative tools

4. **Developer Experience**
   - Type safety important
   - Self-documenting API
   - GraphQL playground

---

## 8. Decision Matrix

```
                    REST    GraphQL
Simplicity           ★★★★★   ★★★☆☆
Learning Curve       ★★★★★   ★★★☆☆
Flexibility          ★★★☆☆   ★★★★★
Performance          ★★★☆☆   ★★★★★
Caching              ★★★★★   ★★☆☆☆
Tooling              ★★★★★   ★★★★☆
Versioning           ★★★☆☆   ★★★★★
Real-time            ★★☆☆☆   ★★★★★
File Handling        ★★★★★   ★★★☆☆
Browser Support      ★★★★★   ★★★★★
```

---

## 9. Migration Strategy

### REST to GraphQL

**Option 1: GraphQL Gateway**
```
[Client] → [GraphQL Gateway] → [REST APIs]
                                (existing)
```
- Gradual migration
- GraphQL wraps REST
- No immediate changes to REST APIs

**Option 2: Parallel Implementation**
```
[Client] → [GraphQL] (new endpoints)
       → [REST]     (existing endpoints)
```
- Both available
- Migrate clients gradually
- Deprecate REST over time

**Option 3: Full Replacement**
```
[Client] → [GraphQL] (complete rewrite)
```
- Clean slate
- Breaking change
- Best long-term

---

## 10. Best Practices

### REST Best Practices

1. Use nouns for resources, not verbs
   - ✅ `/api/users`
   - ❌ `/api/getUsers`

2. Use HTTP methods correctly
   - GET: Read
   - POST: Create
   - PUT: Update/Replace
   - PATCH: Partial Update
   - DELETE: Remove

3. Version your API
   - `/api/v1/users`
   - Header: `Accept: application/vnd.api.v2+json`

4. Use proper status codes
   - 200: OK
   - 201: Created
   - 400: Bad Request
   - 404: Not Found
   - 500: Server Error

5. Implement pagination
   - `/api/posts?page=2&limit=20`

### GraphQL Best Practices

1. Design schema carefully
   - Think in graphs, not endpoints
   - One type per domain entity

2. Use DataLoader for batching
   - Prevents N+1 queries
   - Batches and caches

3. Implement pagination
   - Cursor-based (Relay)
   - Offset-based (simple)

4. Add field descriptions
   ```graphql
   type User {
     """The user's unique identifier"""
     id: ID!
   }
   ```

5. Use persisted queries
   - Reduce payload size
   - Better caching
   - Security

---

## Conclusion

**Choose REST if:**
- Building simple CRUD API
- Need HTTP caching
- Public API for wide consumption
- Team familiar with REST

**Choose GraphQL if:**
- Complex data relationships
- Multiple client types
- Real-time features needed
- Want flexibility and type safety

**Both are valid choices!** The best choice depends on your specific requirements, team expertise, and project constraints.
