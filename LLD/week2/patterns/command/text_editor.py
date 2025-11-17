"""
Text Editor with Undo/Redo using Command Pattern
"""

from abc import ABC, abstractmethod
from collections import deque


class Command(ABC):
    """Abstract command interface."""
    
    @abstractmethod
    def execute(self):
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self):
        """Undo the command."""
        pass


class TextDocument:
    """Document being edited (receiver)."""
    
    def __init__(self):
        self.text = ""
    
    def insert(self, text: str, position: int):
        """Insert text at position."""
        self.text = self.text[:position] + text + self.text[position:]
        print(f"Inserted '{text}' at position {position}")
    
    def delete(self, start: int, end: int) -> str:
        """Delete text and return what was deleted."""
        deleted = self.text[start:end]
        self.text = self.text[:start] + self.text[end:]
        print(f"Deleted '{deleted}' from position {start}")
        return deleted


class InsertCommand(Command):
    """Command to insert text."""
    
    def __init__(self, document: TextDocument, text: str, position: int):
        self.document = document
        self.text = text
        self.position = position
    
    def execute(self):
        """Insert text."""
        self.document.insert(self.text, self.position)
    
    def undo(self):
        """Remove inserted text."""
        start = self.position
        end = self.position + len(self.text)
        self.document.delete(start, end)


class DeleteCommand(Command):
    """Command to delete text."""
    
    def __init__(self, document: TextDocument, start: int, end: int):
        self.document = document
        self.start = start
        self.end = end
        self.deleted_text = ""
    
    def execute(self):
        """Delete text and save it for undo."""
        self.deleted_text = self.document.delete(self.start, self.end)
    
    def undo(self):
        """Restore deleted text."""
        self.document.insert(self.deleted_text, self.start)


class TextEditor:
    """Editor with undo/redo support."""
    
    def __init__(self):
        self.document = TextDocument()
        self.history = deque(maxlen=50)
        self.current_pos = 0
    
    def execute_command(self, command: Command):
        """Execute command and add to history."""
        command.execute()
        self.history.append(command)
        self.current_pos = len(self.history)
    
    def undo(self):
        """Undo last command."""
        if self.current_pos > 0:
            self.current_pos -= 1
            command = list(self.history)[self.current_pos]
            command.undo()
            print("Undo executed")
    
    def redo(self):
        """Redo last undone command."""
        if self.current_pos < len(self.history):
            command = list(self.history)[self.current_pos]
            command.execute()
            self.current_pos += 1
            print("Redo executed")


def demonstrate():
    """Demonstrate command pattern with undo/redo."""
    print("="*70)
    print("TEXT EDITOR WITH UNDO/REDO")
    print("="*70)
    
    editor = TextEditor()
    
    print("\n1. Typing 'Hello':")
    editor.execute_command(InsertCommand(editor.document, "Hello", 0))
    print(f"   Text: '{editor.document.text}'")
    
    print("\n2. Typing ' World':")
    editor.execute_command(InsertCommand(editor.document, " World", 5))
    print(f"   Text: '{editor.document.text}'")
    
    print("\n3. Undo (remove ' World'):")
    editor.undo()
    print(f"   Text: '{editor.document.text}'")
    
    print("\n4. Redo (add ' World' back):")
    editor.redo()
    print(f"   Text: '{editor.document.text}'")


if __name__ == "__main__":
    demonstrate()
    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Each edit operation is a command object
2. Commands know how to execute and undo themselves
3. History stack stores executed commands
4. Undo: call undo() on previous command
5. Redo: call execute() again
    """)
