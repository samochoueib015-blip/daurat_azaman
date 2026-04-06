from engine.world.tile import Tile
import random

class RoadBiome:
    """
    A biome generator for road areas.
    Generates road and adjacent shoulder/dirt tiles.
    """
    def __init__(self):
        self.road_colors = [
            (80, 80, 80),
            (90, 90, 90),
        ]
        self.shoulder_colors = [
            (140, 100, 60),
            (150, 110, 70),
        ]

    def generate_tile(self, global_tile_x, global_tile_y):
        """
        Generates a Tile object for the given global tile coordinates within the Road biome.
        This simple pattern creates a central 'road' strip with 'shoulder' on either side.
        You might want to refine this with a more sophisticated noise or pattern generation
        if roads will have varying widths or design.
        """
        local_x = global_tile_x % 5
        local_y = global_tile_y % 5

        if (1 <= local_x <= 3) and (1 <= local_y <= 3):
             color = random.choice(self.road_colors)
             return Tile("road_surface", color)
        else:
             color = random.choice(self.shoulder_colors)
             return Tile("road_shoulder", color)
