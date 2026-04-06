from engine.world.tile import Tile
import random

class OceanBiome:
    """
    A biome generator for ocean areas.
    """
    def __init__(self):
        self.deep_water_colors = [
            (0, 70, 120),
            (0, 60, 100),
            (0, 80, 140)
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Ocean biome.
        """
        color = random.choice(self.deep_water_colors)
        return Tile("deep_ocean", color)
