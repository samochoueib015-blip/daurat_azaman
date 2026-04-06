from typing import Type, Dict, Any

ITEM_REGISTRY: Dict[str, Type[Any]] = {}

def register_item(item_class: Type[Any]):
    """
    Decorator to register an item class with the global ITEM_REGISTRY.
    The item's unique identifier (ITEM_ID) must be defined as a class attribute
    within the item class itself.
    """

    item_id = getattr(item_class, 'ITEM_ID', None) 

    if item_id and isinstance(item_id, str):
        if item_id in ITEM_REGISTRY:
            print(f"Warning: Duplicate item_id '{item_id}' registered. Overwriting with {item_class.__name__}")
        ITEM_REGISTRY[item_id] = item_class

    else:
        print(f"Warning: Item class {item_class.__name__} has no valid 'ITEM_ID' (must be a non-empty string) class attribute. Not registered.")
    return item_class

def get_item_class(item_id: str) -> Type[Any] | None:
    """
    Retrieves an item class from the registry by its item_id.
    Returns the class object if found, otherwise None.
    """
    return ITEM_REGISTRY.get(item_id)
