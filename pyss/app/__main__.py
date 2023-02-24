import arcade

from ..game.board import Chessboard

       
        
class ChessApp(arcade.Window):
    def __init__(self, width=800, height=800):
        super().__init__(width, height, "PγssChεss")

        self.tile_size = min(width, height) // 8
        self.board_size = self.tile_size * 8
        self.offset = (self.width - self.board_size) // 2, (self.height - self.board_size) // 2

        self.play_board = None

    def setup(self):
        self.play_board = Chessboard()
        self.create_board()

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

        self.board = board
    
    def create_piece(self, color, i, j):
                # rotate visual i, j 90 degrees clockwise
                ix, jx = j, 7 - i
                
                arcade.draw_text(self.play_board[i, j].unicode, 
                                self.offset[0] + (ix * self.tile_size + self.tile_size * 0.5), 
                                self.offset[1] + (jx * self.tile_size + self.tile_size * 0.5), 
                                arcade.color.BLACK, font_size=self.tile_size // 2, anchor_x="center", anchor_y="center")

    def draw_pieces(self):
        for j in range(8):
            for i in range(8):
                if self.play_board[i, j]:
                    piece = self.create_piece(self.play_board[i, j].color, i, j)

    def on_draw(self):
        arcade.start_render()
        self.board.draw()
        self.draw_pieces()

    def update(self, delta_time):
        if delta_time < 1/30:
            # randomly move a piece
            return


def main():
    app = ChessApp()
    app.setup()
    arcade.run()


if __name__ == "__main__":
    main()