from __future__ import annotations

from arcade import color
from dataclasses import field, dataclass
import yaml 

from pyss.app.utils import DEPTH_COLOR_PALETTE


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


@dataclass
class Theme:
    board: dict
    stats: dict
    depth: dict

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict())

    @staticmethod
    def from_dict(theme_dict: dict) -> Theme:
        Theme(**theme_dict)

    @staticmethod
    def from_yaml(yaml: str) -> Theme:
        return Theme.from_dict(yaml.load(yaml))

    @staticmethod
    def load_yaml(yaml_file: str) -> Theme:
        with open(yaml_file, "r") as f:
            return Theme.from_yaml(f.read())
    

class ThemeManager:
    def __init__(self, theme_folder: str) -> None:
        pass

    def list_themes(self) -> list[str]:
        pass

    def load_theme(self, theme: str) -> None:
        pass
    
    def save_theme(self, theme: str) -> None:
        pass