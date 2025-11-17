# System Design Course - Complete Revision Guide

This repository contains comprehensive revision materials for a 10-week System Design course covering both Low-Level Design (LLD) and High-Level Design (HLD). The content has been carefully structured into focused, digestible modules with step-by-step execution traces.

## Quick Start - Learning Management System (LMS)

The best way to learn this course is through the custom-built web-based LMS with progress tracking, YouTube videos, and interactive features.

### Start the LMS in 2 Commands

```bash
cd lms
./setup_all.sh      # One-time setup
./start_lms.sh      # Start the LMS
```

Then open **http://localhost:3000** in your browser.

### LMS Features

- **Progress Tracking**: Track completion, time spent, and learning streaks
- **116 YouTube Videos**: Curated reference videos from top channels
- **31 Lessons**: 17h 48m of content with automatic time estimates
- **Auto-Save Notes**: Take notes that save automatically
- **Bookmarks**: Mark favorite lessons
- **Dark Mode**: Easy on the eyes
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Search & Filter**: Find lessons quickly

See [lms/README.md](./lms/README.md) for complete LMS documentation.

## What Makes This Different

Every concept in this guide follows a consistent approach:
- **Problem First**: Understand why something exists before learning how it works
- **Focused Content**: No file exceeds 400 lines - each module covers one concept thoroughly
- **Execution Traces**: Dry runs show exactly what happens in memory, step by step
- **Professional Tone**: Clear explanations without unnecessary embellishments
- **Practical Examples**: Real-world scenarios with runnable Python code

## Course Organization

### Low-Level Design (LLD) - 5 Weeks

#### Week 1: Object-Oriented Programming Fundamentals
Understanding the building blocks of object-oriented design.

```
LLD/week1/
├── oop-fundamentals/
│   ├── encapsulation/    - Protecting data and controlling access
│   ├── inheritance/      - Code reuse through hierarchies
│   ├── polymorphism/     - Multiple forms of the same interface
│   └── abstraction/      - Hiding complexity behind simple interfaces
├── principles/
│   ├── dry-principle/    - Don't Repeat Yourself
│   └── kiss-principle/   - Keep It Simple, Stupid
├── solid/
│   ├── single-responsibility/
│   ├── open-closed/
│   ├── liskov-substitution/
│   ├── interface-segregation/
│   └── dependency-inversion/
└── patterns/
    ├── factory/
    └── abstract-factory/
```

Each concept includes:
- `concept.md` - Theory with real-world motivation
- `example.py` - Focused, runnable code
- `dry_run.md` - Step-by-step execution trace

#### Week 2: Creational & Behavioral Patterns
How objects are created and how they interact.

```
LLD/week2/patterns/
├── singleton/           - Ensuring single instance
├── builder/            - Constructing complex objects step by step
├── prototype/          - Cloning objects efficiently
├── observer/           - Notifying dependents of state changes
├── command/            - Encapsulating requests as objects
├── chain-of-responsibility/  - Passing requests along a handler chain
└── iterator/           - Accessing elements sequentially
```

#### Week 3: Behavioral & Structural Patterns
Algorithms and object composition patterns.

```
LLD/week3/patterns/
├── strategy/           - Interchangeable algorithms
├── template/           - Defining algorithm skeleton
├── adapter/            - Making incompatible interfaces work together
├── decorator/          - Adding responsibilities dynamically
├── bridge/             - Separating abstraction from implementation
├── composite/          - Tree structures for part-whole hierarchies
├── proxy/              - Controlling access to objects
└── facade/             - Simplified interface to complex subsystems
```

#### Week 4: System Design Examples
Complete end-to-end system implementations.

```
LLD/week4/
├── irctc-system/       - Railway reservation with concurrency
│   ├── overview.md
│   ├── architecture.md
│   ├── components/
│   └── walkthrough.md
├── chess-game/         - Complete chess with move validation
│   ├── overview.md
│   ├── architecture.md
│   ├── pieces/
│   └── walkthrough.md
└── elevator-system/    - Multi-elevator scheduling
    ├── overview.md
    ├── architecture.md
    ├── components/
    └── walkthrough.md
```

#### Week 5: Advanced System Designs
Complex systems requiring multiple patterns.

```
LLD/week5/
├── recommendation-system/
│   ├── overview.md
│   ├── architecture.md
│   ├── algorithms/
│   └── walkthrough.md
└── meeting-scheduler/
    ├── overview.md
    ├── architecture.md
    ├── components/
    └── walkthrough.md
```

### High-Level Design (HLD) - 5 Weeks

#### Week 1: Networking & Protocols
Understanding how distributed systems communicate.

```
HLD/week1/
├── client-server/      - Basic networking architecture
├── protocols/
│   ├── http/          - Request-response protocol
│   ├── websockets/    - Full-duplex communication
│   ├── sse/           - Server-Sent Events
│   └── grpc/          - High-performance RPC
└── architectures/
    ├── monolith-vs-microservices/
    └── rest-vs-graphql/
```

#### Week 2: Scaling, Caching & Distribution
Handling growth and improving performance.

```
HLD/week2/
├── fundamentals/
│   ├── latency-throughput/
│   ├── consistency-availability/
│   └── cap-theorem/
├── load-balancing/
│   ├── round-robin/
│   ├── least-connections/
│   └── consistent-hashing/
├── caching/
│   ├── strategies/
│   │   ├── cache-aside/
│   │   └── write-through/
│   └── eviction/
│       ├── lru/
│       └── lfu/
└── messaging/
    ├── pubsub/
    └── kafka/
```

#### Week 3: Storage & Databases
Persisting and querying data at scale.

```
HLD/week3/
├── database-types/
│   ├── sql/
│   ├── nosql/
│   └── comparison.md
├── indexing/
│   ├── btree/
│   ├── hash/
│   └── bitmap/
├── replication/
│   ├── master-slave/
│   └── master-master/
├── sharding/
│   ├── range-based/
│   ├── hash-based/
│   └── geo-based/
└── consistent-hashing/
```

#### Week 4: APIs, Security & Reliability
Building robust, secure systems.

```
HLD/week4/
├── capacity-estimation/
│   └── examples/
├── communication-patterns/
│   ├── polling/
│   ├── streaming/
│   └── comparison.md
├── rate-limiting/
│   ├── token-bucket/
│   ├── leaky-bucket/
│   └── sliding-window/
├── fault-tolerance/
│   └── circuit-breaker/
└── security/
    ├── authentication/
    └── api-design/
```

#### Week 5: Real-World System Designs
Industry-scale architectures explained.

```
HLD/week5/
├── whatsapp/           - 2B users, real-time messaging
│   ├── overview.md
│   ├── architecture.md
│   ├── components/
│   ├── capacity-estimation.md
│   └── trade-offs.md
├── youtube/            - Video streaming at global scale
├── uber/               - Geospatial matching in real-time
├── stock-trading/      - Ultra-low latency systems
└── interview-guide/
    ├── approach-framework.md
    ├── common-questions.md
    └── company-specific-tips.md
```

## How to Use This Guide

### Option 1: Use the LMS (Recommended)

The interactive Learning Management System provides the best learning experience:

```bash
cd lms
./setup_all.sh
./start_lms.sh
```

Features:
- Progress tracking with completion percentages
- Time estimates for each lesson
- 116 curated YouTube reference videos
- Auto-save notes
- Bookmarks for important lessons
- Search and filter functionality
- Dark mode support

### Option 2: Browse Markdown Files

For self-study without the LMS:

1. **Start with the concept**: Read `concept.md` to understand the problem being solved
2. **Study the code**: Examine `example.py` to see the solution in action
3. **Trace execution**: Follow `dry_run.md` to understand how it works internally
4. **Experiment**: Modify the examples and observe the changes

### For Interview Preparation

The content is organized to mirror common interview progressions:
- **Week 1-3 LLD**: Pattern recognition and application
- **Week 4-5 LLD**: Complete system design
- **Week 1-4 HLD**: Fundamental concepts and trade-offs
- **Week 5 HLD**: Full system design interviews

### Navigation Tips

Each week has a README.md that provides:
- Overview of concepts covered
- Recommended learning order
- Links to all modules
- Time estimates for each section

## Running the Examples

All Python examples are self-contained and can be run directly:

```bash
# LLD Examples
python LLD/week1/oop-fundamentals/encapsulation/example.py
python LLD/week2/patterns/singleton/basic_example.py
python LLD/week4/irctc-system/components/train.py

# HLD Examples
python HLD/week1/client-server/tcp_example.py
python HLD/week2/caching/eviction/lru/example.py
```

## Content Statistics

- **Total Files**: 250+ focused modules
- **Lines of Code**: 90,000+ lines of Python and documentation
- **Design Patterns**: 30+ patterns with implementations
- **System Designs**: 10+ complete systems
- **Dry Runs**: Step-by-step traces for every major concept
- **YouTube Videos**: 116 curated educational videos
- **Total Learning Time**: 17h 48m of content

## LMS Technology Stack

The LMS is built with modern web technologies:

**Backend:**
- Flask (Python web framework)
- SQLite (Database)
- REST API with 18 endpoints

**Frontend:**
- Next.js 14 (React framework)
- TypeScript (Type safety)
- Tailwind CSS (Styling)
- shadcn/ui (UI components)
- Chart.js (Progress visualization)

## Learning Path

### Beginner Track (Weeks 1-4)
Start with LLD Week 1 to build OOP fundamentals, then move through the patterns in Weeks 2-3. After that, study HLD Weeks 1-2 for distributed systems basics.

### Intermediate Track (Weeks 5-7)
Focus on LLD Week 4 system designs and HLD Weeks 3-4 for database and API concepts.

### Advanced Track (Weeks 8-10)
Master LLD Week 5 advanced designs and HLD Week 5 real-world architectures. Practice explaining trade-offs.

## YouTube Videos

116 curated videos from top educational channels:

- **ByteByteGo** (18 videos) - System design interviews
- **Gaurav Sen** (30 videos) - Distributed systems
- **Hussein Nasser** (16 videos) - Backend engineering
- **freeCodeCamp** (10 videos) - Comprehensive tutorials
- **Programming with Mosh** (6 videos) - OOP concepts
- **ArjanCodes** (13 videos) - Design patterns in Python
- **Tech Dummies** (13 videos) - System design fundamentals
- **System Design Interview** (4 videos) - Interview preparation

Videos are integrated into the LMS and cover all major topics.

## Repository Structure

```
.
├── LLD/                  # Low-Level Design content
│   ├── week1/           # OOP & SOLID
│   ├── week2/           # Creational & Behavioral patterns
│   ├── week3/           # Structural patterns
│   ├── week4/           # System design examples
│   └── week5/           # Advanced designs
├── HLD/                  # High-Level Design content
│   ├── week1/           # Networking & Protocols
│   ├── week2/           # Scaling & Caching
│   ├── week3/           # Databases & Storage
│   ├── week4/           # APIs & Security
│   └── week5/           # Real-world systems
└── lms/                  # Learning Management System
    ├── backend/         # Flask API + SQLite
    ├── frontend/        # Next.js application
    ├── setup_all.sh     # One-command setup
    ├── start_lms.sh     # Start both servers
    └── README.md        # LMS documentation
```

## Additional Resources

- `lms/README.md` - Complete LMS documentation
- `lms/QUICK_START.md` - Quick start guide for LMS
- `REFACTORING_PLAN.md` - Details about the content organization approach
- Each week's README.md - Week-specific learning guides
- `**/dry_run.md` files - Detailed execution traces

## Getting Started

### Using the LMS (Recommended)

```bash
cd lms
./setup_all.sh      # First time setup
./start_lms.sh      # Start the LMS
```

Open **http://localhost:3000** in your browser and start learning!

### Reading Markdown Files

Begin your journey with [LLD Week 1: Object-Oriented Fundamentals](./LLD/week1/).

The first concept to explore is [Encapsulation](./LLD/week1/oop-fundamentals/encapsulation/concept.md), which introduces the idea of protecting data and controlling how it's accessed. This fundamental concept appears throughout software design, from simple classes to entire distributed systems.

## Contributing

This content follows specific guidelines:
- Files are kept under 400 lines for readability
- Every code example has an execution trace
- Tone is explanatory and curiosity-driven
- No unnecessary embellishments in the documentation

## License

Educational content for System Design learning.
