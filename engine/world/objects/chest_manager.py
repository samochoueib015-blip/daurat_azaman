import json
import os
import pygame
from typing import Dict, List, Optional
from engine.world.objects.chest import Chest
from engine.display import Display
from engine.items.base_item import BaseItem
from engine.items.weapons.swords.iron_sword import IronSword

class ChestManager:
    """
    Manages loading, saving, and interaction with all chests in the game world.
    """
    CHEST_DATA_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "user_data", "chests", "chests_metadata.json"
    )

    def __init__(self):
        self.chests: Dict[str, Chest] = {}
        self._load_chests_metadata()

        if not self.chests:
            self._create_initial_chests()

    def _load_chests_metadata(self):
        """
        Loads metadata for all chests (their IDs, positions) from a central file.
        Each chest's inventory is loaded by ChestInventory class itself.
        """
        if not os.path.exists(self.CHEST_DATA_FILE):
            print(f"Chest metadata file not found: {self.CHEST_DATA_FILE}. Will create default chests.")
            return

        try:
            with open(self.CHEST_DATA_FILE, 'r') as f:
                chests_metadata = json.load(f)

            for chest_data in chests_metadata:
                chest_id = chest_data["chest_id"]
                x = chest_data["x"]
                y = chest_data["y"]
                chest = Chest(chest_id, x, y)
                self.chests[chest_id] = chest
                print(f"Loaded chest: {chest_id} at ({x}, {y})")
        except json.JSONDecodeError as e:
            print(f"Error decoding chest metadata JSON: {e}. Starting with empty chests.")
            self.chests = {}
        except Exception as e:
            print(f"An unexpected error occurred during chest metadata load: {e}. Starting with empty chests.")
            self.chests = {}

    def save_chests(self):
        """
        Saves metadata for all chests and triggers each chest to save its inventory.
        """
        os.makedirs(os.path.dirname(self.CHEST_DATA_FILE), exist_ok=True)
        
        chests_metadata = []
        for chest_id, chest in self.chests.items():
            chests_metadata.append({
                "chest_id": chest.chest_id,
                "x": chest.world_x,
                "y": chest.world_y
            })
            chest.save_state()
        
        try:
            with open(self.CHEST_DATA_FILE, 'w') as f:
                json.dump(chests_metadata, f, indent=4)
            print(f"Chest metadata saved to {self.CHEST_DATA_FILE}")
        except IOError as e:
            print(f"Error saving chest metadata: {e}")

    def _create_initial_chests(self):
        """
        Creates some default chests if no chest data is found.
        Populates them with some items for testing.
        """
        print("Creating initial default chests...")

        SPAWN_X_METERS = 1300
        SPAWN_Y_METERS = 3300
        player_spawn_pixel_x = int(SPAWN_X_METERS * Display.PIXELS_PER_METER)
        player_spawn_pixel_y = int(SPAWN_Y_METERS * Display.PIXELS_PER_METER)


        chest1_id = "wooden_chest_001"
        chest1_x = player_spawn_pixel_x + (2 * Display.TILE_SIZE_PIXELS)
        chest1_y = player_spawn_pixel_y + (1 * Display.TILE_SIZE_PIXELS)
        chest1 = Chest(chest1_id, chest1_x, chest1_y)
        chest1.inventory.add_item(IronSword(), quantity=3)
        chest1.inventory.add_item(IronSword(name="Polished Iron Sword", value=100, damage=22), quantity=1)
        self.chests[chest1_id] = chest1
        
        chest2_id = "wooden_chest_002"
        chest2_x = player_spawn_pixel_x - (3 * Display.TILE_SIZE_PIXELS)
        chest2_y = player_spawn_pixel_y + (2 * Display.TILE_SIZE_PIXELS)
        chest2 = Chest(chest2_id, chest2_x, chest2_y)
        self.chests[chest2_id] = chest2

        self.save_chests()
        print(f"Created {len(self.chests)} initial chests.")

    def update(self, dt: float):
        """
        Updates internal state of chests if necessary (e.g., animation).
        For now, chests are static, so this is a placeholder.
        """
        pass

    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        """
        Draws all active chests on the screen.
        """
        for chest in self.chests.values():
            chest.draw(screen, camera_offset_x, camera_offset_y)

    def interact_with_chests(self, mouse_world_x: int, mouse_world_y: int, player) -> Optional[Chest]:
        """
        Checks if the mouse click interacted with any chest and if the player is close enough.
        Returns the interacted chest if successful, otherwise None.
        """
        for chest in self.chests.values():
            chest_rect_world = pygame.Rect(chest.world_x, chest.world_y, chest.width, chest.height)
            
            if chest_rect_world.collidepoint(mouse_world_x, mouse_world_y):
                if chest.is_interactable(player.world_x, player.world_y):
                    chest.toggle_open()
                    return chest
        return None
