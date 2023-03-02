from copy import deepcopy
from dataclasses import field
from dataclasses import dataclass
from pyss.game.board import Chessboard


Move = tuple[tuple[int, int], tuple[int, int]]


@dataclass
class Node:

    """ A node in a Boardtree.

        Each node represents a different board state, by storing the
        last board node and the move that led to this board state.
    """
    parent: 'Node' | None = field(default=None)
    children: list['Node'] | None = field(default_factory=None)
    move: Move | None = field(default=None)

    def add_child(self, child: 'Node'):
        if self.children is None:
            self.children = []
            
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: 'Node'):
        child.parent = None
        self.children.remove(child)

    def __repr__(self):
        return f"{self.parent}.{self.move}"
    


class MoveTree:
    """ A tree of moves rooted at a given board state. (usually initial)
    """
    def __init__(self, board: Chessboard):
        self.starting_board = deepcopy(board)

        self._root = Node()

    def to_board(self) -> Chessboard:
        """ Return the board state represented by the given node.

        """
        board = deepcopy(self.starting_board)
        root = self._root

        while root.children:
            board.move(*root.move)            
            for child in root.children:
                child.move
            board.move(*move)
            root = root.children[0]

    def add_move(self, move: Move, node: Node):
        """ Add a move to the tree, rooted at the given node.
        """
        child = Node(move=move)
        node.add_child(child)
