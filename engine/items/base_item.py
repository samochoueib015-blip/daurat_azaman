import pygame
import os
from typing import Optional

class BaseItem:
    """
    Base class for all items in the game. Defines common properties and behaviors.
    """
    def __init__(self, item_id: str, name: str, description: str, value: int, 
                 sprite_path: Optional[str] = None,
                 stackable: bool = True, max_stack: int = 1):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.current_stack = 1
        self._sprite: Optional[pygame.Surface] = None
        self._sprite_path: Optional[str] = sprite_path

        if self._sprite_path:
            self._load_sprite()

    def _load_sprite(self):
        """Loads the item's sprite image."""
        try:
            game_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            if self._sprite_path is None:
                print(f"Error: _sprite_path is None for item {self.name} in _load_sprite().")
                self._sprite = None
                return

            full_sprite_path = os.path.join(game_root_dir, self._sprite_path)

            if not os.path.exists(full_sprite_path):
                print(f"Warning: Item sprite not found at {full_sprite_path} for item {self.name}. Using default placeholder.")
                self._sprite = None
                return

            self._sprite = pygame.image.load(full_sprite_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading sprite for {self.name}: {e}. Path: {self._sprite_path}. Using default placeholder.")
            self._sprite = None

    def get_sprite(self) -> pygame.Surface:
        """Returns the Pygame Surface for the item's sprite."""
        if self._sprite:
            return self._sprite

        placeholder_size = 32
        placeholder_surface = pygame.Surface((placeholder_size, placeholder_size), pygame.SRCALPHA)
        placeholder_surface.fill((255, 0, 255, 128))
        pygame.draw.rect(placeholder_surface, (0, 0, 0), (0, 0, placeholder_size, placeholder_size), 1)
        return placeholder_surface

    def to_dict(self) -> dict:
        """
        Converts the item's essential properties into a dictionary for serialization.
        This only includes what's needed to recreate the item later.
        """
        return {
            "item_id": self.item_id,
            "current_stack": self.current_stack
        }

    def use(self, player):
        """
        Default use method. Override in subclasses for specific item effects.
        """
        print(f"Using {self.name}...")
        
    def __repr__(self):
        return f"{self.name} (ID: {self.item_id}, x{self.current_stack})"
