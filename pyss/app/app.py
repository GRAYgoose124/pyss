import os
import arcade
import arcade.gui
import logging
from pyss.app.draw_piece import load_pieces
from pyss.app.theme import ThemeManager

from pyss.app.utils import DEFAULT_THEME
from ..game.board import Chessboard


logger = logging.getLogger(__name__)




class ChessApp(arcade.Window):
    def __init__(self, width=800, height=800):
        super().__init__(width, height, "PγssChεss")

        # app setup
        self._rotate = False
        self._invert = False

        self._depth_search = 2

        self._show_stats_view = True
        self._show_theme_menu = False

            # display config
        self.tile_size = (min(width, height) - 50) // 8
        self.board_size = self.tile_size * 8
        self.offset = (
            self.width - self.board_size) // 2, (self.height - self.board_size) // 2
        
            # textures
        root = os.path.dirname(os.path.realpath(__file__))
        self._black_placeholder_texture = arcade.load_texture(
            os.path.join(root, "assets/black.png"))

        self._display_board = None
        self._rank_and_file_texture = None

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

        # ui
        # self._theme = arcade.gui.Theme()
        self.theme_manager = ThemeManager(os.path.join(root, "assets/themes"))
        self.gui_manager = None
   
        # game
        self.play_board = Chessboard(initialize=False)
        self._turns_enabled = True
        self._turn_count = 1
        self.turn = "white"

        self._score_updated = False
        self._score_updated_on = None

        self._piece_textures = None

    def setup(self, invert=None, rotate=None, depth=0, enable_turns=True, stat_draw=True, board_config={"no_initial_pieces": False}):
        if rotate is not None:
            self._rotate = rotate
        if invert is not None:
            self._invert = invert

        if self.gui_manager is None:
            self.theme_manager.setup()
            self.gui_manager = arcade.gui.UIManager(self)
            self.__create_gui()
            self.gui_manager.enable()    

        if self._piece_textures is None:
            self._piece_textures = load_pieces()

        if rotate or invert or self._display_board is None or self._rank_and_file_texture is None:
            self.__setup_theme()

        self._depth_search = depth - 1 if depth else self._depth_search
        self._turns_enabled = enable_turns
        self._show_stats_view = stat_draw

        self._reset_selection()
        self._reset_depth_bins()

        self.turn = "white"
        self._turn_count = 1

        self.play_board.reset(**board_config)

    def __setup_theme(self):
            self._display_board = self.__create_board()
            self._rank_and_file_texture = self.__create_rank_and_file()

    def on_draw(self):
        arcade.start_render()
        self._display_board.draw()
        self._rank_and_file_texture.draw()
        
        self.__draw_pieces()
        self.__draw_valid_moves()

        self.gui_manager.draw() # TODO: use this instead of __draw_stats()
        
        if self._show_stats_view:
            self.__draw_stats()

    def update(self, delta_time):
        if delta_time < 1 / 60:
            return
        
        if self.theme_manager._reload_required:
            logger.info("Loading theme...")
            self.__setup_theme()
            self.theme_manager._reload_required = False

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
    def __create_gui(self):
        gui_toolbar = arcade.gui.UIBoxLayout(vertical=False)

        # stats view and button
        stat_button = arcade.gui.UIFlatButton(
            text="\u2139", width=25, height=25, font_size=8)
        stat_button.on_click = lambda _: setattr(
            self, "_enable_stat_draw", not self._show_stats_view)
        gui_toolbar.add(stat_button.with_space_around(5))

        # new game button
        new_game_button = arcade.gui.UIFlatButton(
            text="\u21BB", width=25, height=25, font_size=8)
        new_game_button.on_click = lambda _: self.setup()
        gui_toolbar.add(new_game_button.with_space_around(5))

        # theme button and menu
        theme_button = arcade.gui.UIFlatButton(
            text="\u263C", width=25, height=25, font_size=8)
        gui_toolbar.add(theme_button.with_space_around(5))

        self.gui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="right", anchor_y="bottom", child=gui_toolbar, align_x=-25, align_y=5))
        
        # theme menu
        tmenu = arcade.gui.UIAnchorWidget(
            anchor_x="left", anchor_y="bottom", child=self.theme_manager._theme_menu, align_x=25, align_y=25)
        
        # hide theme menu with button
        theme_button.on_click = lambda _:self.gui_manager.remove(tmenu) if tmenu in list(self.gui_manager.children.values())[0] else self.gui_manager.add(tmenu)

    def __create_board(self):
        """Creates the graphical representation of the board."""
        board = arcade.ShapeElementList()

        def create_tile(color, i, j): return arcade.create_rectangle_filled(self.offset[0] + (i * self.tile_size + self.tile_size * 0.5),
                                                                            self.offset[1] + (
                                                                                j * self.tile_size + self.tile_size * 0.5),
                                                                            self.tile_size, self.tile_size, color)
        check = 0
        if self._rotate:
            check = 1

        if self._invert:
            check = 1 - check

        for i in range(8):
            for j in range(8):                
                if (i + j) % 2 == check:
                    tile = create_tile(self.theme_manager._loaded_theme['board']['dark_tile'], i, j)
                else:
                    tile = create_tile(self.theme_manager._loaded_theme['board']['light_tile'], i, j)

                board.append(tile)

        return board

    def __create_rank_and_file(self):
        """Draws the rank and file of the board."""
        drawlist = arcade.SpriteList()

        for i in range(8):
            vertical = str(i + 1)
            horizontal = chr(ord('a') + i)

            if self._invert:
                vertical = str(8 - i)
                horizontal = chr(ord('h') - i)

            if self._rotate:
                horizontal, vertical = vertical, horizontal


            drawlist.append(arcade.create_text_sprite(vertical, start_x=self.offset[0] - 20,
                                                      start_y=self.offset[1] + (
                                                          i * self.tile_size + self.tile_size * .5),
                                                      color=self.theme_manager._loaded_theme['board']['rank_and_file_font_color'], font_size=self.theme_manager._loaded_theme['board']['rank_and_file_font_size']))
            drawlist.append(arcade.create_text_sprite(horizontal, start_x=self.offset[0] + (i * self.tile_size + self.tile_size * .5),
                                                      start_y=self.offset[1] +
                                                      self.board_size + 5,
                                                      color=self.theme_manager._loaded_theme['board']['rank_and_file_font_color'], font_size=self.theme_manager._loaded_theme['board']['rank_and_file_font_size']))
        
        return drawlist
    
    def __draw_stats(self):
        """Draws the stats of the game."""
        # stats is middle right of the screen
        stats_offset = self.width - 120, self.height // 2
        box_size = (150, 340)

        # draw placeholder texture as 100x300 transparent box at the offset
        arcade.draw_texture_rectangle(
            *stats_offset, *box_size, self._black_placeholder_texture, alpha=128)

        if self._turns_enabled:
            # draw at top of stat box which is centered on stats_offset
            text_offset = stats_offset[0] - \
                box_size[0] // 4, stats_offset[1] + box_size[1] // 2 - 10
            arcade.draw_text(f"Turn {self._turn_count}: {self.turn}", *text_offset, self.theme_manager._loaded_theme['stats']['font_color'], self.theme_manager._loaded_theme['stats']['font_size'], width=100, align="center",
                                anchor_x="center", anchor_y="center")

        # update score if turn has changed
        if self.turn != self._score_updated_on:
            self._score_updated = sum([p.value for p in self.play_board._by_color["white"]]) - sum(
                [p.value for p in self.play_board._by_color["black"]])
            self._score_updated_on = self.turn

        # draw score
        score_offset = stats_offset[0] - \
            box_size[0] // 4, stats_offset[1] - box_size[1] // 2 + 10
        arcade.draw_text(f"Score: {self._score_updated}", *score_offset, self.theme_manager._loaded_theme['stats']['font_color'], self.theme_manager._loaded_theme['stats']['font_size'])

        # active pieces count
        # arcade.draw_text(f"White: {len(self.play_board._by_color['white'])}", 10, 50, FONT_COLOR, FONT_SIZE)
        # arcade.draw_text(f"Black: {len(self.play_board._by_color['black'])}", 10, 70, FONT_COLOR, FONT_SIZE)
        # active piece count
        active_piece_offset = stats_offset[0] - \
            box_size[0] // 4, stats_offset[1] - box_size[1] // 2 + 30
        arcade.draw_text(
            f"White: {len(self.play_board._by_color['white'])}", *active_piece_offset, self.theme_manager._loaded_theme['stats']['font_color'], self.theme_manager._loaded_theme['stats']['font_size'])
        arcade.draw_text(f"Black: {len(self.play_board._by_color['black'])}",
                         active_piece_offset[0], active_piece_offset[1] + 20, self.theme_manager._loaded_theme['stats']['font_color'], self.theme_manager._loaded_theme['stats']['font_size'])

        # move history
        last_move_offset = stats_offset[0] - \
            box_size[0] // 3, stats_offset[1] + box_size[1] // 2 - 40
        arcade.draw_text(f"Last 10 Moves:", *last_move_offset,
                         self.theme_manager._loaded_theme['stats']['font_color'], self.theme_manager._loaded_theme['stats']['font_size'] + 2)
        for i, move in enumerate(self.play_board.move_history[-10:]):
            actual_turn = self.play_board.move_history.index(move) + 1
            arcade.draw_text(f"  {actual_turn}:\t{move}", last_move_offset[0], last_move_offset[1] - (20 + i * 20), self.theme_manager._loaded_theme['stats']['white_font_color' if actual_turn % 2 == 0 else 'black_font_color'], self.theme_manager._loaded_theme['stats']['font_size'])
    
    def __draw_piece(self, i, j):
        """Draws the piece at the given position."""
        # rotate visual i, j 90 degrees clockwise
        ix, jx = self.transform(i, j)

        check = 0
        if self._rotate:
            check = 1

        if self._invert:
            check = 1 - check

        if (ix + jx) % 2 == check:
            color = arcade.color.WHITE
        else:
            color = arcade.color.BLACK

        # arcade.draw_text(self.play_board[i, j].unicode,
        #                     self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5),
        #                     self.offset[1] + (jx * self.tile_size + self.tile_size * 0.5),
        #                     color, self.tile_size * .5, width=self.tile_size, align="center", anchor_x="center", anchor_y="center")
        piece = self.play_board[i, j]
        tex = self._piece_textures[piece.color][piece.type]
        tex.set_position(self.offset[0] + (i * self.tile_size + self.tile_size * 0.5),
                    self.offset[1] + (j * self.tile_size + self.tile_size * 0.5))
        tex.scale = self.tile_size / 170
        tex.draw()

    def __draw_pieces(self):
        """Draws the pieces on the board."""
        for i in range(8):
            for j in range(8):
                if self.play_board[i, j]:
                    if self._selected_piece == (i, j):
                        ix, jx = self.transform(i, j)

                        arcade.draw_rectangle_outline(
                            self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5),
                            self.offset[1] + (jx * self.tile_size + self.tile_size * 0.5),
                            self.tile_size, self.tile_size, arcade.color.RED, 2
                        )
                        
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
                del (self._depth_drawlists[self._selected_piece])

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
            color = self.theme_manager._loaded_theme['depth']['color_palette'][(
                self._depth_search - i) % len(self.theme_manager._loaded_theme['depth']['color_palette'])]
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

        if selection:
            # deselect/block selection if not our turn
            if self._turns_enabled and selection.color != self.turn:
                self._reset_selection()
                return
            
            # only king can move if check
            if self.play_board._check:
                if selection.type != 'king':
                    self._reset_selection()
                    return
                else:
                    # TODO: other pieces can move if they can block check
                    # TODO: king can move, but not into another check, if no available moves - checkmate
                    pass 

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
