from engine.world.tile import Tile
import random

class DesertBiome:
    """
    A biome generator for desert areas.
    """
    def __init__(self):
        self.desert_colors = [
            (200, 160, 100),
            (180, 140, 80),
            (160, 120, 60)
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Desert biome.
        """
        color = random.choice(self.desert_colors)
        return Tile("desert_sand", color)
