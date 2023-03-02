from copy import deepcopy
from dataclasses import field
from dataclasses import dataclass
from typing import Literal

from ..base import BaseBoard

Move = tuple[tuple[int, int], tuple[int, int]]


@dataclass
class DepthNode:

    """ A node in a Boardtree.

        Each node represents a different board state, by storing the
        last board node and the move that led to this board state.
    """
    parent: Literal['DepthNode'] | None = field(default=None)
    children: list['DepthNode'] | None = field(default_factory=None)
    move: Move | None = field(default=None)

    def add_child(self, child: 'DepthNode'):
        if self.children is None:
            self.children = []

        child.parent = self
        self.children.append(child)

    def remove_child(self, child: 'DepthNode'):
        child.parent = None
        self.children.remove(child)

    def __repr__(self):
        return f"{self.parent}.{self.move}"


class MoveTree:
    """ A tree of moves rooted at a given board state. (usually initial)
    """

    def __init__(self, board: BaseBoard):
        self.starting_board = deepcopy(board)

        self._root = DepthNode()
        self._real_turns = [self._root]

    def to_board(self) -> BaseBoard:
        """ Return the board state represented by the given node.

        """
        board = deepcopy(self.starting_board)

        # Build board by breadth-first traversal executing parent moves then child moves
        queue = [self._root]
        while queue:
            node = queue.pop(0)
            if node.move is not None:
                board.move(*node.move)

            if node.children is not None:
                queue.extend(node.children)

        return board

    def add_move(self, move: Move, node: DepthNode, real_turn: bool = False):
        """ Add a move to the tree, rooted at the given node.
        """
        child = DepthNode(move=move)
        node.add_child(child)

        if real_turn:
            self._real_turns.append(child)
