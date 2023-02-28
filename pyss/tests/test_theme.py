import os
from pathlib import Path
import pytest
import yaml

from dataclasses import asdict

from pyss.app.theme import Theme, ThemeManager, DEFAULT_THEME

class TestSuite:
    def test_theme_class(self):
        default = DEFAULT_THEME
        theme = Theme(**default)
        yml = yaml.dump(default)

        assert Theme().from_yaml(yml) == theme
        assert Theme().from_yaml(yml).to_yaml() == yml
        assert Theme().from_yaml(yml).to_dict() == default
        assert theme.to_yaml() == yml
        assert theme.to_dict() == default

    def test_thememanager_class(self):
        root = Path(os.path.dirname(os.path.realpath(__file__)))
        root = root.parent / "app"
        manager = ThemeManager(os.path.join(root, "assets/themes"))
        assert list(manager.list_themes()) == ["default"]
        assert manager.load_theme("default").to_dict() == DEFAULT_THEME