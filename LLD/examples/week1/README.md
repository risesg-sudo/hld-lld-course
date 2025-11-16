# LLD Week 1 - Python Examples and UML Diagrams

A comprehensive collection of Python examples demonstrating design principles and patterns for Low-Level Design (LLD) Week 1.

## Quick Start

Run any example with:
```bash
python3 <filename>.py
```

## Files Overview

### Design Principles (DRY, KISS, SOLID)

| File | Topic | Focus | Lines |
|------|-------|-------|-------|
| `dry_principle.py` | DRY Principle | Code reuse, avoiding duplication | ~280 |
| `kiss_principle.py` | KISS Principle | Simplicity over complexity | ~360 |
| `srp_example.py` | Single Responsibility | Separation of concerns | ~420 |
| `ocp_example.py` | Open/Closed Principle | Extension without modification | ~440 |
| `lsp_example.py` | Liskov Substitution | Correct inheritance | ~450 |
| `isp_example.py` | Interface Segregation | Focused interfaces | ~460 |
| `dip_example.py` | Dependency Inversion | Abstraction dependencies | ~450 |

### Design Patterns

| File | Pattern | Use Case | Lines |
|------|---------|----------|-------|
| `factory_pattern.py` | Factory Pattern | Object creation | ~480 |
| `abstract_factory_pattern.py` | Abstract Factory | Family of objects | ~510 |

### Documentation

| File | Purpose | Content |
|------|---------|---------|
| `uml_examples.md` | UML Reference | 10+ ASCII diagrams, relationship guide |

## File Structure

Each Python file contains:

1. **Docstring**: Core concept explanation
2. **Bad Example**: Anti-pattern showing common mistakes
3. **Good Example**: Best practice implementation
4. **Real-World Example**: Practical use case
5. **Demo Functions**: Runnable examples with output
6. **Key Takeaways**: Summary of lessons learned

## Learning Path

### Beginner
1. Start with `dry_principle.py` and `kiss_principle.py`
2. Understand the basics of code quality
3. Review `uml_examples.md` for visual understanding

### Intermediate
4. Learn `srp_example.py` - break code into focused classes
5. Study `ocp_example.py` - design for extension
6. Master `dip_example.py` - loose coupling through abstractions

### Advanced
7. Explore `lsp_example.py` - proper inheritance design
8. Practice `isp_example.py` - interface design
9. Implement `factory_pattern.py` - object creation
10. Build with `abstract_factory_pattern.py` - complex systems

## Running All Examples

```bash
#!/bin/bash
cd /home/user/hld-lld-course/LLD/examples/week1/

# Run all principle examples
python3 dry_principle.py
python3 kiss_principle.py
python3 srp_example.py
python3 ocp_example.py
python3 lsp_example.py
python3 isp_example.py
python3 dip_example.py

# Run pattern examples
python3 factory_pattern.py
python3 abstract_factory_pattern.py
```

## Key Concepts Covered

### SOLID Principles
- **S**ingle Responsibility: One reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Correct inheritance hierarchies
- **I**nterface Segregation: Specific interfaces for clients
- **D**ependency Inversion: Depend on abstractions

### Design Patterns
- **Factory Pattern**: Centralize object creation
- **Abstract Factory**: Create families of objects
- **Strategy Pattern**: Interchangeable algorithms (in OCP)
- **Dependency Injection**: Inject dependencies from outside (in DIP)

### General Principles
- **DRY** (Don't Repeat Yourself): Single source of truth
- **KISS** (Keep It Simple, Stupid): Simplicity first

## UML Diagrams

See `uml_examples.md` for:
- Class diagram notation
- Inheritance relationships (IS-A)
- Composition relationships (HAS-A, strong)
- Aggregation relationships (HAS-A, weak)
- Dependency relationships
- Visual representations of all patterns

## Real-World Examples

Each file includes practical scenarios:
- User management systems
- E-commerce platforms
- Payment processing
- Database operations
- UI frameworks
- Logging systems
- Notification systems

## Code Quality

All examples follow:
- PEP 8 Python style guide
- Clear variable naming
- Comprehensive comments
- Proper type hints (where applicable)
- Pythonic idioms
- Best practices

## Common Mistakes to Avoid

- Repeating code instead of extracting it (DRY violation)
- Over-engineering solutions (KISS violation)
- Classes doing too much (SRP violation)
- Modifying classes for new features (OCP violation)
- Breaking contracts in subclasses (LSP violation)
- Fat interfaces (ISP violation)
- Depending on concrete classes (DIP violation)

## Further Reading

### Concepts to Explore
- Design patterns from "Gang of Four" book
- Software architecture principles
- Test-driven development (TDD)
- Refactoring techniques
- System design interview preparation

### Related Topics
- Object-oriented programming fundamentals
- Python advanced features
- Design philosophy and trade-offs
- Code review practices
- Documentation standards

## Tips for Learning

1. **Run the code**: Execute examples to see output
2. **Read comments**: Understand the "why" not just "what"
3. **Study differences**: Compare bad vs. good implementations
4. **Draw diagrams**: Visualize relationships using UML
5. **Modify examples**: Try adding new features to understand principles
6. **Create analogs**: Map real-world scenarios to patterns
7. **Review key takeaways**: Summarize learning after each file
8. **Teach others**: Explain concepts to deepen understanding

## Quick Reference

### When to use each principle/pattern:

| Principle/Pattern | When to Use |
|-------------------|------------|
| DRY | See repeated code → extract to function |
| KISS | Multiple ways to solve → choose simplest |
| SRP | Class has multiple reasons to change → split it |
| OCP | Adding features breaks existing code → use polymorphism |
| LSP | Subclass has different behavior → check inheritance |
| ISP | Classes implement unused methods → split interface |
| DIP | Tight coupling to concrete classes → use abstraction |
| Factory | Many classes with similar creation → centralize |
| Abstract Factory | Groups of related objects → create families |

## File Locations

```
/home/user/hld-lld-course/LLD/examples/week1/
├── dry_principle.py
├── kiss_principle.py
├── srp_example.py
├── ocp_example.py
├── lsp_example.py
├── isp_example.py
├── dip_example.py
├── factory_pattern.py
├── abstract_factory_pattern.py
├── uml_examples.md
└── README.md (this file)
```

## Statistics

- **Total Lines**: 5,493
- **Total Size**: 178 KB
- **Python Files**: 9
- **Documentation**: 1 (UML + README)
- **Code Examples**: 40+
- **Real-world scenarios**: 15+
- **UML Diagrams**: 15+

## Author Notes

These examples are designed for:
- LLD course students
- Interview preparation
- Design review references
- Teaching tool
- Quick lookup guide

Each example is self-contained and can be studied independently, though following the suggested learning path will provide better context and understanding.

---

**Last Updated**: 2024-01-15
**Status**: Complete and tested
**Python Version**: 3.7+
