import arcade

from ..game.board import Chessboard

       
        
class ChessApp(arcade.Window):
    def __init__(self, width=800, height=800):
        super().__init__(width, height, "PγssChεss")

        self.tile_size = min(width, height) // 8
        self.board_size = self.tile_size * 8
        self.offset = (self.width - self.board_size) // 2, (self.height - self.board_size) // 2

        self.play_board = None
        self._board = None
        
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
    
    def draw_piece(self, i, j, rotate=True):
        # rotate visual i, j 90 degrees clockwise
        if not rotate:
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
                    self.draw_piece(i, j)

    def on_draw(self):
        arcade.start_render()
        self.board.draw()
        self.draw_pieces()

    def update(self, delta_time):
        if delta_time < 1/60:
            # randomly move a piece
            return

        if self.play_board.updated:
            print("Active pieces:", len(self.play_board.active_pieces))
            self.play_board.consume_update = True


def main():
    app = ChessApp()
    app.setup()
    arcade.run()




if __name__ == "__main__":
    main()