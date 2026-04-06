import pygame

class Tile:
    def __init__(self, tile_type, color=(0, 255, 0)):
        self.tile_type = tile_type
        self.color = color

    def draw(self, surface, x, y, size):
        """
        Draws the tile on the given surface at the specified (x, y) pixel coordinates.
        'size' refers to the pixel dimension of the tile (e.g., Display.TILE_SIZE_PIXELS).
        """
        pygame.draw.rect(surface, self.color, (x, y, size, size))

    def __repr__(self):
        return f"Tile(type='{self.tile_type}', color={self.color})"
