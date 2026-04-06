import pygame
from typing import Optional

class Display:
    """
    Manages the Pygame display window and screen dimensions.
    """
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    CAPTION = "Daurat Azaman (Pre-Alpha)"

    TILE_SIZE_METERS = 2
    TILE_SIZE_PIXELS = 64
    PIXELS_PER_METER = TILE_SIZE_PIXELS / TILE_SIZE_METERS 

    screen: Optional[pygame.Surface]

    def __init__(self):

        self.screen = None 

        pygame.font.init() 
        self.font = pygame.font.Font(None, 24)
        
        self.initialize() 

    def initialize(self) -> pygame.Surface:
        """Initializes the Pygame display and sets up the screen."""
        if self.screen is None:
            pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption(self.CAPTION)
            self.screen = pygame.display.get_surface() 
        return self.screen

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        """
        Draws text on the screen.
        :param text: The string to display.
        :param x: X-coordinate for the top-left corner of the text.
        :param y: Y-coordinate for the top-left corner of the text.
        :param color: RGB tuple for the text color (default white).
        """
        text_surface = self.font.render(text, True, color)

        assert self.screen is not None, "Display screen not initialized!"
        self.screen.blit(text_surface, (x, y))

    def draw_rect_outline(self, surface, color, x, y, width, height, outline_thickness=1):
        """
        Draws an outline of a rectangle on the given surface.
        :param surface: The Pygame surface to draw on.
        :param color: RGB tuple for the outline color.
        :param x: X-coordinate for the top-left corner of the rectangle.
        :param y: Y-coordinate for the top-left corner of the rectangle.
        :param width: Width of the rectangle.
        :param height: Height of the rectangle.
        :param outline_thickness: Thickness of the outline in pixels.
        """
        pygame.draw.rect(surface, color, (x, y, width, height), outline_thickness)
