import arcade
import logging

from .app import ChessApp


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format="[%(levelname)s] %(name)s | %(message)s")
    logging.getLogger("arcade").setLevel(logging.INFO)

    app = ChessApp()
    app.setup()

    arcade.run()


if __name__ == "__main__":
    main()
