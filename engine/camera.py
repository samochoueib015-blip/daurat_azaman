import pygame
from engine.display import Display

class Camera:
    """
    Manages the screen-by-screen camera movement, like in classic Zelda games.
    The camera snaps to precise screen coordinates.
    """
    def __init__(self, player_ref):
        self.player = player_ref
        
        self.screen_world_x = 0
        self.screen_world_y = 0

        self._align_to_screen_grid()

    def _align_to_screen_grid(self):
        """
        Aligns the camera's screen_world_x/y to the grid based on player's position.
        This effectively "snaps" the camera to the correct screen.
        """
        self.screen_world_x = int(self.player.world_x // Display.SCREEN_WIDTH) * Display.SCREEN_WIDTH
        self.screen_world_y = int(self.player.world_y // Display.SCREEN_HEIGHT) * Display.SCREEN_HEIGHT

    def update(self):
        """
        Checks if the player has crossed a screen threshold and updates the camera position if so.
        Also adjusts player position relative to the new screen boundaries to prevent them from getting stuck.
        """
        if self.player.world_x >= self.screen_world_x + Display.SCREEN_WIDTH:
            self.screen_world_x += Display.SCREEN_WIDTH
            self.player.world_x = self.screen_world_x + (self.player.width // 2)

        elif self.player.world_x < self.screen_world_x:
            self.screen_world_x -= Display.SCREEN_WIDTH
            self.player.world_x = self.screen_world_x + Display.SCREEN_WIDTH - (self.player.width // 2)

        if self.player.world_y >= self.screen_world_y + Display.SCREEN_HEIGHT:
            self.screen_world_y += Display.SCREEN_HEIGHT
            self.player.world_y = self.screen_world_y + (self.player.height // 2)

        elif self.player.world_y < self.screen_world_y:
            self.screen_world_y -= Display.SCREEN_HEIGHT
            self.player.world_y = self.screen_world_y + Display.SCREEN_HEIGHT - (self.player.height // 2)

    def get_offset(self):
        """
        Returns the top-left world coordinates of the current screen view.
        This serves as the offset for drawing all world elements.
        """
        return self.screen_world_x, self.screen_world_y
