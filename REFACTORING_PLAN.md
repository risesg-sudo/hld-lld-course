# Refactoring Plan: System Design Course Materials

## Problem Statement

Current issues with the course materials:
1. Large files (1000-2000+ lines) are overwhelming
2. Multiple concepts clubbed together in single files
3. No step-by-step execution traces (dry runs)
4. Too many emojis making it less professional
5. Tone is celebratory rather than explanatory
6. Hard to grasp individual concepts quickly

## Solution Approach

### File Structure Changes

#### Before (Example - Week 2 LLD):
```
week2_creational_behavioral.md (469 lines - all 7 patterns)
builder_pattern.py (713 lines - 4 different builders)
```

#### After (Example - Week 2 LLD):
```
patterns/
  singleton/
    - concept.md (theory, when to use, trade-offs)
    - basic_singleton.py (single focused example)
    - thread_safe_singleton.py (another focused example)
    - dry_run.md (step-by-step execution trace)
  builder/
    - concept.md
    - pizza_builder.py (single example)
    - query_builder.py (single example)
    - dry_run.md
  ... (one directory per pattern)
```

### Content Guidelines

Each concept file should have:
1. **Hook** - Start with an interesting question or problem (100-150 words)
2. **The Problem** - Why does this exist? What problem does it solve? (150-200 words)
3. **The Solution** - How it works conceptually (200-300 words)
4. **Code Example** - Single, focused example (50-100 lines)
5. **Dry Run** - Step-by-step execution trace showing what happens in memory
6. **When to Use** - Practical scenarios (100 words)
7. **Trade-offs** - What you gain, what you lose (100 words)

Total per file: 200-400 lines (easy to read in one sitting)

## Refactoring Breakdown

### LLD Week 1: OOP & SOLID Principles

Current: 1 large markdown + 15 Python files

New Structure:
```
LLD/week1/
  oop-fundamentals/
    encapsulation/
      - concept.md
      - bank_account.py
      - dry_run.md
    inheritance/
      - concept.md
      - vehicle_hierarchy.py
      - dry_run.md
    polymorphism/
      - concept.md
      - payment_methods.py
      - dry_run.md
    abstraction/
      - concept.md
      - database_abstraction.py
      - dry_run.md

  principles/
    dry-principle/
      - concept.md
      - example.py
      - dry_run.md
    kiss-principle/
      - concept.md
      - example.py
      - dry_run.md

  solid/
    single-responsibility/
      - concept.md
      - user_management.py
      - dry_run.md
    open-closed/
      - concept.md
      - discount_calculator.py
      - dry_run.md
    ... (5 SOLID principles)

  patterns/
    factory/
      - concept.md
      - vehicle_factory.py
      - dry_run.md
    abstract-factory/
      - concept.md
      - ui_factory.py
      - dry_run.md
```

### LLD Week 2: Creational & Behavioral Patterns

Split into 7 pattern directories, each with:
- concept.md
- 2-3 focused Python examples (one file each)
- dry_run.md for each example

### LLD Week 3: Structural Patterns

Split into 8 pattern directories with same structure

### LLD Week 4: System Designs

Current: 3 large system designs

New Structure:
```
LLD/week4/
  irctc-system/
    - overview.md (requirements, approach)
    - architecture.md (high-level design)
    - core/
      - train.py + dry_run.md
      - booking.py + dry_run.md
      - payment.py + dry_run.md
    - walkthrough.md (complete flow with trace)

  chess-game/
    - overview.md
    - architecture.md
    - pieces/
      - piece.py + dry_run.md
      - king.py + dry_run.md
      - ... (other pieces)
    - walkthrough.md

  elevator-system/
    - overview.md
    - architecture.md
    - components/
      - elevator.py + dry_run.md
      - controller.py + dry_run.md
      - scheduler.py + dry_run.md
    - walkthrough.md
```

### HLD Weeks: Similar Structure

Each concept in its own directory with:
- Theory file
- Focused implementation
- Dry run showing execution

## Dry Run Format

Example format for dry runs:

```markdown
# Dry Run: LRU Cache Implementation

## Initial State
```
cache = LRUCache(capacity=3)
cache_data = {}
order_list = []  # least recent -> most recent
```

## Operation 1: cache.put(1, "a")

Step 1: Check if key 1 exists
- Result: No

Step 2: Check if cache is full
- Current size: 0
- Capacity: 3
- Result: Not full

Step 3: Add to cache
```
cache_data = {1: "a"}
order_list = [1]
```

## Operation 2: cache.put(2, "b")

Step 1: Check if key 2 exists
- Result: No

Step 2: Add to cache
```
cache_data = {1: "a", 2: "b"}
order_list = [1, 2]
```

... and so on
```

## Writing Style Guidelines

### Remove:
- All emojis
- Celebratory language ("Perfect!", "Excellent!")
- Superlatives ("amazing", "awesome")

### Add:
- Curiosity-driven questions
- "Why" explanations before "how"
- Real-world analogies
- Trade-off discussions
- Progressive disclosure (simple -> complex)

### Example Transformation:

Before:
```
Perfect! The Singleton pattern is awesome! It ensures only one instance exists!
```

After:
```
What happens when two parts of your application try to create separate database
connections? You might end up with connection pool exhaustion. The Singleton
pattern addresses this by guaranteeing exactly one instance of a class exists
throughout your application's lifetime. But this convenience comes with trade-offs
worth understanding.
```

## Implementation Plan

1. Create parallel tasks for each week
2. Each subagent handles one week
3. Each subagent creates the new directory structure
4. Each subagent splits files and adds dry runs
5. Each subagent ensures no emojis, professional tone
6. Final step: Update main README with new navigation

## Success Criteria

- No file larger than 400 lines
- Every code example has a corresponding dry run
- No emojis in any file
- Tone is explanatory and curiosity-driven
- Easy to navigate from concept to concept
- Each concept can be understood in 10-15 minutes of reading
