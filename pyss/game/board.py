from functools import lru_cache
from .piece import piece_dict, Piece


class Chessboard:
    """Represents a chessboard

        - 8x8 grid of alternating black and white squares
        - 16 pieces per player
        - 2 players
    """
    def __init__(self):
        self.reset()

    @staticmethod
    def initialize_board(no_pawns=False, no_left_pawns=False):
        board = [[None for _ in range(8)] for _ in range(8)]
        """Initializes the board with the starting positions of the pieces"""
        for piece in piece_dict:
            if no_pawns and piece == "pawn":
                continue
            for color in piece_dict[piece]["initial_positions"]:
                for position in piece_dict[piece]["initial_positions"][color]:
                    if no_left_pawns and piece == "pawn":
                        if position[1] < 4:
                            continue
                    board[position[0]][position[1]] = Piece(color, piece)
        return board
    
    def reset(self):
        """Resets the board to its initial state"""
        self._active_pieces = None
        self.board = Chessboard.initialize_board(no_left_pawns=True)

    @property
    def active_pieces(self):
        """Returns a list of all the pieces on the board"""
        if self._active_pieces:
            return self._active_pieces

        pieces = {}
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece:
                    pieces[piece] = (i, j)

        return pieces
    
    @lru_cache(maxsize=32)
    def valid_moves(self, i, j):
        """Returns a list of valid moves for a given piece"""
        piece = self.board[i][j]
        if not piece:
            return []

        moves = []
        for move in piece.valid_moves(i, j):
            if piece.type in ["bishop", "rook", "queen"]:
                if self.check_path((i, j), move):
                    moves.append(move)
            elif self.board_valid_move((i, j), move):
                moves.append(move)
        return moves     
       
    def board_valid_move(self, position, new_position):
        """Checks if a move is valid"""
        # check if new position is in bounds
        if new_position[0] < 0 or new_position[0] > 7 or new_position[1] < 0 or new_position[1] > 7:
            return False

        # check if move is to the same position
        if new_position == position:
            return False

        # check if move is to an occupied square by same team
        if self.board[new_position[0]][new_position[1]] and self.board[new_position[0]][new_position[1]].color == self.board[position[0]][position[1]].color:
            return False

        return True

    def check_path(self, position, new_position):
        """ Returns true if there are no pieces in a straight line between two positions. """
        # check if move is valid
        if not self.board_valid_move(position, new_position):
            return False

        # get the direction of the move
        direction = (new_position[0] - position[0], new_position[1] - position[1])

        # get the number of spaces between the two positions
        distance = max(abs(direction[0]), abs(direction[1]))

        # check if the path is clear
        seen_enemy = False
        for i in range(distance):
            # get the position of the next space in the path
            next_position = (position[0] + (i + 1) * direction[0] // distance, position[1] + (i + 1) * direction[1] // distance)
            # check if the space is occupied by a friendly piece
            if self.board[next_position[0]][next_position[1]] and self.board[next_position[0]][next_position[1]].color == self.board[position[0]][position[1]].color:
                return False
            # if it's an enemy piece, chekc if we've already seen one or set that we have
            elif self.board[next_position[0]][next_position[1]]:
                if seen_enemy:
                    return False
                seen_enemy = True

        return True

    def move(self, piece, position):
        """ Unsafely moves a piece destroying any piece that is in the destionatoin. """
        self.board[piece.position[0]][piece.position[1]] = None
        # if move is going to capture a piece, remove it from the active pieces
        if self.board[position[0]][position[1]]:
            self._active_pieces.remove(self.board[position[0]][position[1]])

        self.board[position[0]][position[1]] = piece
        piece.position = position
        self._updated = True
    
    # define index access to board
    def __getitem__(self, key):
        piece = self.board[key[0]][key[1]]
        return piece