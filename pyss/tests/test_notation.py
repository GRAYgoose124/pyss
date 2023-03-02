import pytest

from pyss.game.notation import generate_notation, parse_notation


class TestSuite:
    @pytest.mark.skip
    def test_notation(self):
        # based on:
        # http://www.chesscorner.com/tutorial/basic/notation/notate.htm
        game_notes = "1.f2-f4\te7-e5\n2.f4xe5\td7-d6\n3.e5xd6\tBf8xd6\n4.g2-g3\tQd8-g5\n5.Ng1-f3\tQg5xg3+\n6.h2xg3\tBd6xg3#"
        expected = [
            "1. f2 pawn moves to f4, e7 pawn moves to e5",
            "2. f4 pawn captures e5, d7 pawn moves to d6",
            "3. e5 pawn captures d6, f8 bishop captures d6",
            "4. g2 pawn moves to g3, d8 queen moves to g5",
            "5. g1 knight moves to f3, g5 queen captures g3",
            "6. h2 pawn captures g3, d6 bishop captures g3",
            " ... checkmate"]

        print(parse_notation(game_notes))

    def test_generate_notation(self):
        # TODO: These tuples are (column, row) ?
        # f2-f4
        assert generate_notation("pawn", "", (5, 1), (5, 3)) == "f2-f4"
        # e7-e5
        assert generate_notation("pawn", "", (4, 6), (4, 4)) == "e7-e5"
        # f4xe5
        assert generate_notation(
            "pawn", "", (5, 3), (4, 4), capture=True) == "f4xe5"
        # d7-d6
        assert generate_notation("pawn", "", (3, 6), (3, 5)) == "d7-d6"
        # e5xd6
        assert generate_notation(
            "pawn", "", (4, 4), (3, 5), capture=True) == "e5xd6"
        # Bf8xd6
        assert generate_notation(
            "bishop", "B", (5, 7), (3, 5), capture=True) == "Bf8xd6"
        # g2-g3
        assert generate_notation("pawn", "", (6, 1), (6, 2)) == "g2-g3"
        # Qd8-g5
        assert generate_notation("queen", "Q", (3, 7), (6, 4)) == "Qd8-g5"
        # Ng1-f3
        assert generate_notation("knight", "N", (6, 0), (5, 2)) == "Ng1-f3"
        # Qg5xg3+
        assert generate_notation("queen", "Q", (6, 4),
                                 (6, 2), capture=True, check=True) == "Qg5xg3+"
        # h2xg3
        assert generate_notation(
            "pawn", "", (7, 1), (6, 2), capture=True) == "h2xg3"
        # Bd6xg3#
        assert generate_notation(
            "bishop", "B", (3, 5), (6, 2), capture=True, checkmate=True) == "Bd6xg3#"
