import json
import os
from typing import List, Dict, Optional
from engine.items.base_item import BaseItem
from engine.items.item_registry import get_item_class
from engine.items.weapons.swords.iron_sword import IronSword 

class PlayerInventory:
    """
    Manages the player's inventory, holding item instances in memory
    and handling persistence to/from a JSON file.
    """
    GAME_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    SAVE_DIR = os.path.join(GAME_ROOT_DIR, "user_data", "player")
    INVENTORY_FILE = os.path.join(SAVE_DIR, "inventory_content.json")

    MAX_CAPACITY = 20

    def __init__(self):
        self.items: List[BaseItem] = []
        self._load_inventory()

    def _load_inventory(self):
        """
        Loads the inventory from the JSON file.
        If the file doesn't exist, initializes an empty inventory.
        """
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        
        if not os.path.exists(self.INVENTORY_FILE):
            print(f"Inventory file not found: {self.INVENTORY_FILE}. Initializing empty inventory.")
            self.items = []
            return

        try:
            with open(self.INVENTORY_FILE, 'r') as f:
                serialized_inventory = json.load(f)

            self.items = []
            for item_data in serialized_inventory:
                item_id = item_data.get("item_id")
                current_stack = item_data.get("current_stack", 1)

                item_class = get_item_class(item_id)
                if item_class:
                    item_instance = item_class()
                    item_instance.current_stack = current_stack
                    self.items.append(item_instance)
                else:
                    print(f"Warning: Could not find item class for ID '{item_id}' during load. Item skipped.")
        except json.JSONDecodeError as e:
            print(f"Error decoding inventory JSON: {e}. Starting with empty inventory.")
            self.items = []
        except Exception as e:
            print(f"An unexpected error occurred during inventory load: {e}. Starting with empty inventory.")
            self.items = []

    def save_inventory(self):
        """
        Saves the current inventory to the JSON file.
        """
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        serialized_inventory = [item.to_dict() for item in self.items]
        try:
            with open(self.INVENTORY_FILE, 'w') as f:
                json.dump(serialized_inventory, f, indent=4)
            print(f"Inventory saved to {self.INVENTORY_FILE}")
        except IOError as e:
            print(f"Error saving inventory: {e}")

    def add_item(self, item: BaseItem, quantity: int = 1) -> bool:
        """
        Adds an item to the inventory. Handles stacking if the item is stackable.
        Returns True if item was added, False otherwise (e.g., inventory full).
        """
        if quantity <= 0:
            return False

        if item.stackable:
            for existing_item in self.items:
                if existing_item.item_id == item.item_id and existing_item.current_stack < existing_item.max_stack:
                    space_available = existing_item.max_stack - existing_item.current_stack
                    amount_to_add = min(quantity, space_available)
                    existing_item.current_stack += amount_to_add
                    quantity -= amount_to_add
                    if quantity == 0:
                        return True

            while quantity > 0:
                if len(self.items) >= self.MAX_CAPACITY:
                    print(f"Inventory full, cannot add all {item.name}. Remaining: {quantity}")
                    return False
                
                item_class = get_item_class(item.item_id)
                if not item_class:
                    print(f"Error: Could not find item class for ID '{item.item_id}' when trying to add new stack. Item not added.")
                    return False
                new_stack_item = item_class()

                amount_to_add = min(quantity, new_stack_item.max_stack)
                new_stack_item.current_stack = amount_to_add
                self.items.append(new_stack_item)
                quantity -= amount_to_add
            return True
        else:
            for _ in range(quantity):
                if len(self.items) >= self.MAX_CAPACITY:
                    print(f"Inventory full, cannot add {item.name}.")
                    return False

                item_class = get_item_class(item.item_id)
                if not item_class:
                    print(f"Error: Could not find item class for ID '{item.item_id}' when trying to add non-stackable item. Item not added.")
                    return False
                new_instance = item_class()

                self.items.append(new_instance)
            return True

    def remove_item(self, item: BaseItem, quantity: int = 1) -> bool:
        """
        Removes an item from the inventory. Handles stacking.
        Returns True if item was removed, False otherwise (e.g., not enough quantity).
        """
        if quantity <= 0:
            return False

        total_found_quantity = self.get_item_count(item.item_id)
        if total_found_quantity < quantity:
            print(f"Not enough {item.name} in inventory to remove {quantity}. Found: {total_found_quantity}")
            return False

        remaining_to_remove = quantity
        
        for existing_item in self.items[:]:
            if remaining_to_remove <= 0:
                break

            if existing_item.item_id == item.item_id:
                if existing_item.current_stack >= remaining_to_remove:
                    existing_item.current_stack -= remaining_to_remove
                    remaining_to_remove = 0
                    if existing_item.current_stack == 0:
                        self.items.remove(existing_item)
                else:
                    remaining_to_remove -= existing_item.current_stack
                    self.items.remove(existing_item)

        return remaining_to_remove == 0

    def get_items(self) -> List[BaseItem]:
        """Returns the list of item instances currently in the inventory."""
        return self.items

    def get_item_count(self, item_id: str) -> int:
        """Returns the total quantity of a specific item_id in the inventory."""
        count = 0
        for item in self.items:
            if item.item_id == item_id:
                count += item.current_stack
        return count

    def __len__(self):
        return len(self.items)

    def __str__(self):
        if not self.items:
            return "Inventory: Empty"
        items_str = ", ".join([f"{item.name} x{item.current_stack}" for item in self.items])
        return f"Inventory: [{items_str}]"
