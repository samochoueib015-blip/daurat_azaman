import pygame
from engine.npc.npc import NPC
import random
from engine.display import Display

class NPCManager:
    """
    Manages all NPCs in the game world.
    """
    def __init__(self):
        self.active_npcs = pygame.sprite.Group()

        SPAWN_X_METERS = 1300
        SPAWN_Y_METERS = 3300

        if Display.PIXELS_PER_METER == 0:
            print("WARNING: Display.PIXELS_PER_METER is 0 in NPCManager. This indicates an initialization order issue.")
            player_spawn_pixel_x = int(SPAWN_X_METERS * 32)
            player_spawn_pixel_y = int(SPAWN_Y_METERS * 32)
        else:
            player_spawn_pixel_x = int(SPAWN_X_METERS * Display.PIXELS_PER_METER)
            player_spawn_pixel_y = int(SPAWN_Y_METERS * Display.PIXELS_PER_METER)

        print(f"DEBUG NPCManager: Player reference spawn (pixel): X={player_spawn_pixel_x}, Y={player_spawn_pixel_y}")

        human_spawn_x = float(player_spawn_pixel_x - (2 * Display.PIXELS_PER_METER))
        human_spawn_y = float(player_spawn_pixel_y - (1 * Display.PIXELS_PER_METER))
        human_npc = NPC(x_world=human_spawn_x, y_world=human_spawn_y, race_key="human", name="Villager Alex")

        human_npc.set_target(human_spawn_x + 50.0, human_spawn_y + 50.0) 
        self.active_npcs.add(human_npc)
        print(f"DEBUG NPCManager: Added Human NPC '{human_npc.name}' at world ({human_npc.world_x}, {human_npc.world_y})")

        elf_spawn_x = float(player_spawn_pixel_x + (2 * Display.PIXELS_PER_METER))
        elf_spawn_y = float(player_spawn_pixel_y + (1 * Display.PIXELS_PER_METER))
        elf_npc = NPC(x_world=elf_spawn_x, y_world=elf_spawn_y, race_key="elf", name="Elara Whisperwind")

        elf_npc.set_target(elf_spawn_x - 50.0, elf_spawn_y - 50.0)
        self.active_npcs.add(elf_npc)
        print(f"DEBUG NPCManager: Added Elf NPC '{elf_npc.name}' at world ({elf_npc.world_x}, {elf_npc.world_y})")

    def update(self, dt):
        """
        Updates all active NPCs.
        """
        for npc in self.active_npcs:
            if npc.target_x is None:
                new_target_x = float(npc.world_x + random.randint(-150, 150))
                new_target_y = float(npc.world_y + random.randint(-150, 150))
                npc.set_target(new_target_x, new_target_y)
        
        self.active_npcs.update(dt) 

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """
        Draws all active NPCs on the screen.
        """

        for npc in self.active_npcs:
            npc.draw(screen, camera_offset_x, camera_offset_y)
