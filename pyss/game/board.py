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
    def initialize_board():
        board = [[None for _ in range(8)] for _ in range(8)]
        """Initializes the board with the starting positions of the pieces"""
        for piece in piece_dict:
            for color in piece_dict[piece]["initial_positions"]:
                for position in piece_dict[piece]["initial_positions"][color]:
                    board[position[0]][position[1]] = Piece(color, piece)
        return board
    
    def reset(self):
        """Resets the board to its initial state"""
        self._active_pieces = None
        self._updated = True
        self.board = Chessboard.initialize_board()

    @property
    def updated(self):
        """Check if the board has updated since last call. """
        if self._updated:
            self._updated = False
            return True
        return False
    
    @updated.setter
    def consume_update(self, value):
        """Consume the update flag"""
        self._updated = False

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