import pygame
from engine.world.tile import Tile
from engine.display import Display

class Chunk:
    """
    Represents a single chunk of the game world, consisting of a grid of tiles.
    """
    CHUNK_SIZE_TILES = 5

    def __init__(self, world_x, world_y):
        """
        Initializes a chunk.
        :param world_x: The x-coordinate of the chunk in the world grid (not pixels).
        :param world_y: The y-coordinate of the chunk in the world grid (not pixels).
        """
        self.world_x = world_x
        self.world_y = world_y
        self.tiles = [[None for _ in range(self.CHUNK_SIZE_TILES)] for _ in range(self.CHUNK_SIZE_TILES)]
        self.is_generated = False

    def populate(self, biome_generator_function):
        """
        Populates the chunk's tiles using a provided biome generation function.
        :param biome_generator_function: A function that takes (tile_x, tile_y) and returns a Tile object.
        """
        for y in range(self.CHUNK_SIZE_TILES):
            for x in range(self.CHUNK_SIZE_TILES):
                global_tile_x = self.world_x * self.CHUNK_SIZE_TILES + x
                global_tile_y = self.world_y * self.CHUNK_SIZE_TILES + y
                self.tiles[y][x] = biome_generator_function(global_tile_x, global_tile_y)
        self.is_generated = True

    def draw(self, surface, camera_offset_x, camera_offset_y):
        """
        Draws the chunk's tiles on the given surface, applying a camera offset.
        :param surface: The Pygame surface to draw on.
        :param camera_offset_x: The camera's x-offset (in pixels).
        :param camera_offset_y: The camera's y-offset (in pixels).
        """
        chunk_world_pixel_x = self.world_x * self.CHUNK_SIZE_TILES * Display.TILE_SIZE_PIXELS
        chunk_world_pixel_y = self.world_y * self.CHUNK_SIZE_TILES * Display.TILE_SIZE_PIXELS

        for y in range(self.CHUNK_SIZE_TILES):
            for x in range(self.CHUNK_SIZE_TILES):
                tile = self.tiles[y][x]
                if tile:
                    tile_pixel_x_in_chunk = x * Display.TILE_SIZE_PIXELS
                    tile_pixel_y_in_chunk = y * Display.TILE_SIZE_PIXELS

                    screen_x = chunk_world_pixel_x + tile_pixel_x_in_chunk - camera_offset_x
                    screen_y = chunk_world_pixel_y + tile_pixel_y_in_chunk - camera_offset_y

                    tile.draw(surface, screen_x, screen_y, Display.TILE_SIZE_PIXELS)
