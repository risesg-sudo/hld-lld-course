"""
Chess Game System - Complete Implementation
Demonstrates: Factory, Strategy, Command, Template Method patterns
SOLID Principles: All five principles demonstrated
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Tuple
from copy import deepcopy


# ============================================================================
# ENUMERATIONS
# ============================================================================

class Color(Enum):
    """Chess piece colors"""
    WHITE = "white"
    BLACK = "black"

    def opposite(self):
        """Get opposite color"""
        return Color.BLACK if self == Color.WHITE else Color.WHITE


class PieceType(Enum):
    """Types of chess pieces"""
    KING = ("K", "♔", "♚")
    QUEEN = ("Q", "♕", "♛")
    ROOK = ("R", "♖", "♜")
    BISHOP = ("B", "♗", "♝")
    KNIGHT = ("N", "♘", "♞")
    PAWN = ("P", "♙", "♟")

    def __init__(self, code, white_symbol, black_symbol):
        self.code = code
        self.white_symbol = white_symbol
        self.black_symbol = black_symbol


class GameStatus(Enum):
    """Game status"""
    ACTIVE = "active"
    WHITE_WIN = "white_wins"
    BLACK_WIN = "black_wins"
    STALEMATE = "stalemate"
    DRAW = "draw"


# ============================================================================
# EXCEPTIONS
# ============================================================================

class ChessException(Exception):
    """Base exception for chess game"""
    pass


class InvalidMoveException(ChessException):
    """Raised when move is invalid"""
    pass


class InvalidPositionException(ChessException):
    """Raised when position is invalid"""
    pass


# ============================================================================
# POSITION
# ============================================================================

class Position:
    """
    Represents a position on the chess board.
    Demonstrates: Value Object pattern
    """

    def __init__(self, row: int, col: int):
        """
        Initialize position.

        Args:
            row: Row index (0-7, where 0 is row 8 and 7 is row 1)
            col: Column index (0-7, where 0 is 'a' and 7 is 'h')
        """
        if not self._is_valid(row, col):
            raise InvalidPositionException(f"Invalid position: ({row}, {col})")
        self.row = row
        self.col = col

    @staticmethod
    def _is_valid(row: int, col: int) -> bool:
        """Check if position is valid"""
        return 0 <= row < 8 and 0 <= col < 8

    def is_valid(self) -> bool:
        """Check if this position is valid"""
        return self._is_valid(self.row, self.col)

    def to_algebraic(self) -> str:
        """Convert to algebraic notation (e.g., 'e4')"""
        col_letter = chr(ord('a') + self.col)
        row_number = str(8 - self.row)
        return f"{col_letter}{row_number}"

    @classmethod
    def from_algebraic(cls, notation: str) -> 'Position':
        """
        Create position from algebraic notation.

        Args:
            notation: Algebraic notation like 'e4', 'a1', etc.

        Returns:
            Position object
        """
        if len(notation) != 2:
            raise InvalidPositionException(f"Invalid notation: {notation}")

        col = ord(notation[0].lower()) - ord('a')
        row = 8 - int(notation[1])

        return cls(row, col)

    def __eq__(self, other):
        """Check equality"""
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        """Hash for use in sets/dicts"""
        return hash((self.row, self.col))

    def __str__(self):
        return self.to_algebraic()

    def __repr__(self):
        return f"Position({self.row}, {self.col})"


# ============================================================================
# PIECES (Strategy Pattern)
# ============================================================================

class Piece(ABC):
    """
    Abstract base class for chess pieces.
    Demonstrates: Template Method, Strategy Pattern, SRP
    """

    def __init__(self, color: Color, position: Position, piece_type: PieceType):
        """
        Initialize a piece.

        Args:
            color: Piece color
            position: Current position
            piece_type: Type of piece
        """
        self.color = color
        self.position = position
        self.piece_type = piece_type
        self.has_moved = False

    @abstractmethod
    def can_move(self, to: Position, board: 'Board') -> bool:
        """
        Check if piece can move to given position.
        Each piece implements its own movement rules.

        Args:
            to: Destination position
            board: Current board state

        Returns:
            True if move is valid for this piece type
        """
        pass

    @abstractmethod
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """
        Get all possible moves for this piece.

        Args:
            board: Current board state

        Returns:
            List of valid destination positions
        """
        pass

    def move(self, to: Position):
        """Move piece to new position"""
        self.position = to
        self.has_moved = True

    def is_opponent(self, other: 'Piece') -> bool:
        """Check if other piece is opponent"""
        return other is not None and other.color != self.color

    def get_symbol(self) -> str:
        """Get Unicode symbol for piece"""
        if self.color == Color.WHITE:
            return self.piece_type.white_symbol
        return self.piece_type.black_symbol

    def __str__(self):
        return f"{self.color.value} {self.piece_type.code}"


class King(Piece):
    """King piece - moves one square in any direction"""

    def __init__(self, color: Color, position: Position):
        super().__init__(color, position, PieceType.KING)

    def can_move(self, to: Position, board: 'Board') -> bool:
        """King moves one square in any direction"""
        row_diff = abs(to.row - self.position.row)
        col_diff = abs(to.col - self.position.col)

        # Normal king move (one square)
        if row_diff <= 1 and col_diff <= 1:
            target = board.get_piece(to)
            return target is None or self.is_opponent(target)

        # Castling
        if row_diff == 0 and col_diff == 2:
            return self._can_castle(to, board)

        return False

    def _can_castle(self, to: Position, board: 'Board') -> bool:
        """Check if castling is valid"""
        if self.has_moved:
            return False

        # King-side castling
        if to.col == 6:
            rook_pos = Position(self.position.row, 7)
            rook = board.get_piece(rook_pos)
            if rook is None or rook.has_moved or rook.piece_type != PieceType.ROOK:
                return False

            # Check squares are empty
            for col in range(5, 7):
                if board.get_piece(Position(self.position.row, col)) is not None:
                    return False
            return True

        # Queen-side castling
        elif to.col == 2:
            rook_pos = Position(self.position.row, 0)
            rook = board.get_piece(rook_pos)
            if rook is None or rook.has_moved or rook.piece_type != PieceType.ROOK:
                return False

            # Check squares are empty
            for col in range(1, 4):
                if board.get_piece(Position(self.position.row, col)) is not None:
                    return False
            return True

        return False

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """Get all possible king moves"""
        moves = []
        # All 8 directions
        for row_delta in [-1, 0, 1]:
            for col_delta in [-1, 0, 1]:
                if row_delta == 0 and col_delta == 0:
                    continue

                try:
                    new_pos = Position(self.position.row + row_delta, self.position.col + col_delta)
                    if self.can_move(new_pos, board):
                        moves.append(new_pos)
                except InvalidPositionException:
                    pass

        # Castling
        try:
            king_side = Position(self.position.row, 6)
            if self.can_move(king_side, board):
                moves.append(king_side)
        except InvalidPositionException:
            pass

        try:
            queen_side = Position(self.position.row, 2)
            if self.can_move(queen_side, board):
                moves.append(queen_side)
        except InvalidPositionException:
            pass

        return moves


class Queen(Piece):
    """Queen piece - moves any distance in straight or diagonal lines"""

    def __init__(self, color: Color, position: Position):
        super().__init__(color, position, PieceType.QUEEN)

    def can_move(self, to: Position, board: 'Board') -> bool:
        """Queen moves like rook + bishop"""
        row_diff = abs(to.row - self.position.row)
        col_diff = abs(to.col - self.position.col)

        # Must be straight or diagonal
        if row_diff == 0 or col_diff == 0 or row_diff == col_diff:
            return board.is_path_clear(self.position, to)

        return False

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """Get all possible queen moves"""
        moves = []
        # 8 directions: horizontal, vertical, diagonal
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for row_dir, col_dir in directions:
            for dist in range(1, 8):
                try:
                    new_pos = Position(
                        self.position.row + row_dir * dist,
                        self.position.col + col_dir * dist
                    )
                    if self.can_move(new_pos, board):
                        moves.append(new_pos)
                        # Stop if we capture a piece
                        if board.get_piece(new_pos) is not None:
                            break
                    else:
                        break
                except InvalidPositionException:
                    break

        return moves


class Rook(Piece):
    """Rook piece - moves any distance horizontally or vertically"""

    def __init__(self, color: Color, position: Position):
        super().__init__(color, position, PieceType.ROOK)

    def can_move(self, to: Position, board: 'Board') -> bool:
        """Rook moves in straight lines"""
        row_diff = abs(to.row - self.position.row)
        col_diff = abs(to.col - self.position.col)

        # Must be horizontal or vertical
        if (row_diff == 0 or col_diff == 0) and (row_diff + col_diff > 0):
            return board.is_path_clear(self.position, to)

        return False

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """Get all possible rook moves"""
        moves = []
        # 4 directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for row_dir, col_dir in directions:
            for dist in range(1, 8):
                try:
                    new_pos = Position(
                        self.position.row + row_dir * dist,
                        self.position.col + col_dir * dist
                    )
                    if self.can_move(new_pos, board):
                        moves.append(new_pos)
                        if board.get_piece(new_pos) is not None:
                            break
                    else:
                        break
                except InvalidPositionException:
                    break

        return moves


class Bishop(Piece):
    """Bishop piece - moves any distance diagonally"""

    def __init__(self, color: Color, position: Position):
        super().__init__(color, position, PieceType.BISHOP)

    def can_move(self, to: Position, board: 'Board') -> bool:
        """Bishop moves diagonally"""
        row_diff = abs(to.row - self.position.row)
        col_diff = abs(to.col - self.position.col)

        # Must be diagonal
        if row_diff == col_diff and row_diff > 0:
            return board.is_path_clear(self.position, to)

        return False

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """Get all possible bishop moves"""
        moves = []
        # 4 diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for row_dir, col_dir in directions:
            for dist in range(1, 8):
                try:
                    new_pos = Position(
                        self.position.row + row_dir * dist,
                        self.position.col + col_dir * dist
                    )
                    if self.can_move(new_pos, board):
                        moves.append(new_pos)
                        if board.get_piece(new_pos) is not None:
                            break
                    else:
                        break
                except InvalidPositionException:
                    break

        return moves


class Knight(Piece):
    """Knight piece - moves in L-shape"""

    def __init__(self, color: Color, position: Position):
        super().__init__(color, position, PieceType.KNIGHT)

    def can_move(self, to: Position, board: 'Board') -> bool:
        """Knight moves in L-shape (2+1 or 1+2)"""
        row_diff = abs(to.row - self.position.row)
        col_diff = abs(to.col - self.position.col)

        # L-shape: 2+1 or 1+2
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            target = board.get_piece(to)
            return target is None or self.is_opponent(target)

        return False

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """Get all possible knight moves"""
        moves = []
        # All 8 L-shaped moves
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for row_delta, col_delta in knight_moves:
            try:
                new_pos = Position(self.position.row + row_delta, self.position.col + col_delta)
                if self.can_move(new_pos, board):
                    moves.append(new_pos)
            except InvalidPositionException:
                pass

        return moves


class Pawn(Piece):
    """Pawn piece - moves forward, captures diagonally"""

    def __init__(self, color: Color, position: Position):
        super().__init__(color, position, PieceType.PAWN)

    def can_move(self, to: Position, board: 'Board') -> bool:
        """Pawn moves forward, captures diagonally"""
        direction = -1 if self.color == Color.WHITE else 1
        row_diff = to.row - self.position.row
        col_diff = abs(to.col - self.position.col)

        # Forward move
        if col_diff == 0:
            # One square forward
            if row_diff == direction:
                return board.get_piece(to) is None

            # Two squares forward (initial move)
            if not self.has_moved and row_diff == 2 * direction:
                middle_pos = Position(self.position.row + direction, self.position.col)
                return board.get_piece(middle_pos) is None and board.get_piece(to) is None

        # Diagonal capture
        elif col_diff == 1 and row_diff == direction:
            target = board.get_piece(to)
            return target is not None and self.is_opponent(target)

        return False

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """Get all possible pawn moves"""
        moves = []
        direction = -1 if self.color == Color.WHITE else 1

        # Forward one square
        try:
            forward_one = Position(self.position.row + direction, self.position.col)
            if self.can_move(forward_one, board):
                moves.append(forward_one)

                # Forward two squares (initial move)
                if not self.has_moved:
                    forward_two = Position(self.position.row + 2 * direction, self.position.col)
                    if self.can_move(forward_two, board):
                        moves.append(forward_two)
        except InvalidPositionException:
            pass

        # Diagonal captures
        for col_delta in [-1, 1]:
            try:
                capture_pos = Position(self.position.row + direction, self.position.col + col_delta)
                if self.can_move(capture_pos, board):
                    moves.append(capture_pos)
            except InvalidPositionException:
                pass

        return moves

    def can_promote(self) -> bool:
        """Check if pawn can be promoted"""
        if self.color == Color.WHITE:
            return self.position.row == 0
        return self.position.row == 7


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class PieceFactory:
    """
    Factory for creating chess pieces.
    Demonstrates: Factory Pattern, OCP
    """

    @staticmethod
    def create_piece(piece_type: PieceType, color: Color, position: Position) -> Piece:
        """
        Create a chess piece of given type.

        Args:
            piece_type: Type of piece to create
            color: Color of piece
            position: Initial position

        Returns:
            Created piece
        """
        if piece_type == PieceType.KING:
            return King(color, position)
        elif piece_type == PieceType.QUEEN:
            return Queen(color, position)
        elif piece_type == PieceType.ROOK:
            return Rook(color, position)
        elif piece_type == PieceType.BISHOP:
            return Bishop(color, position)
        elif piece_type == PieceType.KNIGHT:
            return Knight(color, position)
        elif piece_type == PieceType.PAWN:
            return Pawn(color, position)
        else:
            raise ValueError(f"Unknown piece type: {piece_type}")


# ============================================================================
# BOARD
# ============================================================================

class Board:
    """
    Chess board.
    Demonstrates: SRP - manages only board state
    """

    def __init__(self):
        """Initialize empty 8x8 board"""
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.captured_pieces = []

    def initialize_board(self):
        """Set up pieces in starting position"""
        # Pawns
        for col in range(8):
            self.set_piece(Position(6, col), PieceFactory.create_piece(PieceType.PAWN, Color.WHITE, Position(6, col)))
            self.set_piece(Position(1, col), PieceFactory.create_piece(PieceType.PAWN, Color.BLACK, Position(1, col)))

        # Other pieces for white (row 7)
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                      PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]

        for col, piece_type in enumerate(piece_order):
            self.set_piece(Position(7, col), PieceFactory.create_piece(piece_type, Color.WHITE, Position(7, col)))
            self.set_piece(Position(0, col), PieceFactory.create_piece(piece_type, Color.BLACK, Position(0, col)))

    def get_piece(self, pos: Position) -> Optional[Piece]:
        """Get piece at position"""
        return self.squares[pos.row][pos.col]

    def set_piece(self, pos: Position, piece: Optional[Piece]):
        """Set piece at position"""
        self.squares[pos.row][pos.col] = piece
        if piece:
            piece.position = pos

    def move_piece(self, from_pos: Position, to_pos: Position) -> Optional[Piece]:
        """
        Move piece from one position to another.

        Returns:
            Captured piece if any
        """
        piece = self.get_piece(from_pos)
        captured = self.get_piece(to_pos)

        if captured:
            self.captured_pieces.append(captured)

        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)

        if piece:
            piece.move(to_pos)

        return captured

    def is_path_clear(self, from_pos: Position, to_pos: Position) -> bool:
        """
        Check if path between positions is clear.
        Used for sliding pieces (rook, bishop, queen).
        """
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # Determine direction
        row_step = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
        col_step = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)

        # Check each square in path
        curr_row = from_pos.row + row_step
        curr_col = from_pos.col + col_step

        while curr_row != to_pos.row or curr_col != to_pos.col:
            if self.get_piece(Position(curr_row, curr_col)) is not None:
                return False
            curr_row += row_step
            curr_col += col_step

        # Check destination
        dest_piece = self.get_piece(to_pos)
        source_piece = self.get_piece(from_pos)

        if dest_piece is None:
            return True

        return source_piece.is_opponent(dest_piece)

    def get_all_pieces(self, color: Color) -> List[Piece]:
        """Get all pieces of given color"""
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(Position(row, col))
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces

    def get_king(self, color: Color) -> Optional[King]:
        """Find king of given color"""
        for piece in self.get_all_pieces(color):
            if piece.piece_type == PieceType.KING:
                return piece
        return None

    def clone(self) -> 'Board':
        """Create deep copy of board"""
        return deepcopy(self)

    def display(self):
        """Display board in console"""
        print("\n  a b c d e f g h")
        print("  ───────────────")
        for row in range(8):
            print(f"{8-row}|", end="")
            for col in range(8):
                piece = self.get_piece(Position(row, col))
                if piece:
                    print(piece.get_symbol(), end=" ")
                else:
                    print("·", end=" ")
            print(f"|{8-row}")
        print("  ───────────────")
        print("  a b c d e f g h\n")


# ============================================================================
# MOVE (Command Pattern)
# ============================================================================

class Move:
    """
    Represents a chess move.
    Demonstrates: Command Pattern - encapsulates move as object
    """

    def __init__(self, piece: Piece, from_pos: Position, to_pos: Position):
        """
        Initialize a move.

        Args:
            piece: Piece being moved
            from_pos: Starting position
            to_pos: Destination position
        """
        self.piece = piece
        self.from_position = from_pos
        self.to_position = to_pos
        self.captured_piece: Optional[Piece] = None
        self.is_castling = False
        self.castling_rook_move: Optional[Tuple[Position, Position]] = None
        self.is_promotion = False
        self.promoted_to: Optional[PieceType] = None
        self.piece_had_moved = piece.has_moved

    def execute(self, board: Board):
        """Execute the move"""
        # Handle castling
        if isinstance(self.piece, King) and abs(self.to_position.col - self.from_position.col) == 2:
            self.is_castling = True
            # Move rook
            if self.to_position.col == 6:  # King-side
                rook_from = Position(self.from_position.row, 7)
                rook_to = Position(self.from_position.row, 5)
            else:  # Queen-side
                rook_from = Position(self.from_position.row, 0)
                rook_to = Position(self.from_position.row, 3)

            self.castling_rook_move = (rook_from, rook_to)
            board.move_piece(rook_from, rook_to)

        # Execute main move
        self.captured_piece = board.move_piece(self.from_position, self.to_position)

        # Handle pawn promotion
        if isinstance(self.piece, Pawn) and self.piece.can_promote():
            self.is_promotion = True
            if self.promoted_to is None:
                self.promoted_to = PieceType.QUEEN  # Default promotion

            new_piece = PieceFactory.create_piece(self.promoted_to, self.piece.color, self.to_position)
            new_piece.has_moved = True
            board.set_piece(self.to_position, new_piece)

    def undo(self, board: Board):
        """Undo the move"""
        # Restore piece position
        board.set_piece(self.from_position, self.piece)
        self.piece.position = self.from_position
        self.piece.has_moved = self.piece_had_moved

        # Restore captured piece
        board.set_piece(self.to_position, self.captured_piece)

        # Undo castling
        if self.is_castling and self.castling_rook_move:
            rook_from, rook_to = self.castling_rook_move
            rook = board.get_piece(rook_to)
            board.set_piece(rook_from, rook)
            board.set_piece(rook_to, None)
            if rook:
                rook.position = rook_from
                rook.has_moved = False

    def to_algebraic_notation(self) -> str:
        """Convert move to algebraic notation"""
        return f"{self.from_position.to_algebraic()}-{self.to_position.to_algebraic()}"

    def __str__(self):
        return self.to_algebraic_notation()


# ============================================================================
# MOVE VALIDATOR
# ============================================================================

class MoveValidator:
    """
    Validates chess moves.
    Demonstrates: SRP - handles only move validation logic
    """

    @staticmethod
    def is_valid_move(move: Move, board: Board) -> bool:
        """Check if move follows piece movement rules"""
        return move.piece.can_move(move.to_position, board)

    @staticmethod
    def is_position_under_attack(pos: Position, by_color: Color, board: Board) -> bool:
        """Check if position is under attack by given color"""
        for piece in board.get_all_pieces(by_color):
            if piece.can_move(pos, board):
                return True
        return False

    @staticmethod
    def is_in_check(king_color: Color, board: Board) -> bool:
        """Check if king of given color is in check"""
        king = board.get_king(king_color)
        if not king:
            return False

        opponent_color = king_color.opposite()
        return MoveValidator.is_position_under_attack(king.position, opponent_color, board)

    @staticmethod
    def causes_self_check(move: Move, board: Board) -> bool:
        """Check if move puts own king in check"""
        # Simulate move on board copy
        board_copy = board.clone()

        # Execute move on copy
        from_piece = board_copy.get_piece(move.from_position)
        board_copy.move_piece(move.from_position, move.to_position)

        # Check if king is in check
        return MoveValidator.is_in_check(from_piece.color, board_copy)

    @staticmethod
    def is_legal_move(move: Move, board: Board) -> bool:
        """Check if move is legal (valid and doesn't cause self-check)"""
        if not MoveValidator.is_valid_move(move, board):
            return False

        if MoveValidator.causes_self_check(move, board):
            return False

        return True

    @staticmethod
    def get_all_legal_moves(color: Color, board: Board) -> List[Move]:
        """Get all legal moves for given color"""
        legal_moves = []

        for piece in board.get_all_pieces(color):
            possible_positions = piece.get_possible_moves(board)
            for to_pos in possible_positions:
                move = Move(piece, piece.position, to_pos)
                if MoveValidator.is_legal_move(move, board):
                    legal_moves.append(move)

        return legal_moves


# ============================================================================
# PLAYER
# ============================================================================

class Player:
    """Represents a chess player"""

    def __init__(self, name: str, color: Color):
        """
        Initialize player.

        Args:
            name: Player name
            color: Player color (WHITE or BLACK)
        """
        self.name = name
        self.color = color
        self.is_in_check = False

    def __str__(self):
        return f"{self.name} ({self.color.value})"


# ============================================================================
# GAME
# ============================================================================

class Game:
    """
    Main game controller.
    Demonstrates: Facade pattern - simplifies complex subsystem interaction
    """

    def __init__(self, white_player_name: str, black_player_name: str):
        """
        Initialize game.

        Args:
            white_player_name: Name of white player
            black_player_name: Name of black player
        """
        self.board = Board()
        self.board.initialize_board()

        self.white_player = Player(white_player_name, Color.WHITE)
        self.black_player = Player(black_player_name, Color.BLACK)

        self.current_turn = Color.WHITE
        self.status = GameStatus.ACTIVE
        self.move_history: List[Move] = []
        self.validator = MoveValidator()

    def get_current_player(self) -> Player:
        """Get current player"""
        return self.white_player if self.current_turn == Color.WHITE else self.black_player

    def make_move(self, from_notation: str, to_notation: str,
                 promotion: Optional[PieceType] = None) -> bool:
        """
        Make a move using algebraic notation.

        Args:
            from_notation: Source position (e.g., "e2")
            to_notation: Destination position (e.g., "e4")
            promotion: Piece type for pawn promotion

        Returns:
            True if move successful

        Raises:
            InvalidMoveException: If move is invalid
        """
        if self.status != GameStatus.ACTIVE:
            raise InvalidMoveException("Game is not active")

        # Parse positions
        try:
            from_pos = Position.from_algebraic(from_notation)
            to_pos = Position.from_algebraic(to_notation)
        except InvalidPositionException as e:
            raise InvalidMoveException(f"Invalid position: {e}")

        # Get piece
        piece = self.board.get_piece(from_pos)
        if piece is None:
            raise InvalidMoveException(f"No piece at {from_notation}")

        if piece.color != self.current_turn:
            raise InvalidMoveException(f"Not {piece.color.value}'s turn")

        # Create move
        move = Move(piece, from_pos, to_pos)
        if promotion:
            move.promoted_to = promotion

        # Validate move
        if not self.validator.is_legal_move(move, self.board):
            raise InvalidMoveException(f"Illegal move: {move}")

        # Execute move
        move.execute(self.board)
        self.move_history.append(move)

        # Update game state
        self._update_game_state()

        # Switch turn
        self.switch_turn()

        return True

    def undo_move(self) -> bool:
        """Undo last move"""
        if not self.move_history:
            return False

        last_move = self.move_history.pop()
        last_move.undo(self.board)

        # Switch turn back
        self.switch_turn()

        # Update game state
        self.status = GameStatus.ACTIVE
        self._update_game_state()

        return True

    def _update_game_state(self):
        """Update game status (check, checkmate, stalemate)"""
        opponent_color = self.current_turn.opposite()

        # Check if opponent is in check
        if self.is_check(opponent_color):
            opponent = self.black_player if opponent_color == Color.BLACK else self.white_player
            opponent.is_in_check = True

            # Check for checkmate
            if self.is_checkmate(opponent_color):
                self.status = GameStatus.WHITE_WIN if self.current_turn == Color.WHITE else GameStatus.BLACK_WIN
                print(f"\nCheckmate! {self.get_current_player().name} wins!")
        else:
            opponent = self.black_player if opponent_color == Color.BLACK else self.white_player
            opponent.is_in_check = False

            # Check for stalemate
            if self.is_stalemate(opponent_color):
                self.status = GameStatus.STALEMATE
                print("\nStalemate! Game is a draw!")

    def is_check(self, color: Color) -> bool:
        """Check if given color is in check"""
        return self.validator.is_in_check(color, self.board)

    def is_checkmate(self, color: Color) -> bool:
        """Check if given color is in checkmate"""
        if not self.is_check(color):
            return False

        # Check if any legal move can save the king
        legal_moves = self.validator.get_all_legal_moves(color, self.board)
        return len(legal_moves) == 0

    def is_stalemate(self, color: Color) -> bool:
        """Check if given color is in stalemate"""
        if self.is_check(color):
            return False

        # No legal moves but not in check = stalemate
        legal_moves = self.validator.get_all_legal_moves(color, self.board)
        return len(legal_moves) == 0

    def switch_turn(self):
        """Switch to other player's turn"""
        self.current_turn = self.current_turn.opposite()

    def display_board(self):
        """Display current board state"""
        self.board.display()

    def display_status(self):
        """Display game status"""
        print(f"Turn: {self.get_current_player()}")
        if self.get_current_player().is_in_check:
            print("⚠️  Check!")
        print(f"Status: {self.status.value}")
        print(f"Moves made: {len(self.move_history)}")


# ============================================================================
# DEMO
# ============================================================================

def demo_chess_game():
    """Demonstrate chess game with sample moves"""

    print("\n" + "="*80)
    print(" CHESS GAME SYSTEM - DEMO ".center(80))
    print("="*80 + "\n")

    # Create game
    game = Game("Alice", "Bob")

    print("Initial board:")
    game.display_board()
    game.display_status()

    # Play some moves (Scholar's Mate)
    moves = [
        ("e2", "e4"),   # White pawn
        ("e7", "e5"),   # Black pawn
        ("f1", "c4"),   # White bishop
        ("b8", "c6"),   # Black knight
        ("d1", "h5"),   # White queen
        ("g8", "f6"),   # Black knight
        ("h5", "f7"),   # White queen checkmate!
    ]

    for i, (from_pos, to_pos) in enumerate(moves):
        print(f"\nMove {i+1}: {from_pos} → {to_pos}")

        try:
            game.make_move(from_pos, to_pos)
            game.display_board()
            game.display_status()

            if game.status != GameStatus.ACTIVE:
                break

        except InvalidMoveException as e:
            print(f"Invalid move: {e}")

    # Demonstrate undo
    if game.status != GameStatus.ACTIVE:
        print("\n" + "="*80)
        print("Demonstrating UNDO functionality...")
        print("="*80)
        game.undo_move()
        print("\nAfter undo:")
        game.display_board()
        game.display_status()

    print("\n" + "="*80)
    print(" DEMO COMPLETED ".center(80))
    print("="*80 + "\n")

    print("DESIGN PATTERNS DEMONSTRATED:")
    print("  ✓ Factory: PieceFactory (creating different piece types)")
    print("  ✓ Strategy: Each piece has its own movement strategy")
    print("  ✓ Command: Move class (encapsulates moves, supports undo)")
    print("  ✓ Template Method: Piece abstract class with template methods")
    print("\nSOLID PRINCIPLES DEMONSTRATED:")
    print("  ✓ SRP: Each class has single responsibility")
    print("  ✓ OCP: Open for extension (new pieces, variants)")
    print("  ✓ LSP: All pieces are substitutable for Piece")
    print("  ✓ ISP: Focused interfaces")
    print("  ✓ DIP: Depend on abstractions (Piece, not concrete types)")


if __name__ == "__main__":
    demo_chess_game()
