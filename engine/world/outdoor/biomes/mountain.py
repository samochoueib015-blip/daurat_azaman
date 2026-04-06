from engine.world.tile import Tile
import random

class MountainBiome:
    """
    A biome generator for mountain areas.
    """
    def __init__(self):

        self.rock_colors = [
            (100, 100, 100),
            (120, 120, 120),
            (140, 140, 140),
            (110, 105, 100)
        ]

        self.snow_colors = [
            (240, 240, 240),
            (220, 220, 220)
        ]

        self.sparse_ground_colors = [
            (80, 70, 60),
            (90, 80, 70)
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Mountain biome.
        Mixes rocky terrain with occasional snow patches and sparse ground.
        """
        rnd = random.Random(global_tile_x * 1000 + global_tile_y * 1000)
        choice_val = rnd.random()

        if choice_val < 0.7:
            color = random.choice(self.rock_colors)
            return Tile("mountain_rock", color)
        elif choice_val < 0.85:
            color = random.choice(self.sparse_ground_colors)
            return Tile("mountain_sparse_ground", color)
        else:
            color = random.choice(self.snow_colors)
            return Tile("mountain_snow_patch", color)
