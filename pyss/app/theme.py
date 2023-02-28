from __future__ import annotations
import os

from arcade import color
from dataclasses import asdict, field, dataclass, fields
from dataclass_wizard import YAMLWizard
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
class Theme(YAMLWizard):
    board: dict = field(default_factory=lambda: DEFAULT_THEME["board"])
    stats: dict = field(default_factory=lambda: DEFAULT_THEME["stats"])
    depth: dict = field(default_factory=lambda: DEFAULT_THEME["depth"])

    def from_yaml_file(self, file: str, decoder: type = yaml.FullLoader) -> Theme:
        with open(file) as f:
            return Theme(**yaml.load(f.read(), Loader=decoder))

    def from_yaml(self, yml: str, decoder: type = yaml.FullLoader) -> Theme:
        return Theme(**yaml.load(yml, Loader=decoder))
    
    def to_dict(self) -> dict:
        return asdict(self)

    def __getitem__(self, key: str) -> dict:
        return getattr(self, key)

class ThemeManager:
    def __init__(self, theme_folder: str) -> None:
        self._theme_folder = theme_folder
        self._loaded_theme = None

    def list_themes(self) -> list[str]:
        for theme in os.listdir(self._theme_folder):
            if theme.endswith(".yml"):
                yield theme[:-4]

    def load_theme(self, theme: str) -> Theme:
        if ".yml" not in theme:
            theme += ".yml"

        self._loaded_theme = Theme().from_yaml_file(os.path.join(self._theme_folder, theme))
        return self._loaded_theme
    
    def save_theme(self, theme: str) -> None:
        if ".yml" not in theme:
            theme += ".yml"

        Theme.to_yaml_file(self._loaded_theme, os.path.join(self._theme_folder, theme))

    def delete_theme(self, theme: str) -> None:
        if ".yml" not in theme:
            theme += ".yml"

        os.remove(os.path.join(self._theme_folder, theme))


class ThemeBuilder:
    pass