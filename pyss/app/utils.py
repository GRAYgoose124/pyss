import arcade.color as color


DEPTH_COLOR_PALETTE = [color.ANDROID_GREEN,
                       color.AMBER,
                       color.AMETHYST,
                       color.BRINK_PINK,
                       color.BLUE_GRAY,
                       color.BLUE_SAPPHIRE,
                       color.RED]


DEFAULT_THEME = {
    "board": {
        "light_tile": color.LIGHT_BROWN,
        "dark_tile": color.DARK_BROWN,
        "outline_color": color.BLACK,
        "outline_width": 2,
        "rank_and_file_font_color": color.PASTEL_ORANGE,
        "rank_and_file_font_size": 16
    },
    "stats": {
        "font_color": color.PASTEL_YELLOW,
        "white_font_color": color.LAVENDER_GRAY,
        "black_font_color": color.DARK_BLUE_GRAY,
        "font_size": 12
    },
    "depth": {
        "color_palette": DEPTH_COLOR_PALETTE
    }
}



