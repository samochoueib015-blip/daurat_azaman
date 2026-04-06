from engine.world.tile import Tile
import random

class SnowBiome:
    """
    A biome generator for snow and ice areas.
    """
    def __init__(self):
        self.snow_colors = [
            (230, 230, 250),
            (240, 240, 255),
            (200, 200, 220)
        ]
        self.ice_colors = [
            (180, 220, 240),
            (170, 210, 230)
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Snow biome.
        """
        if (global_tile_x * global_tile_y) % 9 == 0:
            color = random.choice(self.ice_colors)
            return Tile("ice", color)
        else:
            color = random.choice(self.snow_colors)
            return Tile("snow", color)
