import arcade
import logging
import argparse

from .app import ChessApp


def argparser():
    parser = argparse.ArgumentParser()


    # sub parser for app config
    app_cfg_parser = parser.add_argument_group("App Config")
    # logging level
    app_cfg_parser.add_argument("-l", "--log-level", type=str, default="INFO",
                        help="Logging level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

    # window size
    app_cfg_parser.add_argument("-wi", "--width", type=int, default=1200,
                        help="Window width")
    app_cfg_parser.add_argument("-hi", "--height", type=int, default=800,
                        help="Window height")
    
    app_cfg_parser.add_argument("-d", "--depth", type=int, default=3,
                        help="Visual depth")
    app_cfg_parser.add_argument("-dt", "--disable-turns", action="store_true", default=False,
                        help="Disable turns")
    app_cfg_parser.add_argument("-ds", "--disable-stats", action="store_true", default=False,
                        help="Disable stats")
    
    app_cfg_parser.add_argument('-inv', '--invert', action='store_true', default=False,
                        help="Invert board orientation")
    app_cfg_parser.add_argument('-rot', '--rotate', action='store_true', default=False,
                        help="Rotate board orientation")
    
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
    args = argparser().parse_args()

    logging.basicConfig(level=args.log_level,
                        format="[%(levelname)s] %(name)s | %(message)s")

    logging.getLogger("arcade").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


    default_board_cfg = {"no_initial_pieces": False}
    default_board_cfg["interlace_pawns"] = args.interlace_pawns
    for arg in vars(args):
        if arg.startswith("no_"):
            default_board_cfg[arg] = getattr(args, arg)
    

    app = ChessApp(width=args.width, height=args.height)
    app.setup(invert=args.invert, rotate=args.rotate, depth=args.depth, stat_draw=not args.disable_stats, enable_turns=not args.disable_turns,
              board_config=default_board_cfg)

    arcade.run()


if __name__ == "__main__":
    main()
