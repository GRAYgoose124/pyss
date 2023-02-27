

def get_rank(position):
    """Returns the file of a given position"""
    return chr(position[0] + ord('a'))


def get_file(position):
    """Returns the rank of a given position"""
    return position[1] + 1


def position_to_notation(position: tuple):
    """Returns the notation of a given position

    Args:
        position (str or tuple): The position to parse
            example: "a1" or (0, 0)

    Returns:
        (str): The notation of the position
            example: "a1"
    """
    return f"{get_rank(position)}{get_file(position)}"


def notation_to_position(notation: str):
    """Returns the position of a given notation

    Args:
        notation (str): The notation to parse
            example: "a1"

    Returns:
        (tuple): The position of the notation
            example: (0, 0)
    """
    return (get_file(notation), ord(notation[0]) - ord('a'))


def generate_notation(piece_type, piece_note, position,
                      new_position=None, capture=False, check=False, checkmate=False, en_passant=False, castle=False):
    """Returns the notation of the piece at a given position"""
    if castle == "queenside":
            return "O-O-O"
    elif castle == "kingside":
        return "O-O"
    elif castle:
        return "\u2654"
        
    position = position_to_notation(position)
    if new_position:
        new_position = position_to_notation(new_position)

    if piece_type == "pawn":
        notation = f"{position}{'x' if capture else '-'}{new_position}{en_passant * ' e.p.'}"
    else:
        if not new_position:
            notation = f"{piece_note}{position}"
        else:
            notation = f"{piece_note}{position}{'x' if capture else '-'}{new_position}"

    if checkmate:
        notation += "#"
    elif check:
        notation += "+"

    return notation


def parse_notation(game_notes: str):
    pass
