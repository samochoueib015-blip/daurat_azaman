import pygame
import os
import math
from engine.world.objects.inventory.chest_inventory import ChestInventory
from typing import Optional, Tuple
from engine.items.base_item import BaseItem 
from engine.display import Display
from game_config import CHEST_SPRITE_CLOSED_PATH, CHEST_SPRITE_OPEN_PATH 

class Chest:
    """
    Represents an interactive chest object in the world.
    Contains an inventory and can be opened by the player.
    """
    def __init__(self, chest_id: str, x: float, y: float, 
                 width: int = Display.TILE_SIZE_PIXELS, 
                 height: int = Display.TILE_SIZE_PIXELS):
        self.chest_id = chest_id
        self.world_x = x
        self.world_y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.world_x, self.world_y, self.width, self.height)
        self.inventory = ChestInventory(chest_id)
        self.is_open = False
        self._sprite_closed: Optional[pygame.Surface] = None
        self._sprite_open: Optional[pygame.Surface] = None
        self._load_sprites()

    def _load_sprites(self):
        """Loads closed and open chest sprites."""
        try:
            game_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            
            closed_path = os.path.join(game_root_dir, CHEST_SPRITE_CLOSED_PATH)
            open_path = os.path.join(game_root_dir, CHEST_SPRITE_OPEN_PATH)

            if os.path.exists(closed_path):
                self._sprite_closed = pygame.image.load(closed_path).convert_alpha()

                self._sprite_closed = pygame.transform.scale(self._sprite_closed, (self.width, self.height))
            else:
                print(f"Warning: Chest closed sprite not found at {closed_path}")

            if os.path.exists(open_path):
                self._sprite_open = pygame.image.load(open_path).convert_alpha()

                self._sprite_open = pygame.transform.scale(self._sprite_open, (self.width, self.height))
            else:
                print(f"Warning: Chest open sprite not found at {open_path}")

        except pygame.error as e:
            print(f"Error loading chest sprites: {e}. Using default rectangles.")
            self._sprite_closed = None
            self._sprite_open = None

    def get_current_sprite(self) -> Optional[pygame.Surface]:
        """Returns the appropriate sprite based on the chest's open state."""
        if self.is_open and self._sprite_open:
            return self._sprite_open
        elif self._sprite_closed:
            return self._sprite_closed
        return None

    def toggle_open(self):
        """Toggles the open state of the chest."""
        self.is_open = not self.is_open
        print(f"Chest {self.chest_id} is now {'open' if self.is_open else 'closed'}.")
        if not self.is_open:
            self.inventory.save_inventory()

    def is_interactable(self, player_x: float, player_y: float) -> bool:
        """
        Checks if the player is close enough to interact with the chest.
        A simple AABB distance check.
        """

        distance = ((player_x - self.world_x)**2 + (player_y - self.world_y)**2)**0.5

        INTERACT_RADIUS_PIXELS = Display.TILE_SIZE_PIXELS * 2
        chest_center_x = self.world_x + self.width / 2
        chest_center_y = self.world_y + self.height / 2
        
        distance_to_center = math.hypot(player_x - chest_center_x, player_y - chest_center_y)
        
        return distance_to_center < INTERACT_RADIUS_PIXELS

    def get_collision_rect(self) -> pygame.Rect: 
        """
        Returns the collision bounding box for the chest in world coordinates.
        """
        return pygame.Rect(self.world_x, self.world_y, self.width, self.height)


    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        """
        Draws the chest on the screen, applying camera offset.
        """
        screen_x = int(self.world_x - camera_offset_x)
        screen_y = int(self.world_y - camera_offset_y)

        draw_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        
        current_sprite = self.get_current_sprite()
        if current_sprite:
            screen.blit(current_sprite, draw_rect)
        else:

            pygame.draw.rect(screen, (139, 69, 19), draw_rect)
            if self.is_open:
                pygame.draw.rect(screen, (255, 255, 0), draw_rect, 2)

    def save_state(self):
        """Saves the chest's current state (open/closed, inventory)."""
        self.inventory.save_inventory()
        
    def load_state(self):
        """Loads the chest's state (inventory)."""
        self.inventory._load_inventory()
