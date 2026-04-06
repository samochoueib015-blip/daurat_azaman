from engine.world.tile import Tile
import random

class FieldsBiome:
    """
    A simple biome generator for 'fields'.
    """
    def __init__(self):

        self.grass_colors = [
            (50, 150, 50),
            (70, 170, 70),
            (90, 190, 90)
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Fields biome.
        For now, just random grass color.
        """
        color = random.choice(self.grass_colors)
        return Tile("grass", color)
