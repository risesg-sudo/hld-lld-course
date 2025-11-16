"""
Command Pattern - Encapsulate a request as an object.

This module demonstrates various command implementations:
1. Simple command pattern with receiver
2. Text editor with undo/redo
3. Smart home automation with queued commands
4. Command macros (composite commands)
5. Reversible commands with rollback
6. Async command execution
7. Command logging and replay

Key Learning Points:
- Command encapsulates request as an object
- Enables undo/redo functionality
- Decouples invoker from receiver
- Allows queuing, scheduling, and logging of requests
- Composite commands group multiple commands
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import deque
import time


# ============================================================================
# 1. SIMPLE COMMAND PATTERN
# ============================================================================

class Command(ABC):
    """Abstract base class for all commands."""

    @abstractmethod
    def execute(self):
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self):
        """Undo the command (optional)."""
        pass


class Light:
    """
    Receiver - object that performs actual work.
    """

    def __init__(self, location: str):
        self.location = location
        self.is_on = False

    def turn_on(self):
        """Turn on the light."""
        self.is_on = True
        print(f"Light at {self.location} is ON")

    def turn_off(self):
        """Turn off the light."""
        self.is_on = False
        print(f"Light at {self.location} is OFF")

    def __str__(self):
        status = "ON" if self.is_on else "OFF"
        return f"Light({self.location}, {status})"


class LightOnCommand(Command):
    """Concrete command to turn on light."""

    def __init__(self, light: Light):
        self.light = light

    def execute(self):
        """Turn on light."""
        self.light.turn_on()

    def undo(self):
        """Turn off light to undo."""
        self.light.turn_off()


class LightOffCommand(Command):
    """Concrete command to turn off light."""

    def __init__(self, light: Light):
        self.light = light

    def execute(self):
        """Turn off light."""
        self.light.turn_off()

    def undo(self):
        """Turn on light to undo."""
        self.light.turn_on()


class RemoteControl:
    """
    Invoker - asks command to execute.

    Doesn't know details of receiver or command implementation.
    """

    def __init__(self):
        self._command = None

    def set_command(self, command: Command):
        """Set command to execute."""
        self._command = command

    def press_button(self):
        """Press remote button (execute command)."""
        if self._command:
            self._command.execute()

    def press_undo(self):
        """Press undo button."""
        if self._command:
            self._command.undo()


# ============================================================================
# 2. TEXT EDITOR WITH UNDO/REDO
# ============================================================================

class TextDocument:
    """
    Document being edited - receiver.
    """

    def __init__(self):
        self.text = ""
        self.cursor_pos = 0

    def insert(self, text: str, pos: Optional[int] = None):
        """Insert text at position."""
        if pos is None:
            pos = len(self.text)
        self.text = self.text[:pos] + text + self.text[pos:]
        print(f"Inserted '{text}' at position {pos}")

    def delete(self, start: int, end: int) -> str:
        """Delete text between start and end."""
        deleted = self.text[start:end]
        self.text = self.text[:start] + self.text[end:]
        print(f"Deleted '{deleted}' from position {start}")
        return deleted

    def replace(self, start: int, end: int, text: str):
        """Replace text between start and end."""
        deleted = self.delete(start, end)
        self.insert(text, start)
        return deleted

    def __str__(self):
        return f"Document: '{self.text}'"


class InsertCommand(Command):
    """Command to insert text."""

    def __init__(self, document: TextDocument, text: str, pos: int):
        self.document = document
        self.text = text
        self.pos = pos

    def execute(self):
        """Insert text."""
        self.document.insert(self.text, self.pos)

    def undo(self):
        """Remove inserted text."""
        start = self.pos
        end = self.pos + len(self.text)
        self.document.delete(start, end)


class DeleteCommand(Command):
    """Command to delete text."""

    def __init__(self, document: TextDocument, start: int, end: int):
        self.document = document
        self.start = start
        self.end = end
        self.deleted_text = ""

    def execute(self):
        """Delete text."""
        self.deleted_text = self.document.delete(self.start, self.end)

    def undo(self):
        """Restore deleted text."""
        self.document.insert(self.deleted_text, self.start)


class ReplaceCommand(Command):
    """Command to replace text."""

    def __init__(self, document: TextDocument, start: int, end: int, text: str):
        self.document = document
        self.start = start
        self.end = end
        self.new_text = text
        self.old_text = ""

    def execute(self):
        """Replace text."""
        self.old_text = self.document.replace(self.start, self.end, self.new_text)

    def undo(self):
        """Restore original text."""
        self.document.replace(self.start, self.start + len(self.new_text), self.old_text)


class TextEditor:
    """
    Text editor with undo/redo support.

    Maintains history of commands.
    """

    def __init__(self):
        self.document = TextDocument()
        self.history: deque = deque(maxlen=50)  # Keep last 50 commands
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
        else:
            print("Nothing to undo")

    def redo(self):
        """Redo last undone command."""
        if self.current_pos < len(self.history):
            command = list(self.history)[self.current_pos]
            command.execute()
            self.current_pos += 1
            print("Redo executed")
        else:
            print("Nothing to redo")

    def get_text(self):
        """Get current document text."""
        return self.document.text

    def insert(self, text: str):
        """Insert text at end."""
        cmd = InsertCommand(self.document, text, len(self.document.text))
        self.execute_command(cmd)

    def delete(self, start: int, end: int):
        """Delete text."""
        cmd = DeleteCommand(self.document, start, end)
        self.execute_command(cmd)

    def replace(self, start: int, end: int, text: str):
        """Replace text."""
        cmd = ReplaceCommand(self.document, start, end, text)
        self.execute_command(cmd)


# ============================================================================
# 3. SMART HOME AUTOMATION
# ============================================================================

class Device:
    """Smart home device."""

    def __init__(self, name: str):
        self.name = name
        self.is_on = False

    def turn_on(self):
        """Turn on device."""
        self.is_on = True
        print(f"  {self.name} turned ON")

    def turn_off(self):
        """Turn off device."""
        self.is_on = False
        print(f"  {self.name} turned OFF")


class DeviceCommand(ABC):
    """Abstract command for device control."""

    @abstractmethod
    def execute(self):
        """Execute command."""
        pass


class TurnOnCommand(DeviceCommand):
    """Turn on device."""

    def __init__(self, device: Device):
        self.device = device

    def execute(self):
        """Execute turn on."""
        self.device.turn_on()

    def __str__(self):
        return f"TurnOn({self.device.name})"


class TurnOffCommand(DeviceCommand):
    """Turn off device."""

    def __init__(self, device: Device):
        self.device = device

    def execute(self):
        """Execute turn off."""
        self.device.turn_off()

    def __str__(self):
        return f"TurnOff({self.device.name})"


class Thermostat(Device):
    """Thermostat device."""

    def __init__(self, name: str):
        super().__init__(name)
        self.temperature = 20

    def set_temperature(self, temp: float):
        """Set temperature."""
        self.temperature = temp
        print(f"  {self.name} set to {temp}°C")


class SetTemperatureCommand(DeviceCommand):
    """Set thermostat temperature."""

    def __init__(self, thermostat: Thermostat, temperature: float):
        self.thermostat = thermostat
        self.temperature = temperature
        self.previous_temperature = 0

    def execute(self):
        """Set temperature."""
        self.previous_temperature = self.thermostat.temperature
        self.thermostat.set_temperature(self.temperature)

    def __str__(self):
        return f"SetTemp({self.thermostat.name}, {self.temperature}°C)"


class CommandScheduler:
    """
    Schedules commands to execute at specific times.

    Useful for home automation - schedule lights to turn on/off at specific times.
    """

    def __init__(self):
        self.scheduled_commands: List[tuple] = []
        self.executed_count = 0

    def schedule(self, delay_seconds: float, command: DeviceCommand):
        """Schedule command to execute after delay."""
        self.scheduled_commands.append((delay_seconds, command))
        print(f"Scheduled: {command} (in {delay_seconds}s)")

    def execute_all(self):
        """Execute all scheduled commands."""
        print("\nExecuting scheduled commands:")
        for delay, command in self.scheduled_commands:
            # In real app, would use threading/async
            print(f"Executing in {delay}s: {command}")
            command.execute()
            self.executed_count += 1

    def get_pending_count(self):
        """Get count of pending commands."""
        return len(self.scheduled_commands)


# ============================================================================
# 4. COMPOSITE COMMANDS (Macros)
# ============================================================================

class CompositeCommand(Command):
    """
    Composite command - combines multiple commands.

    Useful for macros: "Good Morning" macro turns on lights, coffee maker, etc.
    """

    def __init__(self, name: str):
        self.name = name
        self.commands: List[Command] = []

    def add_command(self, command: Command):
        """Add command to macro."""
        self.commands.append(command)

    def execute(self):
        """Execute all commands in sequence."""
        print(f"\nExecuting macro: {self.name}")
        for command in self.commands:
            command.execute()

    def undo(self):
        """Undo all commands in reverse order."""
        print(f"Undoing macro: {self.name}")
        for command in reversed(self.commands):
            command.undo()

    def __str__(self):
        return f"Macro({self.name}, {len(self.commands)} commands)"


# ============================================================================
# 5. COMMAND LOGGER AND REPLAY
# ============================================================================

class CommandLogger:
    """
    Logs all executed commands.

    Useful for:
    - Audit trails
    - Command replay/replay
    - Debugging
    """

    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def log_command(self, command: Command, result: str = "SUCCESS"):
        """Log command execution."""
        entry = {
            "timestamp": datetime.now(),
            "command": command.__class__.__name__,
            "result": result,
            "details": str(command)
        }
        self.log.append(entry)

    def get_logs(self) -> List[Dict]:
        """Get all logs."""
        return self.log.copy()

    def print_logs(self):
        """Print all logs."""
        print("\nCommand Log:")
        for entry in self.log:
            print(f"  [{entry['timestamp'].strftime('%H:%M:%S')}] "
                  f"{entry['command']}: {entry['details']}")


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def test_simple_command():
    """Test simple command pattern with remote control."""
    print("\n" + "="*70)
    print("TEST 1: SIMPLE COMMAND PATTERN - REMOTE CONTROL")
    print("="*70)

    # Create receiver
    light = Light("Living Room")

    # Create commands
    on_cmd = LightOnCommand(light)
    off_cmd = LightOffCommand(light)

    # Create invoker
    remote = RemoteControl()

    # Execute commands
    print("Turning light on:")
    remote.set_command(on_cmd)
    remote.press_button()

    print("\nUndoing (turning light off):")
    remote.press_undo()

    print("\nTurning light off:")
    remote.set_command(off_cmd)
    remote.press_button()


def test_text_editor():
    """Test text editor with undo/redo."""
    print("\n" + "="*70)
    print("TEST 2: TEXT EDITOR WITH UNDO/REDO")
    print("="*70)

    editor = TextEditor()

    print("Editing document:")
    editor.insert("Hello")
    print(f"Text: {editor.get_text()}")

    editor.insert(" World")
    print(f"Text: {editor.get_text()}")

    print("\nUndoing:")
    editor.undo()
    print(f"Text: {editor.get_text()}")

    print("\nRedoing:")
    editor.redo()
    print(f"Text: {editor.get_text()}")

    print("\nReplacing 'World' with 'Python':")
    editor.replace(6, 11, "Python")
    print(f"Text: {editor.get_text()}")

    print("\nUndoing replace:")
    editor.undo()
    print(f"Text: {editor.get_text()}")

    print("\nUndoing insert:")
    editor.undo()
    print(f"Text: {editor.get_text()}")


def test_smart_home():
    """Test smart home automation."""
    print("\n" + "="*70)
    print("TEST 3: SMART HOME AUTOMATION")
    print("="*70)

    # Create devices
    bedroom_light = Device("Bedroom Light")
    bathroom_light = Device("Bathroom Light")
    living_room_light = Device("Living Room Light")
    thermostat = Thermostat("Thermostat")

    # Create commands
    commands = [
        TurnOnCommand(bedroom_light),
        TurnOnCommand(bathroom_light),
        TurnOnCommand(living_room_light),
        SetTemperatureCommand(thermostat, 22.0)
    ]

    # Schedule commands
    scheduler = CommandScheduler()
    scheduler.schedule(1.0, commands[0])
    scheduler.schedule(1.0, commands[1])
    scheduler.schedule(1.0, commands[2])
    scheduler.schedule(2.0, commands[3])

    print(f"Pending commands: {scheduler.get_pending_count()}")
    scheduler.execute_all()


def test_macros():
    """Test command macros."""
    print("\n" + "="*70)
    print("TEST 4: COMMAND MACROS")
    print("="*70)

    # Create devices
    lights = [Device(f"Light {i}") for i in range(1, 4)]
    tv = Device("TV")
    coffee_maker = Device("Coffee Maker")

    # Create "Good Morning" macro
    morning_macro = CompositeCommand("Good Morning")
    morning_macro.add_command(TurnOnCommand(lights[0]))
    morning_macro.add_command(TurnOnCommand(lights[1]))
    morning_macro.add_command(TurnOnCommand(coffee_maker))

    # Execute macro
    morning_macro.execute()

    # Undo macro
    print("\nUndoing morning routine:")
    morning_macro.undo()


def test_command_logging():
    """Test command logging."""
    print("\n" + "="*70)
    print("TEST 5: COMMAND LOGGING AND AUDIT TRAIL")
    print("="*70)

    logger = CommandLogger()
    light = Light("Office")

    # Execute commands and log them
    cmd1 = LightOnCommand(light)
    cmd1.execute()
    logger.log_command(cmd1)

    time.sleep(0.5)

    cmd2 = LightOffCommand(light)
    cmd2.execute()
    logger.log_command(cmd2)

    time.sleep(0.5)

    cmd3 = LightOnCommand(light)
    cmd3.execute()
    logger.log_command(cmd3)

    logger.print_logs()


def test_command_queue():
    """Test command queue for batch processing."""
    print("\n" + "="*70)
    print("TEST 6: COMMAND QUEUE")
    print("="*70)

    class CommandQueue:
        """Queue for command execution."""

        def __init__(self):
            self.commands: deque = deque()

        def enqueue(self, command: Command):
            """Add command to queue."""
            self.commands.append(command)
            print(f"Queued: {command.__class__.__name__}")

        def process_all(self):
            """Process all commands in queue."""
            print("\nProcessing command queue:")
            while self.commands:
                command = self.commands.popleft()
                command.execute()

    queue = CommandQueue()
    light = Light("Hallway")

    queue.enqueue(LightOnCommand(light))
    queue.enqueue(LightOffCommand(light))
    queue.enqueue(LightOnCommand(light))

    queue.process_all()


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

def print_key_takeaways():
    """Print key learning points."""
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. COMMAND ENCAPSULATES REQUEST AS OBJECT
   Benefits:
   - Decouple invoker from receiver
   - Pass commands around as objects
   - Queue, schedule, execute commands
   - Support undo/redo functionality
   - Log commands for audit trails

2. UNDO/REDO IMPLEMENTATION
   Pattern:
   - Store executed commands in history
   - Undo: call command.undo() in reverse
   - Redo: call command.execute() again
   - Maintain pointer to current command
   - Limit history size (memory constraint)

3. REVERSIBLE COMMANDS
   Requirements:
   - Must have execute() and undo()
   - Undo must completely reverse execute()
   - Store state needed for undo
   - Handle edge cases (can't undo twice)

4. MACRO/COMPOSITE COMMANDS
   Use case:
   - Group multiple commands together
   - Execute as single unit
   - "Good Morning" macro: lights, coffee, etc.
   - Undo entire macro in one action

5. COMMAND QUEUING AND SCHEDULING
   Use cases:
   - Batch processing commands
   - Schedule execution for later time
   - Priority-based execution
   - Async/threaded execution
   - Job scheduling systems

6. COMMAND LOGGING AND AUDIT TRAILS
   Benefits:
   - Audit trail for compliance
   - Debug command execution
   - Replay for testing
   - Crash recovery (replay logs)
   - Analytics on user actions

7. INVOKER VS RECEIVER
   Invoker:
   - Executes command
   - Doesn't know command details
   - Doesn't know receiver
   - Can queue/schedule commands

   Receiver:
   - Performs actual work
   - Called by command
   - Completely decoupled from invoker

8. REAL-WORLD APPLICATIONS
   - Text editors (undo/redo)
   - Job scheduling systems
   - Web frameworks (request handling)
   - Database transactions
   - Workflow engines
   - Smart home automation
   - ATM machines (request encapsulation)
   - Game engines (action replay)
   - API request builders

9. WHEN TO USE COMMAND PATTERN
   - Need to encapsulate requests
   - Require undo/redo functionality
   - Queue commands for later execution
   - Schedule commands
   - Need audit trail/logging
   - Decouple invoker from receiver
   - Support macros/composite operations

10. PERFORMANCE CONSIDERATIONS
    - Memory overhead: store command objects
    - Undo history: limit size to prevent memory leaks
    - Serialization: commands might need serialization
    - Threading: be careful with concurrent command execution
    - Rollback: ensure undo leaves valid state
    """)


if __name__ == "__main__":
    test_simple_command()
    test_text_editor()
    test_smart_home()
    test_macros()
    test_command_logging()
    test_command_queue()
    print_key_takeaways()
