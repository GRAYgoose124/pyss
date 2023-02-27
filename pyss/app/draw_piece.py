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