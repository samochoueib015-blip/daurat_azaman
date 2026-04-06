VECTOR_TO_DIRECTION = {
    (0, -1): "N",
    (1, -1): "NE",
    (1, 0):  "E",
    (1, 1):  "SE",
    (0, 1):  "S",
    (-1, 1): "SW",
    (-1, 0): "W",
    (-1, -1):"NW",
    (0, 0):  None
}

def get_direction_from_vector(dx, dy, current_direction_key):
    """
    Determines the direction string from a movement vector (dx, dy).

    Args:
        dx (int): Change in x-coordinate (-1, 0, or 1).
        dy (int): Change in y-coordinate (-1, 0, or 1).
        current_direction_key (str): The player's current/last known direction.
                                     Used if there's no movement (dx=0, dy=0)
                                     or if the vector is not recognized.

    Returns:
        str: The determined direction string (e.g., "N", "SE", "W").
    """
    if (dx, dy) == (0, 0):
        return current_direction_key
    
    direction = VECTOR_TO_DIRECTION.get((dx, dy))
    
    if direction:
        return direction
    else:

        print(f"Warning: Unrecognized movement vector ({dx}, {dy}) given to get_direction_from_vector. "
              f"Maintaining current direction '{current_direction_key}'.")
        return current_direction_key
