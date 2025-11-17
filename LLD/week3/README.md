# LLD Week 3: Behavioral & Structural Design Patterns

## Overview

This directory contains refactored content for LLD Week 3, covering 8 essential design patterns split across behavioral and structural categories.

## Structure

Each pattern is organized in its own directory with three focused files:

```
patterns/
├── <pattern-name>/
│   ├── concept.md          # Theory, when to use, trade-offs (200-300 lines)
│   ├── <example>.py        # Focused, runnable example (50-150 lines)
│   └── dry_run.md          # Step-by-step execution trace (100-200 lines)
```

## Patterns Covered

### Behavioral Patterns

#### 1. Strategy Pattern
**Directory**: `/patterns/strategy/`
**Problem**: Eliminating conditional complexity for multiple algorithm variations
**Example**: Payment processing with credit card, PayPal, crypto
**Key Concept**: Encapsulate interchangeable algorithms

#### 2. Template Method Pattern
**Directory**: `/patterns/template/`
**Problem**: Reusing algorithm structure while varying implementation steps
**Example**: Data processing pipeline for CSV and JSON
**Key Concept**: Define skeleton, vary steps through inheritance

### Structural Patterns

#### 3. Adapter Pattern
**Directory**: `/patterns/adapter/`
**Problem**: Making incompatible interfaces work together
**Example**: Legacy payment system integration
**Key Concept**: Translate between interfaces

#### 4. Decorator Pattern
**Directory**: `/patterns/decorator/`
**Problem**: Adding behavior dynamically without subclass explosion
**Example**: Coffee shop with customizable add-ons
**Key Concept**: Wrap objects to add features

#### 5. Bridge Pattern
**Directory**: `/patterns/bridge/`
**Problem**: Avoiding Cartesian product class explosion
**Example**: Remote controls for different devices
**Key Concept**: Separate abstraction from implementation

#### 6. Composite Pattern
**Directory**: `/patterns/composite/`
**Problem**: Treating individuals and collections uniformly
**Example**: File system with files and directories
**Key Concept**: Tree structures with recursive composition

#### 7. Proxy Pattern
**Directory**: `/patterns/proxy/`
**Problem**: Controlling access and deferring expensive operations
**Example**: Lazy-loading images
**Key Concept**: Surrogate object for access control

#### 8. Facade Pattern
**Directory**: `/patterns/facade/`
**Problem**: Simplifying complex subsystem interfaces
**Example**: Home theater system coordination
**Key Concept**: Unified interface to complex subsystem

## How to Use This Content

### Learning Path

1. **Read concept.md** - Understand the problem and solution (10-15 min)
2. **Run example.py** - See the pattern in action (5 min)
3. **Study dry_run.md** - Trace execution step-by-step (10-15 min)

Total time per pattern: ~30 minutes

### Running Examples

All Python examples are standalone and runnable:

```bash
# Strategy pattern
python3 /home/user/hld-lld-course/LLD/week3/patterns/strategy/payment_strategies.py

# Template method
python3 /home/user/hld-lld-course/LLD/week3/patterns/template/data_processing.py

# Adapter pattern
python3 /home/user/hld-lld-course/LLD/week3/patterns/adapter/legacy_integration.py

# Decorator pattern
python3 /home/user/hld-lld-course/LLD/week3/patterns/decorator/coffee_shop.py

# Bridge pattern
python3 /home/user/hld-lld-course/LLD/week3/patterns/bridge/remote_control.py

# Composite pattern
python3 /home/user/hld-lld-course/LLD/week3/patterns/composite/file_system.py

# Proxy pattern
python3 /home/user/hld-lld-course/LLD/week3/patterns/proxy/image_loader.py

# Facade pattern
python3 /home/user/hld-lld-course/LLD/week3/patterns/facade/home_theater.py
```

## Content Philosophy

All content follows these principles:

- **No Emojis**: Professional, technical documentation
- **Curiosity-Driven**: Focus on "why" before "how"
- **Practical**: Real-world examples and trade-offs
- **Focused**: Each file under 300 lines, easily digestible
- **Progressive**: Simple concepts building to complex understanding
- **Executable**: All code examples are runnable and tested

## Quick Reference

| Pattern | Type | Main Use Case | Key Benefit |
|---------|------|---------------|-------------|
| Strategy | Behavioral | Algorithm variations | Runtime algorithm selection |
| Template Method | Behavioral | Fixed algorithm structure | Code reuse via inheritance |
| Adapter | Structural | Interface mismatch | Makes incompatible interfaces work |
| Decorator | Structural | Dynamic features | Avoids subclass explosion |
| Bridge | Structural | Multiple variation axes | Decouples abstraction from implementation |
| Composite | Structural | Tree structures | Uniform treatment of parts and wholes |
| Proxy | Structural | Access control | Lazy loading, protection |
| Facade | Structural | Complex subsystems | Simplified interface |

## Interview Preparation

Each pattern's concept.md includes:
- When to use vs when not to use
- Common pitfalls and anti-patterns
- Comparisons with similar patterns
- Real-world applications
- Trade-off analysis

## Files Inventory

**Total Files**: 24 (8 patterns × 3 files each)

- 8 `concept.md` files (~2,000 lines total)
- 8 Python example files (~800 lines total)
- 8 `dry_run.md` files (~1,200 lines total)

**Total Content**: ~4,000 lines of focused, high-quality documentation

## Related Content

- **Week 1**: OOP Fundamentals & SOLID Principles
- **Week 2**: Creational Patterns
- **Week 3**: Behavioral & Structural Patterns (you are here)
- **Week 4**: System Design Applications

## Contributing

When adding new examples or improving existing content:
1. Keep files under 300 lines
2. Maintain curiosity-driven tone
3. No emojis in documentation
4. Include dry runs for code examples
5. Test all Python examples before committing

## Summary

This refactored structure provides:
- **Clarity**: One pattern per directory
- **Focus**: Small, digestible files
- **Depth**: Concept + Example + Dry Run for each pattern
- **Practicality**: Runnable, tested code
- **Professionalism**: No emojis, explanatory style

Learn at your own pace, one pattern at a time.
