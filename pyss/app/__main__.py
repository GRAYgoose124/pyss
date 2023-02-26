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
    
    # subparser to set board config with flags
    board_cfg_parser = parser.add_argument_group("Board Config")
    board_cfg_parser.add_argument("-nk", "--no-knights", action="store_true", default=False,
                                  help="Disable knights")
    board_cfg_parser.add_argument("-nb", "--no-bishops", action="store_true", default=False,
                                    help="Disable bishops")
    board_cfg_parser.add_argument("-nr", "--no-rooks", action="store_true", default=False,
                                    help="Disable rooks")
    board_cfg_parser.add_argument("-nq", "--no-queens", action="store_true", default=False,
                                    help="Disable queens")
    board_cfg_parser.add_argument("-np", "--no-pawns", action="store_true", default=False,
                                    help="Disable pawns")
    board_cfg_parser.add_argument("-nss", "--no-second-special", action="store_true", default=False,
                                    help="Only one of each special piece")
    board_cfg_parser.add_argument("-ni", "--no-initial-pieces", action="store_true", default=False,
                                    help="Disable initial pieces")
    board_cfg_parser.add_argument("-ip", "--interlace-pawns", action="store_true", default=False,
                                    help="Interlace pawns")

    return parser


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format="[%(levelname)s] %(name)s | %(message)s")
    logging.getLogger("arcade").setLevel(logging.INFO)

    args = argparser().parse_args()

    default_board_cfg = {"no_initial_pieces":False}
    for arg in vars(args):
        if arg.startswith("no_"):
            default_board_cfg[arg] = getattr(args, arg)

    app = ChessApp()
    app.setup(depth=args.depth, enable_turns=not args.disable_turns, board_config=default_board_cfg)

    arcade.run()


if __name__ == "__main__":
    main()
