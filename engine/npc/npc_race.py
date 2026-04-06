from engine.display import Display
from game_config import NPC_HUMAN_IDLE_SHEET_PATH, NPC_ELF_IDLE_SHEET_PATH

class BaseRace:
    """Base class for all NPC races."""
    def __init__(self, name, description, default_width_pixels, default_height_pixels, default_speed_pixels_per_sec, default_color, idle_sprite_sheet_path):
        self.name = name
        self.description = description
        self.default_width_pixels = default_width_pixels
        self.default_height_pixels = default_height_pixels
        self.default_speed_pixels_per_sec = default_speed_pixels_per_sec
        self.default_color = default_color
        self.idle_sprite_sheet_path = idle_sprite_sheet_path

class HumanRace(BaseRace):
    """Defines characteristics for the Human race."""
    def __init__(self):
        width_in_meters = 1.0
        height_in_meters = 2.0
        
        speed_in_meters_per_sec = 1.5
        
        pixels_per_meter = Display.PIXELS_PER_METER if hasattr(Display, 'PIXELS_PER_METER') and Display.PIXELS_PER_METER != 0 else 32 

        calculated_width_pixels = int(width_in_meters * pixels_per_meter)
        calculated_height_pixels = int(height_in_meters * pixels_per_meter)
        calculated_speed_pixels = int(speed_in_meters_per_sec * pixels_per_meter) 

        super().__init__(
            name="Human",
            description="A common human.",
            default_width_pixels=calculated_width_pixels,
            default_height_pixels=calculated_height_pixels,
            default_speed_pixels_per_sec=calculated_speed_pixels, 
            default_color=(0, 200, 0),
            idle_sprite_sheet_path=NPC_HUMAN_IDLE_SHEET_PATH
        )

class ElfRace(BaseRace):
    """Defines characteristics for the Elf race."""
    def __init__(self):
        width_in_meters = 1.0
        height_in_meters = 2.0
        
        speed_in_meters_per_sec = 1.8

        pixels_per_meter = Display.PIXELS_PER_METER if hasattr(Display, 'PIXELS_PER_METER') and Display.PIXELS_PER_METER != 0 else 32

        calculated_width_pixels = int(width_in_meters * pixels_per_meter)
        calculated_height_pixels = int(height_in_meters * pixels_per_meter)
        calculated_speed_pixels = int(speed_in_meters_per_sec * pixels_per_meter)

        super().__init__(
            name="Elf",
            description="A graceful elf, identical to humans for now.",
            default_width_pixels=calculated_width_pixels,
            default_height_pixels=calculated_height_pixels,
            default_speed_pixels_per_sec=calculated_speed_pixels,
            default_color=(0, 0, 200),
            idle_sprite_sheet_path=NPC_ELF_IDLE_SHEET_PATH
        )

RACE_REGISTRY = {
    "human": HumanRace(),
    "elf": ElfRace()
}
