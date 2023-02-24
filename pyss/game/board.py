from .piece import piece_dict, Piece

class Chessboard:
    """Represents a chessboard

        - 8x8 grid of alternating black and white squares
        - 16 pieces per player
        - 2 players
    """
    def __init__(self):
        self.board = Chessboard.initialize_board()
        self._updated = None

    @staticmethod
    def initialize_board():
        board = [[None for _ in range(8)] for _ in range(8)]
        """Initializes the board with the starting positions of the pieces"""
        for piece in piece_dict:
            for color in piece_dict[piece]["initial_positions"]:
                for position in piece_dict[piece]["initial_positions"][color]:
                    board[position[0]][position[1]] = Piece(color, piece)
                    print(f"Initialized {color} {piece} at {position}")
        return board

    def update(self):
        """Check if the board has updated since last call. """
        if self._updated:
            self._updated = False
            return True
        return False
    
    def move(self, piece, position):
        """Moves a piece to a new position"""
        self.board[piece.position[0]][piece.position[1]] = None
        self.board[position[0]][position[1]] = piece
        piece.position = position
        self._updated = True

    @property
    def active_pieces(self):
        """Returns a list of all the pieces on the board"""
        pieces = []
        for row in self.board:
            for piece in row:
                if piece:
                    pieces.append(piece)
        return pieces
    
    def get_notation(self, position, move=None, capture=False):
        """Returns the notation of the piece at a given position"""
        piece = self.board[position[0]][position[1]]

        # TODO: Unhandled cases: pawn promotion, castling, en passant
        if piece.piece_type == "pawn":
            if capture:
                notation = f"{self.get_file(position)}x{move}"
            elif move:
                notation = move
            else:
                notation = self.get_file(position)
        else:
            if not move:
                move = f"{self.get_file(position)}{self.get_rank(position)}"
            notation = f"{piece.notation}{'x' if capture else ''}{move}"
        
        return notation
    
    @staticmethod
    def get_file(position):
        """Returns the file of a given position"""
        return chr(ord('a') + position[1])
    
    @staticmethod
    def get_rank(position):
        """Returns the rank of a given position"""
        return position[0] + 1
    
    # define index access to board
    def __getitem__(self, key):
        piece = self.board[key[0]][key[1]]
        return piece