from engine.world.tile import Tile
import random

class CoastBiome:
    """
    A biome generator for coastal areas.
    """
    def __init__(self):
        self.sand_colors = [
            (240, 220, 170),
            (220, 200, 150),
            (200, 180, 130)
        ]
        self.water_colors = [
            (50, 150, 200),
            (40, 130, 180)
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Coast biome.
        For demonstration, mixes sand and water tiles based on simple logic (can be replaced by noise).
        """
        if (global_tile_x % 5 == 0 or global_tile_y % 5 == 0) and (global_tile_x + global_tile_y) % 2 == 0:
            color = random.choice(self.water_colors)
            return Tile("shallow_water", color)
        else:
            color = random.choice(self.sand_colors)
            return Tile("sand", color)
