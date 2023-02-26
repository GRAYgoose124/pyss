import arcade
import logging

from pyss.app.utils import DEPTH_COLOR_PALETTE

from ..game.board import Chessboard


logger = logging.getLogger(__name__)


class ChessApp(arcade.Window):
    def __init__(self, width=800, height=800):
        super().__init__(width, height, "PγssChεss")

        # app setup
        self.tile_size = min(width, height) // 8
        self.board_size = self.tile_size * 8
        self.offset = (
            self.width - self.board_size) // 2, (self.height - self.board_size) // 2

        self._display_board = self.__create_board()
        self._rotate = True
        self._invert = True
        self._depth_search = 2

        # selection
        self._selected_piece = None
        self._old_selected_piece = None
        self._selected_valid_moves = []
        # depth selection
        self._depth_bins = {}
        self._depth_drawlists = {}
        self._selected_depth_bins = None
        self._selected_depth_moves = None
        self._selected_moves_list = None

        # game
        self.play_board = Chessboard(initialize=False)
        self._turns_enabled = True
        self._turn_count = 0
        self.turn = "white"

        self._score_updated = False
        self._score_updated_on = None

    def setup(self, rotate=True, depth=0, enable_turns=True, board_config={"no_initial_pieces":False}):
        self._rotate = rotate
        self._depth_search = depth - 1 if depth else 0
        self._turns_enabled = enable_turns
        self._turn_count = 0

        self.play_board.reset(**board_config) # no_queens=True, no_knights=True, no_bishops=True)

    def on_draw(self):
        arcade.start_render()

        self._display_board.draw()
        self.__draw_pieces()
        self.__draw_valid_moves()
        self.__draw_stats()
        self.__draw_rank_and_file()

    def update(self, delta_time):
        if delta_time < 1 / 60:
            return

    # access
    def transform(self, i, j):
        """Transforms the given position to another for visual board position."""
        if self._rotate:
            ix, jx = j, i
        else:
            ix, jx = i, j

        if self._invert:
            ix, jx = 7 - ix, 7 - jx

        return ix, jx

    def get_tile(self, x, y):
        """Get the tile at the given position, handling rotation."""
        i = (x - self.offset[0]) // self.tile_size
        j = (y - self.offset[1]) // self.tile_size

        return self.transform(i, j)

    def _reset_selection(self):
        """Resets the selection of a piece."""
        self._selected_piece = None
        self._old_selected_piece = None
        self._selected_valid_moves = None

        self._selected_depth_bins = None
        self._selected_depth_moves = None
        self._selected_moves_list = None

    def _reset_depth_bins(self):
        """Resets the depth bins."""
        self._depth_bins = {}
        self._depth_drawlists = {}

    # drawing
    def __create_board(self):
        """Creates the graphical representation of the board."""
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

        return board
    
    def __draw_rank_and_file(self):
        """Draws the rank and file of the board."""
        for i in range(8):
            arcade.draw_text(str(i + 1), self.offset[0] - 20, self.offset[1] + (i * self.tile_size + self.tile_size * .5),
                             arcade.color.YELLOW, font_size=14, anchor_x="center", anchor_y="center")
            arcade.draw_text(str(i + 1), self.offset[0] + (i * self.tile_size + self.tile_size * .5), self.offset[1] - 20,
                             arcade.color.YELLOW, font_size=14, anchor_x="center", anchor_y="center")

    def __draw_stats(self):
        """Draws the stats of the game."""
        FONT_SIZE = 8
        if self._turns_enabled:
            arcade.draw_text(f"Turn: {self.turn}", 10, 10, arcade.color.RED, FONT_SIZE)

        if self.turn != self._score_updated_on:
            self._score_updated = sum([p.value for p in self.play_board._by_color["white"]]) - sum([p.value for p in self.play_board._by_color["black"]])
            self._score_updated_on = self.turn

        arcade.draw_text(f"Score: {self._score_updated}", 10, 30, arcade.color.RED, FONT_SIZE)

        # active pieces count
        arcade.draw_text(f"White: {len(self.play_board._by_color['white'])}", 10, 50, arcade.color.RED, FONT_SIZE)
        arcade.draw_text(f"Black: {len(self.play_board._by_color['black'])}", 10, 70, arcade.color.RED, FONT_SIZE)

    def __draw_piece(self, i, j):
        """Draws the piece at the given position."""
        # rotate visual i, j 90 degrees clockwise
        ix, jx = self.transform(i, j)

        if (ix + jx) % 2 == 0:
            color = arcade.color.WHITE
        else:
            color = arcade.color.BLACK

        arcade.draw_text(self.play_board[i, j].unicode,
                         self.offset[1] +
                         (ix * self.tile_size + self.tile_size * .5),
                         self.offset[0] +
                         (jx * self.tile_size + self.tile_size * .5),
                         color, font_size=self.tile_size // 2, anchor_x="center", anchor_y="center")

    def __draw_pieces(self):
        """Draws the pieces on the board."""
        for i in range(8):
            for j in range(8):
                if self.play_board[i, j]:
                    if self._selected_piece == (i, j):
                        ix, jx = self.transform(i, j)

                        arcade.draw_rectangle_outline(self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5),
                                                      self.offset[1] + (
                            jx * self.tile_size + self.tile_size * 0.5),
                            self.tile_size, self.tile_size, arcade.color.RED, 2)
                    self.__draw_piece(i, j)

    def __create_moves_list(
            self, valid_moves, color=arcade.color.GREEN, size=1):
        """Creates a list of shapes to draw the valid moves."""
        drawlist = arcade.ShapeElementList()

        for move in valid_moves:
            ix, jx = self.transform(*move)

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

    def __draw_valid_moves(self):
        """Draw valid moves for selected piece."""
        if self._selected_piece is None:
            return

        if self._selected_valid_moves is None and self._selected_depth_moves is None:
            return

        if self._depth_search > 0:
            self.__prepare_depth_map()
            if self._selected_piece not in self._depth_drawlists:
                self.__create_depth_map()

            self._depth_drawlists[self._selected_piece].draw()
        else:
            if self._selected_moves_list is None:
                self._selected_moves_list = self.__create_moves_list(
                    self._selected_valid_moves)

            self._selected_moves_list.draw()

    # def _update_depth_bins(self, changed_positions):
    #     pass

    def __prepare_depth_map(self):
        """ Build and set the depth map for the selected piece.

        Class Args Modified: TODO: properties and group into subclass?
            self._selected_depth_bins is a dict of depth: valid_moves
                This is generated here to be used by the _draw_depth_map method
            self._selected_depth_moves is a list of (depth, valid_moves) tuples
                This is generated by the play_board.valid_moves_to_depth method
            self._selected_valid_moves is a list of valid_moves a player can make
                This is usually self._selected_depth_bins[0]
        """
        # first use cached depth bins
        if self._selected_depth_bins is None:
            if self._depth_bins is not None and self._selected_piece in self._depth_bins:
                self._selected_depth_bins = self._depth_bins[self._selected_piece]

        # if no cached bins, create them
        if self._selected_depth_bins is None:
            valid_ms = [vms for vms in self._selected_depth_moves if vms[1]]
            # collect moves by depth, each set of moves is (depth, valid_moves)
            depth_bins = {}
            for move in valid_ms:
                depth = move[0]
                if depth not in depth_bins:
                    depth_bins[depth] = []
                depth_bins[depth].extend(move[1])

            # cache depth bins
            if self._depth_bins is None:
                self._depth_bins = {}

            self._depth_bins[self._selected_piece] = depth_bins

            # force rebuild valid moves
            if self._selected_valid_moves is not None:
                self._selected_valid_moves = None

            # force rebuild drawlists
            if self._selected_piece in self._depth_drawlists:
                del(self._depth_drawlists[self._selected_piece])

            self._selected_depth_bins = depth_bins

        # if valid moves not yet selected, select them
        if self._selected_valid_moves is None:
            if self._depth_search not in self._selected_depth_bins:
                try:
                    depth = min(self._selected_depth_bins.keys(), default=None)
                except ValueError:
                    depth = None
            else:
                depth = self._depth_search

            if depth is not None:
                self._selected_valid_moves = self._selected_depth_bins[depth]

    def __create_depth_map(self):
        """Create the depth map for the selected piece."""
        self._depth_drawlists[self._selected_piece] = arcade.ShapeElementList()

        depth_drawlists = []
        for i, valid_moves in self._selected_depth_bins.items():
            color = DEPTH_COLOR_PALETTE[(
                self._depth_search - i) % len(DEPTH_COLOR_PALETTE)]
            drawlist = self.__create_moves_list(
                valid_moves, color=color, size=(
                    self._depth_search - i) + 1)
            depth_drawlists.extend(drawlist)

        for s in depth_drawlists:
            self._depth_drawlists[self._selected_piece].append(s)

    # GUI interactivity
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            i, j = self.get_tile(x, y)
            logger.debug(f"Clicked pos: {x, y} -> {i, j}")

            if self._selected_piece is not None:
                self.__make_valid_move_handler(i, j)

            self.__select_piece_handler(i, j)

    # TODO: we could cache everything until a self.play_board._update ...
    def __select_piece_handler(self, i, j):
        """Select a piece, or deselect if already selected."""
        selection = self.play_board[i, j]

        # deselect/block selection if not our turn
        if selection and self._turns_enabled and selection.color != self.turn:
            self._reset_selection()
            return

        if selection:
          # toggle selection
            if self._selected_piece == (i, j):
                self._reset_selection()
                return
            else:
                self._reset_selection()
                self._selected_piece = i, j

            # get valid moves
            if self._depth_search:
                # Depth is recursive over .valid_moves()
                if self._selected_depth_moves is None:
                    self._selected_depth_moves = self.play_board.valid_moves_to_depth(
                        self._selected_piece, depth=self._depth_search)
            else:
                # Depth is 0, so just get valid moves
                self._selected_valid_moves = self.play_board.valid_moves(
                    self._selected_piece)
        else:
            self._reset_selection()

    def __make_valid_move_handler(self, i, j):
        """Make a valid move."""
        # check if any valid moves are ready
        if self._selected_valid_moves is not None and len(
                self._selected_valid_moves) and isinstance(self._selected_valid_moves[0], list):
            selected_valid_moves = self._selected_valid_moves[0][1]
        elif self._selected_valid_moves:
            selected_valid_moves = self._selected_valid_moves
        else:
            return False

        # if the attempted click is a valid move, try to make it
        if (i, j) in selected_valid_moves:
            other = self.play_board[i, j]
            # king check is a hack because for some reason selecting it swaps the turn - probably because you can't capture it
            if other and other.type == "king" and other.color != self.turn:
                return False
            if (i, j) != self._selected_piece:
                self.play_board.move(self._selected_piece, (i, j), update=True)
                # self._update_depth_bins([self.selected_piece, (i, j)])
                self._reset_depth_bins()  # TODO: rebuild instead

                # next turn
                if self._turns_enabled:
                    self._turn_count += 1
                    self.turn = "black" if self.turn == "white" else "white"

                return True
