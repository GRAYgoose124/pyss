import pytest

from pyss.game.notation import generate_notation

class TestSuite:
    def test_notation():
        # based on: http://www.chesscorner.com/tutorial/basic/notation/notate.htm
        # 1.f2-f4  	e7-e5
        # 2.f4xe5 	d7-d6
        # 3.e5xd6  	Bf8xd6
        # 4.g2-g3  	Qd8-g5
        # 5.Ng1-f3 	Qg5xg3+
        # 6.h2xg3  	Bd6xg3#