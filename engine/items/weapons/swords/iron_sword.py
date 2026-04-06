from engine.items.base_item import BaseItem
from engine.items.item_registry import register_item
import os
from typing import Optional

@register_item
class IronSword(BaseItem):
    ITEM_ID = "iron_sword"

    def __init__(self, 
                 name: str = "Iron Sword", 
                 description: str = "A robust sword crafted from iron. Suitable for basic combat.",
                 value: int = 50,
                 damage: int = 10,

                 sprite_path: Optional[str] = None
                ):
        
        default_sprite_path = os.path.join("av", "sprites", "items", "weapons", "iron_sword.png")
        final_sprite_path = sprite_path if sprite_path is not None else default_sprite_path

        super().__init__(
            item_id=IronSword.ITEM_ID,
            name=name,
            description=description,
            value=value,
            sprite_path=final_sprite_path,
            stackable=False,
            max_stack=1
        )
        
        self.damage = damage

    def inspect(self):
        """
        Custom method to display sword-specific details.
        """
        print(f"--- {self.name} ---")
        print(f"Description: {self.description}")
        print(f"Value: {self.value} gold")
        print(f"Damage: {self.damage}")
