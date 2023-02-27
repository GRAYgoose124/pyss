import os
import arcade

def create_rook_shape():
    shape = arcade.ShapeElementList()
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 50, arcade.color.WHITE))
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 10, arcade.color.BLACK))
    shape.append(arcade.create_rectangle_filled(0, 0, 10, 50, arcade.color.BLACK))
    return shape

def create_knight_shape():
    shape = arcade.ShapeElementList()
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 50, arcade.color.WHITE))
    shape.append(arcade.create_ellipse_filled(0, 0, 50, 50, arcade.color.BLACK))
    return shape

def create_bishop_shape():
    shape = arcade.ShapeElementList()
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 50, arcade.color.WHITE))
    shape.append(arcade.create_ellipse_filled(0, 0, 50, 50, arcade.color.BLACK))
    shape.append(arcade.create_ellipse_filled(0, 0, 40, 40, arcade.color.WHITE))
    return shape

def create_queen_shape():
    shape = arcade.ShapeElementList()
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 50, arcade.color.WHITE))
    shape.append(arcade.create_ellipse_filled(0, 0, 50, 50, arcade.color.BLACK))
    shape.append(arcade.create_ellipse_filled(0, 0, 40, 40, arcade.color.WHITE))
    shape.append(arcade.create_ellipse_filled(0, 0, 30, 30, arcade.color.BLACK))
    return shape

def create_king_shape():
    shape = arcade.ShapeElementList()
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 50, arcade.color.WHITE))
    shape.append(arcade.create_ellipse_filled(0, 0, 50, 50, arcade.color.BLACK))
    shape.append(arcade.create_ellipse_filled(0, 0, 40, 40, arcade.color.WHITE))
    shape.append(arcade.create_ellipse_filled(0, 0, 30, 30, arcade.color.BLACK))
    shape.append(arcade.create_ellipse_filled(0, 0, 20, 20, arcade.color.WHITE))
    return shape

def create_pawn_shape():
    shape = arcade.ShapeElementList()
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 50, arcade.color.WHITE))
    shape.append(arcade.create_rectangle_filled(0, 0, 50, 10, arcade.color.BLACK))
    return shape


def load_pieces():
    root = os.path.dirname(os.path.realpath(__file__))
    path = 'assets/1024px-Chess_Pieces_Sprite.png'
    filename = os.path.join(root, path)
    sprite_size = 1024 // 6, 170
    pieces = {'white': {}, 'black': {}}
    

    build_sprite = lambda x, y: arcade.Sprite(
        filename=filename,
        image_x=x,
        image_y=y,
        image_width=sprite_size[0],
        image_height=sprite_size[1])

    pieces['white']['king'] = build_sprite(0, 0)
    pieces['white']['queen'] = build_sprite(sprite_size[0], 0)
    pieces['white']['bishop'] = build_sprite(2*sprite_size[0], 0)
    pieces['white']['knight'] = build_sprite(3*sprite_size[0], 0)
    pieces['white']['rook'] = build_sprite(4*sprite_size[0], 0)
    pieces['white']['pawn'] = build_sprite(5*sprite_size[0], 0)

    pieces['black']['king'] = build_sprite(0, sprite_size[1])
    pieces['black']['queen'] = build_sprite(sprite_size[0], sprite_size[1])
    pieces['black']['bishop'] = build_sprite(2*sprite_size[0], sprite_size[1])
    pieces['black']['knight'] = build_sprite(3*sprite_size[0], sprite_size[1])
    pieces['black']['rook'] = build_sprite(4*sprite_size[0], sprite_size[1])
    pieces['black']['pawn'] = build_sprite(5*sprite_size[0], sprite_size[1])

    return pieces