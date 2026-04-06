from engine.world.tile import Tile
import random

class ForestBiome:
    """
    A biome generator for forest areas.
    """
    def __init__(self):
        self.forest_floor_colors = [
            (30, 90, 30),
            (40, 100, 40),
            (50, 110, 50)
        ]
        self.tree_colors = [
            (0, 50, 0),
            (0, 60, 0)
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Forest biome.
        """
        if (global_tile_x % 3 == 0 and global_tile_y % 3 == 0) or \
           ((global_tile_x + 1) % 3 == 0 and (global_tile_y + 1) % 3 == 0):
            color = random.choice(self.tree_colors)
            return Tile("tree_canopy", color)
        else:
            color = random.choice(self.forest_floor_colors)
            return Tile("forest_floor", color)
