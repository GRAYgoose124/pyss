import arcade
import logging

from pyss.app.utils import DEPTH_COLOR_PALETTE

from ..game.board import Chessboard


logger = logging.getLogger(__name__)


class ChessApp(arcade.Window):
    def __init__(self, width=800, height=800):
        super().__init__(width, height, "PγssChεss")

        self.tile_size = min(width, height) // 8
        self.board_size = self.tile_size * 8
        self.offset = (
            self.width - self.board_size) // 2, (self.height - self.board_size) // 2

        self.play_board = None

        self.turn = "white"

        self.selected_piece = None
        self.old_selected_piece = None
        self._selected_valid_moves = []
        self._depth_bins = {}
        self._depth_drawlists = {}
        self._selected_depth_bins = None
        self._selected_depth_moves = None
        self._selected_moves_list = None

        self._board = None
        self._rotate = True

        self._depth_search = 2

    def setup(self, rotate=True, depth=0):
        self._rotate = rotate
        self._depth_search = depth - 1 if depth else 0

        self.play_board = Chessboard()
        self._create_board()

    def on_draw(self):
        arcade.start_render()

        self.board.draw()
        self.draw_valid_moves()
        self.draw_pieces()

    def update(self, delta_time):
        if delta_time < 1 / 60:
            return

    @property
    def board(self):
        if self._board is None:
            self._create_board()
        return self._board

    def reset_selection(self):
        self.selected_piece = None
        self.old_selected_piece = None
        self._selected_depth_bins = None
        self._selected_depth_moves = None
        self._selected_moves_list = None
        self._selected_valid_moves = None

    def reset_depth_bins(self):
        self._depth_bins = {}
        self._depth_drawlists = {}

    def _create_board(self):
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

    def _draw_piece(self, i, j):
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
                    self._draw_piece(i, j)

    def _create_moves_list(
            self, valid_moves, color=arcade.color.GREEN, size=1):
        drawlist = arcade.ShapeElementList()

        for move in valid_moves:
            ix, jx = move
            if self._rotate:
                ix, jx = jx, ix
            else:
                ix, jx = ix, jx

            # # draw a rectangle half the size of the tile
            # arcade.draw_circle_filled(self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5),
            #                           self.offset[1] + (jx * self.tile_size +
            #                                             self.tile_size * 0.5),
            #                           self.tile_size // ((size ** 1.5) + 2), color)
            # add to drawlist instead of drawing
            drawlist.append(arcade.create_ellipse_filled(self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5),
                                                         self.offset[1] + (
                jx * self.tile_size + self.tile_size * 0.5),
                self.tile_size // ((size ** 1.5) + 2), self.tile_size // ((size ** 1.5) + 2), color))
        return drawlist

    def _draw_valid_depth(self):
        # filter out [] from self._selected_valid_moves
        if self._selected_depth_bins is None:
            valid_ms = [vms for vms in self._selected_depth_moves if vms[1]]
            # collect moves by depth, each set of moves is (depth, valid_moves)
            depth_bins = {}
            for move in valid_ms:
                depth = move[0]
                if depth not in depth_bins:
                    depth_bins[depth] = []
                depth_bins[depth].extend(move[1])

            if self._depth_search not in depth_bins:
                return

            self._selected_depth_bins = depth_bins

        if self._selected_valid_moves is None:
            self._selected_valid_moves = self._selected_depth_bins[self._depth_search]

        # create drawlist for each depth and combine int ShapeElementList
        if self.selected_piece not in self._depth_drawlists:
            self._depth_drawlists[self.selected_piece] = arcade.ShapeElementList(
            )
            depth_drawlists = []
            for i, valid_moves in self._selected_depth_bins.items():
                color = DEPTH_COLOR_PALETTE[(
                    self._depth_search - i) % len(DEPTH_COLOR_PALETTE)]
                drawlist = self._create_moves_list(
                    valid_moves, color=color, size=(
                        self._depth_search - i) + 1)
                depth_drawlists.extend(drawlist)
            for s in depth_drawlists:
                self._depth_drawlists[self.selected_piece].append(s)

        self._depth_drawlists[self.selected_piece].draw()

    def draw_valid_moves(self):
        """Show valid moves for selected piece."""
        if self.selected_piece is None:
            return

        if self._selected_valid_moves is None and self._selected_depth_moves is None:
            return

        if self._depth_search > 0:
            self._draw_valid_depth()
        else:
            if self._selected_moves_list is None:
                self._selected_moves_list = self._create_moves_list(
                    self._selected_valid_moves)
            self._selected_moves_list.draw()

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

    # TODO: we could cache everything until a self.play_board._update ...
    def select_piece_handler(self, i, j):
        """Select a piece, or deselect if already selected."""
        if self.play_board[i, j]:
          # toggle selection
            if self.selected_piece == (i, j):
                if self._depth_search and (i, j) not in self._depth_bins:
                    self._depth_bins[(i, j)] = self._selected_depth_bins
                self.reset_selection()
                return
            else:
                if self._depth_search and self.selected_piece not in self._depth_bins:
                    self._depth_bins[self.selected_piece] = self._selected_depth_bins
                self.reset_selection()
                self.selected_piece = i, j

            if self._depth_search:
                if self._selected_depth_bins is None:
                    if self.selected_piece and self.selected_piece in self._depth_bins and self._depth_bins[
                            self.selected_piece]:
                        self._selected_depth_bins = self._depth_bins[self.selected_piece]
                        # get min key in self._selected_depth_bins,
                        # TODO: ISSUE / Theoretically losing the depth at the edge is part of the cause
                        # for the top edge failure.
                        min_key = min(self._selected_depth_bins.keys())
                        self._selected_depth_moves = self._selected_depth_bins[min_key]
                        return

                self._selected_depth_moves = self.play_board.valid_moves_to_depth(
                    self.selected_piece, depth=self._depth_search)
            else:
                self._selected_valid_moves = self.play_board.valid_moves(
                    self.selected_piece)
        else:
            self.reset_selection()

    def make_valid_move_handler(self, i, j):
        """Make a valid move."""
        if self._selected_valid_moves is not None and len(
                self._selected_valid_moves) and isinstance(self._selected_valid_moves[0], list):
            selected_valid_moves = self._selected_valid_moves[0][1]
        elif self._selected_valid_moves:
            selected_valid_moves = self._selected_valid_moves
        else:
            return False

        if (i, j) in selected_valid_moves:
            if (i, j) != self.selected_piece:
                self.play_board.move(self.selected_piece, (i, j))
                self.reset_depth_bins()
                return True
