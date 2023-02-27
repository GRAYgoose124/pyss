

def get_rank(position):
    """Returns the file of a given position"""
    return chr((7 - position[1]) + ord('a'))


def get_file(position):
    """Returns the rank of a given position"""
    return 8 - position[0]


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


def move_piece_notation(piece_note, position, move, capture=False, check=False, checkmate=False):
    """Returns the notation of a piece moving to a given position

    Args:
        piece_note (str): The notation of the piece
        position (tuple): The position of the piece
        move (tuple): The position to move the piece to
        capture (bool, optional): Whether the piece is capturing another piece. Defaults to False.

    Returns:
        (str): The notation of the move
    """
    check_or_checkmate = ""
    if checkmate:
        check_or_checkmate = "#"
    elif check:
        check_or_checkmate = "+"
        
    return f"{piece_note}{'x' if capture else ''}{position_to_notation(position)}-{position_to_notation(move)}{check_or_checkmate}"


def generate_notation(piece_type, piece_note, position,
                      new_position=None, capture=False, check=False, checkmate=False, en_passant=False):
    """Returns the notation of the piece at a given position"""
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
