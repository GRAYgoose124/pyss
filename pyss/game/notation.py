
    
def get_file(position):
    """Returns the file of a given position"""
    return chr(ord('a') + position[1])


def get_rank(position):
    """Returns the rank of a given position"""
    return position[0] + 1


def generate_notation(piece_type, piece_note, position, move=None, capture=False):
        """Returns the notation of the piece at a given position"""
        if piece_type == "pawn":
            if capture:
                notation = f"{get_file(position)}x{move}"
            elif move:
                notation = move
            else:
                notation = get_file(position)
        else:
            if not move:
                move = f"{get_file(position)}{get_rank(position)}"
            notation = f"{piece_note}{'x' if capture else ''}{move}"
        
        return notation
    