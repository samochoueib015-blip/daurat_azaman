from engine.world.tile import Tile
import random

class RiverBiome:
    """
    A biome generator for river areas. (Can be integrated within other biomes later)
    """
    def __init__(self):
        self.river_water_colors = [
            (30, 120, 170),
            (25, 110, 160)
        ]
        self.riverbank_colors = [
            (150, 130, 90),
            (160, 140, 100)
        ]
    
    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the River biome.
        Simple alternating pattern for water and bank for now.
        """
        if (global_tile_x % 3 == 0) or (global_tile_y % 3 == 0):
            color = random.choice(self.river_water_colors)
            return Tile("river_water", color)
        else:
            color = random.choice(self.riverbank_colors)
            return Tile("river_bank", color)
