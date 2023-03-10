from ..playable import PlayableBoard
from .tree import DepthNode, MoveTree


class Chessboard(PlayableBoard):
    def __init__(self, initialize=True):
        super().__init__(initialize)

        self._move_tree = { 'white': None, 'black': None }

    def valid_move_tree(self, depth=3, tree=None):
        """Returns a tree of valid moves for the current player."""
        if depth < 0:
            return tree
        
        if tree is None:
            if self._move_tree[self.active_color] is not None:
                tree = self._move_tree[self.active_color]
            else:
                tree = MoveTree(self)
                self._move_tree[self.active_color] = tree


        for piece in self.by_color[self.active_color]:
            moves = self.get_valid_moves(piece[1])
            node = DepthNode(parent=tree._current_node)
            tree.add_move(None, node)
            for move in moves:
                tree.add_move(move, node)

                # simulate move - we don't use getters/setters here because we don't want to update the board
                move_piece = self[move]
                self.board[piece[1][0]][piece[1][1]] = None
                self.board[move[0]][move[1]] = piece[0]

                # check valid moves for piece
                self.valid_move_tree(depth=depth - 1, tree=tree)

                # undo move
                self.board[piece[1][0]][piece[1][1]] = piece[0]
                self.board[move[0]][move[1]] = move_piece

    def all_valid_moves_to_depth(self, position, depth=3, all_valid_moves=None):
        """Returns a list of valid moves for a piece to a given depth. (max=3) """
        if all_valid_moves is None:
            all_valid_moves = []

        original_piece = self[position]
        if not original_piece or depth < 0:
            return all_valid_moves

        # check valid moves for piece
        valid_moves = self.get_valid_moves(position)
        all_valid_moves.append((depth, valid_moves))
        for move in valid_moves:
            # simulate move - we don't use getters/setters here because we don't want to update the board
            move_piece = self[move]
            self.board[move[0]][move[1]] = original_piece

            # check valid moves for piece
            self.board[position[0]][position[1]] = None
            self.all_valid_moves_to_depth(
                move, depth=depth - 1, all_valid_moves=all_valid_moves)

            # undo move
            self.board[move[0]][move[1]] = move_piece
            self.board[position[0]][position[1]] = original_piece

        return all_valid_moves
