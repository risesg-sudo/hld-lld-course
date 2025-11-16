# Chess Game System - Design Document

## Problem Statement
Design a chess game that supports two players, validates moves according to chess rules, tracks game state (check, checkmate, stalemate), maintains move history for undo functionality, and handles special moves like castling, en passant, and pawn promotion.

---

## Requirements Analysis

### Functional Requirements
1. **Board Setup**: Initialize 8x8 chess board with pieces in starting positions
2. **Move Validation**: Validate moves according to chess rules for each piece type
3. **Turn Management**: Alternate turns between white and black players
4. **Check Detection**: Detect when king is in check
5. **Checkmate Detection**: Detect when game ends in checkmate
6. **Stalemate Detection**: Detect stalemate condition
7. **Special Moves**:
   - Castling (king-side and queen-side)
   - En passant (pawn capture)
   - Pawn promotion (to queen, rook, bishop, knight)
8. **Move History**: Track all moves for undo/redo
9. **Game States**: Track game status (active, white wins, black wins, draw)
10. **Capture**: Handle piece captures

### Non-Functional Requirements
- **Performance**: Move validation should be instant (<100ms)
- **Extensibility**: Easy to add new piece types or variants
- **Maintainability**: Clean code with clear separation of concerns
- **Usability**: Clear interface for making moves

### Out of Scope
- GUI/graphical interface (text-based is sufficient)
- Time controls/chess clocks
- Player ratings/ELO
- Network play/multiplayer
- AI opponent
- Game persistence (save/load)
- Opening book or endgame tablebase

---

## Actors

| Actor | Description | Key Actions |
|-------|-------------|-------------|
| White Player | Player controlling white pieces | Make moves, offer draw, resign |
| Black Player | Player controlling black pieces | Make moves, offer draw, resign |
| Game System | Automated game logic | Validate moves, detect check/checkmate, update board |

---

## Use Cases

### UC1: Make a Move
**Actor**: Player (White/Black)
**Preconditions**: Game is active, it's player's turn

**Main Flow**:
1. Player selects a piece at source position
2. Player selects destination position
3. System validates piece selection (must be player's piece)
4. System validates move according to piece rules
5. System checks if move puts own king in check (illegal)
6. System executes move
7. System checks if opponent is in check
8. System checks for checkmate/stalemate
9. System switches turn
10. System updates game state

**Alternative Flows**:
- **Alt 1**: Invalid move → Display error, prompt for new move
- **Alt 2**: Move puts own king in check → Reject move
- **Alt 3**: Castling move → Validate castling conditions, move king and rook
- **Alt 4**: En passant → Validate conditions, capture pawn
- **Alt 5**: Pawn promotion → Prompt for piece choice, replace pawn

**Exception Flows**:
- **Ex 1**: Selected piece doesn't belong to player → Error
- **Ex 2**: No piece at source position → Error
- **Ex 3**: Destination has player's own piece → Error

**Postconditions**: Board updated, turn switched, game state updated

---

### UC2: Detect Checkmate
**Actor**: Game System
**Preconditions**: A move has been made

**Main Flow**:
1. System checks if current player's king is in check
2. System generates all possible moves for current player
3. System simulates each move
4. System checks if any move removes the check
5. If no legal moves exist, declare checkmate
6. Set game status to opponent wins

**Postconditions**: Game ends if checkmate detected

---

### UC3: Undo Move
**Actor**: Player
**Preconditions**: At least one move has been made

**Main Flow**:
1. Player requests undo
2. System retrieves last move from history
3. System reverses the move
4. System restores captured piece if any
5. System switches turn back
6. System updates board state

**Postconditions**: Board restored to previous state

---

## Class Design

### Class Diagram (ASCII)
```
┌─────────────────────┐
│   Game              │
├─────────────────────┤
│ - board: Board      │
│ - players: Player[] │
│ - current_turn: Col │
│ - status: GameStatus│
│ - move_history: []  │
├─────────────────────┤
│ + make_move()       │
│ + undo_move()       │
│ + is_checkmate()    │
│ + is_stalemate()    │
└──────────┬──────────┘
           │ has
           │
    ┌──────▼──────────┐
    │   Board         │
    ├─────────────────┤
    │ - squares: [][]│
    ├─────────────────┤
    │ + get_piece()   │
    │ + set_piece()   │
    │ + move_piece()  │
    └────────┬────────┘
             │ contains
             │
        ┌────▼────────────┐
        │   Square        │
        ├─────────────────┤
        │ - piece: Piece  │
        │ - position: Pos │
        ├─────────────────┤
        │ + get_piece()   │
        │ + set_piece()   │
        │ + is_occupied() │
        └─────────────────┘

┌──────────────────┐
│   Piece (ABC)    │ ← Abstract Base Class
├──────────────────┤
│ - color: Color   │
│ - position: Pos  │
│ - has_moved: bool│
├──────────────────┤
│ + can_move()     │ ← Abstract
│ + get_moves()    │ ← Abstract
│ + move()         │
└────────┬─────────┘
         △
         │ (inheritance)
         │
    ┌────┴─────────────────────────────────────┐
    │                                           │
┌───┴────┐ ┌──────┐ ┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐
│  King  │ │Queen │ │ Rook │ │ Bishop │ │Knight│ │ Pawn │
└────────┘ └──────┘ └──────┘ └────────┘ └──────┘ └──────┘
           (Each implements can_move() and get_moves())

┌──────────────────┐         ┌─────────────────┐
│   Player         │         │   Move          │
├──────────────────┤         ├─────────────────┤
│ - name: str      │         │ - piece: Piece  │
│ - color: Color   │         │ - from: Position│
│ - is_in_check:   │         │ - to: Position  │
├──────────────────┤         │ - captured: Pc  │
│ + make_move()    │         │ - special: str  │
└──────────────────┘         ├─────────────────┤
                             │ + execute()     │ ← Command Pattern
                             │ + undo()        │
                             └─────────────────┘

┌──────────────────┐
│  MoveValidator   │
├──────────────────┤
│ + is_valid_move()│
│ + is_in_check()  │
│ + causes_check() │
└──────────────────┘

┌──────────────────┐
│  PieceFactory    │ ← Factory Pattern
├──────────────────┤
│ + create_piece() │
└──────────────────┘
```

### Core Classes

#### 1. Position
```python
class Position:
    - row: int           # 0-7
    - col: int           # 0-7

    + __init__(row, col)
    + is_valid() -> bool
    + to_algebraic() -> str  # e.g., "e4"
    + from_algebraic(notation: str) -> Position
    + __eq__(other) -> bool
```

#### 2. Piece (Abstract Base Class)
```python
class Piece(ABC):
    - color: Color
    - position: Position
    - has_moved: bool      # For castling, pawn double move
    - piece_type: PieceType

    + __init__(color, position)
    + can_move(to: Position, board: Board) -> bool  # Abstract
    + get_possible_moves(board: Board) -> List[Position]  # Abstract
    + move(to: Position)
    + get_color() -> Color
    + get_type() -> PieceType
```

#### 3. Concrete Pieces
```python
class King(Piece):
    + can_move(to: Position, board: Board) -> bool
    + get_possible_moves(board: Board) -> List[Position]
    + can_castle_kingside(board: Board) -> bool
    + can_castle_queenside(board: Board) -> bool

class Queen(Piece):
    + can_move(to: Position, board: Board) -> bool
    + get_possible_moves(board: Board) -> List[Position]

class Rook(Piece):
    + can_move(to: Position, board: Board) -> bool
    + get_possible_moves(board: Board) -> List[Position]

class Bishop(Piece):
    + can_move(to: Position, board: Board) -> bool
    + get_possible_moves(board: Board) -> List[Position]

class Knight(Piece):
    + can_move(to: Position, board: Board) -> bool
    + get_possible_moves(board: Board) -> List[Position]

class Pawn(Piece):
    + can_move(to: Position, board: Board) -> bool
    + get_possible_moves(board: Board) -> List[Position]
    + can_promote() -> bool
    + can_en_passant(to: Position, board: Board) -> bool
```

#### 4. Square
```python
class Square:
    - piece: Optional[Piece]
    - position: Position

    + __init__(position)
    + get_piece() -> Optional[Piece]
    + set_piece(piece: Piece)
    + is_occupied() -> bool
    + is_occupied_by_color(color: Color) -> bool
```

#### 5. Board
```python
class Board:
    - squares: List[List[Square]]  # 8x8 grid
    - captured_pieces: List[Piece]

    + __init__()
    + initialize_board()           # Setup starting position
    + get_piece(pos: Position) -> Optional[Piece]
    + set_piece(pos: Position, piece: Piece)
    + move_piece(from: Position, to: Position) -> Optional[Piece]
    + is_position_valid(pos: Position) -> bool
    + get_all_pieces(color: Color) -> List[Piece]
    + get_king(color: Color) -> King
    + clone() -> Board  # For move simulation
```

#### 6. Move (Command Pattern)
```python
class Move:
    - piece: Piece
    - from_position: Position
    - to_position: Position
    - captured_piece: Optional[Piece]
    - is_castling: bool
    - is_en_passant: bool
    - is_promotion: bool
    - promoted_to: Optional[PieceType]

    + __init__(piece, from_pos, to_pos)
    + execute(board: Board)        # Execute the move
    + undo(board: Board)           # Undo the move
    + to_algebraic_notation() -> str  # e.g., "e2-e4"
```

#### 7. Player
```python
class Player:
    - name: str
    - color: Color
    - is_in_check: bool

    + __init__(name, color)
    + get_color() -> Color
    + set_check_status(in_check: bool)
```

#### 8. Game
```python
class Game:
    - board: Board
    - white_player: Player
    - black_player: Player
    - current_turn: Color
    - status: GameStatus
    - move_history: List[Move]
    - validator: MoveValidator

    + __init__(player1_name, player2_name)
    + start()
    + make_move(from: Position, to: Position, promotion: PieceType) -> bool
    + undo_move() -> bool
    + is_check(color: Color) -> bool
    + is_checkmate(color: Color) -> bool
    + is_stalemate(color: Color) -> bool
    + get_current_player() -> Player
    + switch_turn()
    + get_status() -> GameStatus
```

#### 9. MoveValidator
```python
class MoveValidator:
    + is_valid_move(move: Move, board: Board) -> bool
    + is_legal_move(move: Move, board: Board) -> bool  # Doesn't put own king in check
    + is_position_under_attack(pos: Position, by_color: Color, board: Board) -> bool
    + is_in_check(king_color: Color, board: Board) -> bool
    + get_all_legal_moves(color: Color, board: Board) -> List[Move]
    + causes_self_check(move: Move, board: Board) -> bool
```

#### 10. PieceFactory (Factory Pattern)
```python
class PieceFactory:
    + create_piece(piece_type: PieceType, color: Color, position: Position) -> Piece
    + create_king(color: Color, position: Position) -> King
    + create_queen(color: Color, position: Position) -> Queen
    + create_rook(color: Color, position: Position) -> Rook
    + create_bishop(color: Color, position: Position) -> Bishop
    + create_knight(color: Color, position: Position) -> Knight
    + create_pawn(color: Color, position: Position) -> Pawn
```

### Enumerations

```python
class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    KING = "K"
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN = "P"

class GameStatus(Enum):
    ACTIVE = "active"
    WHITE_WIN = "white_wins"
    BLACK_WIN = "black_wins"
    STALEMATE = "stalemate"
    DRAW = "draw"
```

---

## Design Patterns Applied

### 1. Factory Pattern
**Where**: `PieceFactory`

**Why**:
- Creating different piece types with different behaviors
- Centralizes piece creation logic
- Easy to extend with new piece types (for variants like Chess960)

**Implementation**:
```python
class PieceFactory:
    @staticmethod
    def create_piece(piece_type, color, position):
        if piece_type == PieceType.KING:
            return King(color, position)
        elif piece_type == PieceType.QUEEN:
            return Queen(color, position)
        # ... etc
```

### 2. Command Pattern
**Where**: `Move` class

**Why**:
- Encapsulate move as an object
- Support undo/redo functionality
- Move history tracking
- Can add logging, replay, analysis

**Implementation**:
```python
class Move:
    def execute(self, board):
        # Execute the move
        # Store necessary info for undo
        pass

    def undo(self, board):
        # Reverse the move
        # Restore captured pieces
        pass
```

### 3. Strategy Pattern
**Where**: Different piece movement strategies

**Why**:
- Each piece type has different movement rules
- Movement logic encapsulated in each piece class
- Easy to modify rules or add new pieces

**Implementation**:
```python
class Piece(ABC):
    @abstractmethod
    def can_move(self, to, board):
        pass  # Each piece implements its own strategy

class Knight(Piece):
    def can_move(self, to, board):
        # L-shaped move logic
        pass

class Bishop(Piece):
    def can_move(self, to, board):
        # Diagonal move logic
        pass
```

### 4. Template Method Pattern
**Where**: `Piece` abstract class

**Why**:
- Define skeleton of move validation algorithm
- Subclasses provide specific implementations
- Common code reused in base class

**Implementation**:
```python
class Piece(ABC):
    def move(self, to):
        # Template method - common logic
        if not self.can_move(to):
            raise InvalidMoveException()
        self.position = to
        self.has_moved = True

    @abstractmethod
    def can_move(self, to):
        # Specific implementation in subclasses
        pass
```

---

## SOLID Principles Demonstrated

### Single Responsibility Principle (SRP)
- `Board`: Manages only the chess board state
- `Piece`: Each piece manages only its movement rules
- `MoveValidator`: Handles only move validation logic
- `Game`: Coordinates game flow, doesn't handle validation or movement

### Open/Closed Principle (OCP)
- New piece types can be added without modifying existing code
- New game variants can extend `Game` class
- New move validators can extend `MoveValidator`

### Liskov Substitution Principle (LSP)
- Any `Piece` subclass can be used wherever `Piece` is expected
- All pieces respond to `can_move()` and `get_possible_moves()`
- Substituting one piece type for another doesn't break the system

### Interface Segregation Principle (ISP)
- `Piece` interface has only essential methods
- Clients depend only on methods they use
- No unnecessary methods forced on implementers

### Dependency Inversion Principle (DIP)
- `Game` depends on `Board` abstraction, not specific implementation
- `Board` depends on `Piece` abstraction
- High-level game logic doesn't depend on low-level piece details

---

## Move Validation Algorithm

### Basic Move Validation
```
1. Check piece exists at source
2. Check piece belongs to current player
3. Check destination is different from source
4. Check piece-specific move rules (can_move)
5. Check path is clear (for sliding pieces)
6. Check destination doesn't have own piece
7. Simulate move and check if it puts own king in check
8. If all checks pass, move is valid
```

### Check Detection
```
1. Find king of given color
2. For each opponent piece:
   a. Check if piece can attack king's position
   b. If any piece can attack, king is in check
3. Return check status
```

### Checkmate Detection
```
1. Verify king is in check
2. Generate all possible moves for current player
3. For each move:
   a. Simulate move on board copy
   b. Check if king still in check
   c. If any move removes check, not checkmate
4. If no legal moves exist, it's checkmate
```

---

## Special Moves Implementation

### Castling
**Conditions**:
- King hasn't moved
- Rook hasn't moved
- No pieces between king and rook
- King not in check
- King doesn't pass through check
- King doesn't end up in check

**Implementation**:
```python
def can_castle_kingside(king, board):
    if king.has_moved:
        return False
    rook = board.get_piece(Position(king.row, 7))
    if not rook or rook.has_moved:
        return False
    # Check empty squares
    # Check king not in check
    # Check king doesn't pass through check
    return True
```

### En Passant
**Conditions**:
- Opponent pawn just moved two squares forward
- Your pawn is beside opponent pawn
- Capture immediately (only valid for one turn)

### Pawn Promotion
**Conditions**:
- Pawn reaches opposite end of board (row 0 or 7)
- Player chooses piece to promote to (Q, R, B, N)

---

## Edge Cases Handled

1. **Invalid positions**: Positions outside 0-7 range
2. **Moving to same square**: Source and destination are same
3. **Capturing own piece**: Destination has player's own piece
4. **Moving through pieces**: Sliding pieces blocked by other pieces
5. **Self-check**: Move puts own king in check
6. **Stalemate**: No legal moves but not in check
7. **Insufficient material**: Only kings left (draw)
8. **Threefold repetition**: Same position repeated three times
9. **Fifty-move rule**: 50 moves without capture or pawn move

---

## Sample Usage Flow

```
1. Create game
   └─> Game(player1="Alice", player2="Bob")
   └─> Board initialized with pieces in starting positions

2. White's turn - Move pawn
   └─> make_move(from="e2", to="e4")
   └─> Validate move
   └─> Execute move
   └─> Check for check/checkmate
   └─> Switch turn

3. Black's turn - Move knight
   └─> make_move(from="g8", to="f6")
   └─> Validate and execute
   └─> Switch turn

4. Continue playing...

5. Special move - Castling
   └─> make_move(from="e1", to="g1")  # King-side castling
   └─> Validate castling conditions
   └─> Move both king and rook

6. Pawn promotion
   └─> make_move(from="a7", to="a8", promotion=PieceType.QUEEN)
   └─> Replace pawn with queen

7. Checkmate detected
   └─> Game status changes to WHITE_WIN or BLACK_WIN

8. Undo move (if allowed)
   └─> undo_move()
   └─> Restore previous board state
```

---

## Testing Considerations

### Unit Tests
1. Test each piece's movement rules
2. Test board initialization
3. Test move execution and undo
4. Test check detection
5. Test checkmate detection

### Integration Tests
1. Test complete game flow
2. Test special moves (castling, en passant, promotion)
3. Test checkmate scenarios (Scholar's Mate, Fool's Mate)
4. Test stalemate scenarios

### Edge Case Tests
1. Test invalid moves
2. Test self-check prevention
3. Test boundary conditions (edge of board)

---

## Potential Enhancements

1. **AI Opponent**: Minimax algorithm with alpha-beta pruning
2. **Move Notation**: Full algebraic notation (e.g., Nf3, Qxd5+)
3. **Time Control**: Chess clocks, time limits
4. **Draw Conditions**: Threefold repetition, fifty-move rule, insufficient material
5. **Game Save/Load**: Serialize game state to file
6. **Move Analysis**: Suggest best moves, blunder detection
7. **Opening Book**: Database of opening sequences
8. **Puzzle Mode**: Chess puzzles and tactics training
9. **Variants**: Chess960, Crazyhouse, Three-check
10. **Network Play**: Online multiplayer

---

## Complexity Analysis

### Time Complexity
- **Move validation**: O(1) for most pieces, O(n) for checking check (n = number of opponent pieces)
- **Get possible moves**: O(1) to O(64) depending on piece
- **Checkmate detection**: O(n²) where n = number of pieces
- **Board clone**: O(64) constant

### Space Complexity
- **Board**: O(64) = O(1) constant
- **Move history**: O(m) where m = number of moves
- **Overall**: O(m) linear with game length

---

## Conclusion

This chess game design demonstrates:
- Clean object-oriented design with inheritance hierarchy
- Appropriate use of design patterns (Factory, Command, Strategy)
- SOLID principles throughout
- Complete chess rules implementation
- Extensible architecture for variants and enhancements
- Proper move validation and game state management

The system is ready for text-based play and can be extended with GUI, AI, or network features.
