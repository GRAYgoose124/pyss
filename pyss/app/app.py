import arcade
import logging

from ..game.board import Chessboard


logger = logging.getLogger(__name__)


class ChessApp(arcade.Window):
    def __init__(self, width=800, height=800, rotate=True):
        super().__init__(width, height, "PγssChεss")

        self.tile_size = min(width, height) // 8
        self.board_size = self.tile_size * 8
        self.offset = (
            self.width - self.board_size) // 2, (self.height - self.board_size) // 2

        self.play_board = None

        self.turn = "white"

        self.selected_piece = None
        self.old_selected_piece = None

        self._board = None
        self._rotate = rotate
        self._selected_valid_moves = []
        self._depth_search = 0

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

        def create_tile(color, i, j): return arcade.create_rectangle_filled(self.offset[0] + (i * self.tile_size + self.tile_size * 0.5),
                                                                            self.offset[1] + (
                                                                                j * self.tile_size + self.tile_size * 0.5),
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
                         self.offset[1] +
                         (ix * self.tile_size + self.tile_size * .5),
                         self.offset[0] +
                         (jx * self.tile_size + self.tile_size * .5),
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
                                                      self.offset[1] + (
                            jx * self.tile_size + self.tile_size * 0.5),
                            self.tile_size, self.tile_size, arcade.color.RED, 2)
                    self.draw_piece(i, j)

    def _draw_valid_moves(self, valid_moves, color=arcade.color.GREEN, size=1):
        for move in valid_moves:
            ix, jx = move
            if self._rotate:
                ix, jx = jx, ix
            else:
                ix, jx = ix, jx

            # draw a rectangle half the size of the tile
            arcade.draw_circle_filled(self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5),
                                      self.offset[1] + (jx * self.tile_size +
                                                        self.tile_size * 0.5),
                                      self.tile_size // ((size * 2) + 2), color)

    def draw_valid_moves(self):
        """Show valid moves for selected piece."""
        if self.selected_piece is None:
            return

        i, j = self.selected_piece

        if self._selected_valid_moves is None or len(
                self._selected_valid_moves) == 0:
            return

        if self._depth_search > 0:
            for i, valid_moves in enumerate(self._selected_valid_moves):
                # color from depth
                if i == 0:
                    color = arcade.color.GREEN
                elif i == 1:
                    color = arcade.color.YELLOW
                elif i == 2:
                    color = arcade.color.RED

                self._draw_valid_moves(valid_moves, color=color, size=i + 1)
        else:
            self._draw_valid_moves(self._selected_valid_moves)

    def on_draw(self):
        arcade.start_render()

        self.board.draw()
        self.draw_valid_moves()
        self.draw_pieces()

    def update(self, delta_time):
        if delta_time < 1 / 60:
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

            if self.selected_piece is not None:
                self.make_valid_move_handler(i, j)

            self.select_piece_handler(i, j)

    # TODO: we could cache everything until a self.board._update ...
    def select_piece_handler(self, i, j):
        """Select a piece, or deselect if already selected."""
        if self.play_board[i, j]:
            # toggle selection
            if self.selected_piece == (i, j):
                self.selected_piece = None
            else:
                self.selected_piece = i, j

            # get valid moves
            if self._depth_search:
                self._selected_valid_moves = self.play_board.valid_moves_to_depth(
                    (i, j), depth=self._depth_search)
            else:
                self._selected_valid_moves = self.play_board.valid_moves((i, j))

            logger.debug(f"Valid moves: {self._selected_valid_moves}")
        else:
            self.selected_piece = None
            self._selected_valid_moves = []

    def make_valid_move_handler(self, i, j):
        """Make a valid move."""
        if len(self._selected_valid_moves) and isinstance(self._selected_valid_moves[0], list):
            selected_valid_moves = self._selected_valid_moves[0]
        else:
            selected_valid_moves = self._selected_valid_moves

        if (i, j) in selected_valid_moves:
            self.play_board.move(self.selected_piece, (i, j))
            self.old_selected_piece = None
            self.selected_piece = (i, j)  # = None
            self._selected_valid_moves = []
            return True
