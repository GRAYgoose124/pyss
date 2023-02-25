import pytest

from pyss.game.piece import Piece


class TestSuite:
    def test_compare(self):
        p1 = Piece("white", "pawn")
        p2 = Piece("black", "pawn")
        p3 = Piece("white", "knight")
        p4 = Piece("black", "knight")

        diff1 = p1.compare(p2)
        diff2 = p1.compare(p3)
        diff3 = p1.compare(p4)

        diff4 = p2.compare(p1)
        diff5 = p3.compare(p1)
        diff6 = p4.compare(p1)

        assert diff1 == {"color": "black"}
        assert diff2 == {"type": "knight"}
        assert diff3 == {"color": "black", "type": "knight"}

        assert diff4 == {"color": "white"}
        assert diff5 == {"type": "pawn"}
        assert diff6 == {"color": "white", "type": "pawn"}

        assert diff1 != diff4
        assert diff2 != diff5
        assert diff3 != diff6