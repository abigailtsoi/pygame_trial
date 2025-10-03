import random

# Tile types
SAND = 0
ROCKS = 1
CRATER = 2

def generate_game_map(width, height):
    """
    Generate a game map of given width and height.
    Border tiles are always ROCKS (1).
    Interior tiles are randomly SAND (0), ROCKS (1), or CRATER (2).
    """
    if width < 3 or height < 3:
        raise ValueError("Map size must be at least 3x3 to have a border.")
    game_map = []
    for y in range(height):
        row = []
        for x in range(width):
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                row.append(ROCKS)
            else:
                # Weighted random: more sand, less rocks/crater
                tile = random.choices([SAND, ROCKS, CRATER], weights=[0.7, 0.15, 0.15])[0]
                row.append(tile)
        game_map.append(row)
    return game_map
