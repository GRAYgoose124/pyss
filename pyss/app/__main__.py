import arcade
import logging

from ..game.board import Chessboard


APP_NAME = "PγssChεss"
logger = logging.getLogger(APP_NAME)
  
        
class ChessApp(arcade.Window):
    def __init__(self, width=800, height=800, rotate=True):
        super().__init__(width, height, APP_NAME)

        self.tile_size = min(width, height) // 8
        self.board_size = self.tile_size * 8
        self.offset = (self.width - self.board_size) // 2, (self.height - self.board_size) // 2

        self.play_board = None
        self._board = None
        self._rotate = rotate
        self._selected_valid_moves = []

        self.selected_piece = None
        self.old_selected_piece = None
        
    def setup(self):
        self.play_board = Chessboard()
        self.create_board()

    @property
    def board(self):
        if self._board is None:
            self.create_board()
        return self._board

    def create_board(self):
        board = arcade.ShapeElementList()

        create_tile = lambda color, i, j: arcade.create_rectangle_filled(self.offset[0] + (i * self.tile_size + self.tile_size * 0.5), 
                                                                   self.offset[1] + (j * self.tile_size + self.tile_size * 0.5), 
                                                                   self.tile_size, self.tile_size, color)
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    tile = create_tile(arcade.color.BLACK, i, j)
                else:
                    tile = create_tile(arcade.color.WHITE, i, j)

                board.append(tile)

        self._board = board
    
    def draw_piece(self, i, j):
        # rotate visual i, j 90 degrees clockwise
        if not self._rotate:
            ix, jx = i, j
        else:
            ix, jx = j, i
        
        if (i + j) % 2 == 0:
            color = arcade.color.WHITE
        else:
            color = arcade.color.BLACK

        arcade.draw_text(self.play_board[i, j].unicode, 
                        self.offset[1] + (ix * self.tile_size + self.tile_size * .5), 
                        self.offset[0] + (jx * self.tile_size + self.tile_size * .5), 
                        color, font_size=self.tile_size // 2, anchor_x="center", anchor_y="center")

    def draw_pieces(self):
        for i in range(8):
            for j in range(8):
                if self.play_board[i, j]:
                    if self.selected_piece == (i, j):
                        if self._rotate:
                            ix, jx = j, i
                        else:
                            ix, jx = i, j

                        arcade.draw_rectangle_outline(self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5), 
                                                      self.offset[1] + (jx * self.tile_size + self.tile_size * 0.5), 
                                                      self.tile_size, self.tile_size, arcade.color.RED, 2)
                    self.draw_piece(i, j)

    def draw_valid_moves(self):
        """Show valid moves for selected piece."""
        if self.selected_piece is None:
            return

        i, j = self.selected_piece
        if self.selected_piece != self.old_selected_piece:
            self._selected_valid_moves = self.play_board.valid_moves(i, j)
            self.old_selected_piece = self.selected_piece
        
        if self._selected_valid_moves is None:
            return

        for move in self._selected_valid_moves:
            ix, jx = move
            if self._rotate:
                ix, jx = jx, ix
            else:
                ix, jx = ix, jx

            # draw a rectangle half the size of the tile
            arcade.draw_circle_filled(self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5), 
                                      self.offset[1] + (jx * self.tile_size + self.tile_size * 0.5), 
                                      self.tile_size // 4, arcade.color.GREEN)
    def on_draw(self):
        arcade.start_render()
        self.board.draw()
        self.draw_valid_moves()

        self.draw_pieces()

    def update(self, delta_time):
        if delta_time < 1/60:
            return

    def get_tile(self, x, y):
        """Get the tile at the given position, handling rotation."""
        i = (x - self.offset[0]) // self.tile_size
        j = (y - self.offset[1]) // self.tile_size
        if self._rotate:
            return j, i
        
        return i, j

    # interaction
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            i, j = self.get_tile(x, y)
            logger.debug(f"Clicked pos: {x, y} -> {i, j}")

            made_move = False
            if self.selected_piece is not None:
                made_move = self.make_valid_move_handler(i, j)

            if not made_move:
                self.select_piece_handler(i, j)

    def select_piece_handler(self, i, j):
        """Select a piece, or deselect if already selected."""
        if self.play_board[i, j]:
            if self.selected_piece == (i, j):
                self.selected_piece = None
            else:
                self.selected_piece = i, j
                print(self.play_board[i, j].unicode)
        else:
            self.selected_piece = None
    
    def make_valid_move_handler(self, i, j):
        """Make a valid move."""
        if (i, j) in self._selected_valid_moves:
            self.play_board.move(self.selected_piece, (i, j))
            self.selected_piece = None
            self.old_selected_piece = None
            self._selected_valid_moves = []
            return True
        
  

def main():
    logging.basicConfig(level=logging.DEBUG, 
                        format="[%(levelname)s] %(name)s | %(message)s")
    logging.getLogger("arcade").setLevel(logging.INFO)

    app = ChessApp()
    app.setup()

    arcade.run()


if __name__ == "__main__":
    main()