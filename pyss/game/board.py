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
    
    def valid_moves(self, i, j):
        """Returns a list of valid moves for a given piece"""
        piece = self.board[i][j]
        if not piece:
            return []

        moves = []
        for move in piece.valid_moves(i, j):
            if self.board_valid_move(piece, (i, j), move):
                moves.append(move)
        return moves        

    def board_valid_move(self, piece, position, new_position):
        """Checks if a move is valid"""
        # check if new position is in bounds
        if new_position[0] < 0 or new_position[0] > 7 or new_position[1] < 0 or new_position[1] > 7:
            return False

        # check if move is to the same position
        if new_position == position:
            return False

        # check if move is to an occupied square by same team
        if self.board[new_position[0]][new_position[1]] and self.board[new_position[0]][new_position[1]].color == piece.color:
            return False
        
        # see if there is not a piece in the way
        if piece.type in ["rook", "bishop", "queen"]:
            # check if there is a piece in the way
            if not piece.check_path(self.board, position, new_position):
                return False

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