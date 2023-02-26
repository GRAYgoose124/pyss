import arcade
import logging
import argparse

from .app import ChessApp


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--depth", type=int, default=0,
                        help="Visual depth")
    parser.add_argument("-nt", "--disable-turns", action="store_true", default=False,
                        help="Disable turns")

    return parser


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format="[%(levelname)s] %(name)s | %(message)s")
    logging.getLogger("arcade").setLevel(logging.INFO)

    args = argparser().parse_args()

    app = ChessApp()
    app.setup(depth=args.depth, enable_turns=not args.disable_turns)

    arcade.run()


if __name__ == "__main__":
    main()
