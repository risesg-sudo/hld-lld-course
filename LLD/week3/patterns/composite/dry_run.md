# Dry Run: Composite Pattern

## Operation: Calculate Directory Size

Structure:
```
root/
├── Documents/
│   ├── resume.pdf (512000 bytes)
│   └── cover_letter.docx (256000 bytes)
└── readme.txt (1024 bytes)
```

Call: `root.get_size()`

### Execution Trace

**Level 1**: `root.get_size()`
```
sum(child.get_size() for child in self.children)
Children: [Documents, readme.txt]

Call child[0].get_size() → Documents.get_size()
  **Level 2**: Documents.get_size()
  Children: [resume.pdf, cover_letter.docx]
  
  Call child[0].get_size() → resume.pdf.get_size()
    **Level 3**: File.get_size()
    Return: 512000
  
  Call child[1].get_size() → cover_letter.docx.get_size()
    **Level 3**: File.get_size()
    Return: 256000
  
  Sum: 512000 + 256000 = 768000
  Return: 768000

Call child[1].get_size() → readme.txt.get_size()
  **Level 2**: File.get_size()
  Return: 1024

Sum: 768000 + 1024 = 769024
Return: 769024
```

**Final Result**: 769024 bytes

## Key: Uniform Recursion

`get_size()` called on:
- File: returns size (base case)
- Directory: sums children's get_size() (recursive case)

Client doesn't know or care whether component is file or directory. Same interface, different implementation. Recursion handles tree traversal automatically.
