# Dry Run: Abstract Factory Pattern

## Creating Windows Application

```python
app = Application(WindowsFactory())
```

### Execution Steps

**Step 1**: WindowsFactory passed to Application

**Step 2**: Create button
- Calls factory.create_button()
- Returns WindowsButton()

**Step 3**: Create checkbox
- Calls factory.create_checkbox()
- Returns WindowsCheckbox()

**Result**: All components are Windows-style

### Switching to Mac

```python
app = Application(MacFactory())
```

**Same steps, different family**:
- MacFactory creates MacButton and MacCheckbox
- All components match Mac style

## Benefits

1. **Consistency**: All components from same family
2. **Easy Switch**: Change factory, change everything
3. **No Mixing**: Cannot accidentally mix Windows and Mac

Abstract Factory ensures related objects work together consistently.
