"""
Document Cloning with Prototype Pattern

Demonstrates shallow vs deep copy and when to use each.
"""

import copy
from datetime import datetime
from typing import Dict, List, Any


class Document:
    """
    Document that can be cloned.
    
    Demonstrates deep copying to avoid shared state issues.
    """
    
    def __init__(self, title: str, content: str, metadata: Dict[str, Any]):
        self.title = title
        self.content = content
        self.metadata = metadata
        self.sections = []
        self.created_at = datetime.now()
    
    def add_section(self, section_title: str, section_content: str):
        """Add a section to the document."""
        self.sections.append({
            "title": section_title,
            "content": section_content
        })
    
    def deep_clone(self) -> "Document":
        """Create a deep copy of this document."""
        return copy.deepcopy(self)
    
    def shallow_clone(self) -> "Document":
        """Create a shallow copy (WARNING: shares nested objects)."""
        return copy.copy(self)
    
    def __str__(self):
        return f"Document('{self.title}', {len(self.sections)} sections)"


def demonstrate_shallow_vs_deep():
    """Show the difference between shallow and deep copy."""
    print("="*70)
    print("SHALLOW VS DEEP COPY")
    print("="*70)
    
    # Create original document
    original = Document(
        title="Original Report",
        content="Content here",
        metadata={"author": "Alice", "version": "1.0"}
    )
    original.add_section("Introduction", "Intro text")
    
    # Shallow copy
    print("\n1. Creating shallow copy:")
    shallow = original.shallow_clone()
    print(f"   Original: {original}")
    print(f"   Shallow:  {shallow}")
    print(f"   Same metadata dict? {original.metadata is shallow.metadata}")
    
    # Modify shallow copy's metadata
    print("\n2. Modifying shallow copy's metadata:")
    shallow.metadata["version"] = "2.0"
    print(f"   Original version: {original.metadata['version']}")
    print(f"   Shallow version:  {shallow.metadata['version']}")
    print("   WARNING: Original affected! (shared reference)")
    
    # Deep copy
    print("\n3. Creating deep copy:")
    deep = original.deep_clone()
    deep.metadata["version"] = "3.0"
    print(f"   Original version: {original.metadata['version']}")
    print(f"   Deep version:     {deep.metadata['version']}")
    print("   SUCCESS: Original not affected! (separate copy)")


if __name__ == "__main__":
    demonstrate_shallow_vs_deep()
    
    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Shallow copy shares nested objects (dangerous!)
2. Deep copy creates independent copies (safe)
3. Use copy.deepcopy() for complete independence
4. Python's copy module handles circular references
    """)
