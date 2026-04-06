# engine/world/objects/inventory/chest_inventory.py

import json
import os
from typing import List, Dict, Optional
from engine.items.base_item import BaseItem
from engine.items.item_registry import get_item_class
# Assuming IronSword is registered as 'iron_sword_id' when imported
from engine.items.weapons.swords.iron_sword import IronSword # Needed to ensure its registration

class ChestInventory:
    """
    Manages the inventory for a single chest, handling item instances and persistence.
    Each chest will have its own inventory file based on its unique ID.
    """
    MAX_CAPACITY = 15 # Chests might have a different capacity

    def __init__(self, chest_id: str):
        self.chest_id = chest_id
        self.items: List[BaseItem] = []
        # Path modified to ensure it's relative to the main game directory
        # user_data/chests/{chest_id}_inventory.json
        game_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        self._inventory_file_path = os.path.join(game_root_dir, "user_data", "chests", f"{self.chest_id}_inventory.json")
        self._load_inventory()

    def _load_inventory(self):
        """
        Loads the inventory from the chest's specific JSON file.
        If the file doesn't exist, initializes an empty inventory.
        """
        if not os.path.exists(self._inventory_file_path):
            print(f"Chest inventory file not found: {self._inventory_file_path}. Initializing empty inventory for chest {self.chest_id}.")
            self.items = []
            return

        try:
            with open(self._inventory_file_path, 'r') as f:
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
                    print(f"Warning: Could not find item class for ID '{item_id}' for chest {self.chest_id} during load.")
        except json.JSONDecodeError as e:
            print(f"Error decoding chest inventory JSON for {self.chest_id}: {e}. Starting with empty inventory.")
            self.items = []
        except Exception as e:
            print(f"An unexpected error occurred during chest inventory load for {self.chest_id}: {e}. Starting with empty inventory.")
            self.items = []

    def save_inventory(self):
        """
        Saves the current chest inventory to its specific JSON file.
        """
        os.makedirs(os.path.dirname(self._inventory_file_path), exist_ok=True)
        serialized_inventory = [item.to_dict() for item in self.items]
        try:
            with open(self._inventory_file_path, 'w') as f:
                json.dump(serialized_inventory, f, indent=4)
            print(f"Chest inventory for {self.chest_id} saved to {self._inventory_file_path}")
        except IOError as e:
            print(f"Error saving chest inventory for {self.chest_id}: {e}")

    def add_item(self, item: BaseItem, quantity: int = 1) -> bool:
        """
        Adds an item to the chest inventory. Handles stacking.
        Returns True if item was added, False otherwise.
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
                    print(f"Chest '{self.chest_id}' full, cannot add all {item.name}. Remaining: {quantity}")
                    return False
                
                item_class = get_item_class(item.item_id)
                if not item_class:
                    print(f"Error: Could not find item class for ID '{item.item_id}' when trying to add new stack to chest.")
                    return False
                new_stack_item = item_class() # Create a new instance for the new stack

                amount_to_add = min(quantity, new_stack_item.max_stack)
                new_stack_item.current_stack = amount_to_add
                self.items.append(new_stack_item)
                quantity -= amount_to_add
            return True
        else: # Non-stackable
            for _ in range(quantity):
                if len(self.items) >= self.MAX_CAPACITY:
                    print(f"Chest '{self.chest_id}' full, cannot add {item.name}.")
                    return False

                item_class = get_item_class(item.item_id)
                if not item_class:
                    print(f"Error: Could not find item class for ID '{item.item_id}' when trying to add non-stackable item to chest.")
                    return False
                new_instance = item_class() # Create a new instance for each quantity
                self.items.append(new_instance)
            return True

    def remove_item(self, item: BaseItem, quantity: int = 1) -> bool:
        """
        Removes an item from the chest inventory. Handles stacking.
        Returns True if item was removed, False otherwise.
        """
        if quantity <= 0:
            return False

        total_found_quantity = self.get_item_count(item.item_id)
        if total_found_quantity < quantity:
            print(f"Not enough {item.name} in chest '{self.chest_id}' to remove {quantity}. Found: {total_found_quantity}")
            return False

        remaining_to_remove = quantity
        
        # Iterate over a copy of the list to allow modification during iteration
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

    def get_item_count(self, item_id: str) -> int: # FIXED: Removed extra ')'
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
            return f"Chest ({self.chest_id}): Empty"
        items_str = ", ".join([f"{item.name} x{item.current_stack}" for item in self.items])
        return f"Chest ({self.chest_id}): [{items_str}]"
