import pygame
import sys
from engine.player.inventory.player_inventory import PlayerInventory
from engine.display import Display
from engine.player.player import Player
from utils.user_input import UserInputManager
from engine.world.world_logic.chunkloader import ChunkLoader
from engine.camera import Camera
from pygame import Surface
import math 
from engine.npc.npc_manager import NPCManager
from engine.world.objects.chest_manager import ChestManager
from ui.popup.inventory_view import InventoryView 
from ui.popup.chest_view import ChestView 

pygame.init()

game_display = Display() 

assert game_display.screen is not None, "game_display.screen somehow not initialized to a Surface"
screen: Surface = game_display.screen 

SPAWN_X_METERS = 3300
SPAWN_Y_METERS = 1300

player_initial_pixel_x = int(SPAWN_X_METERS * Display.PIXELS_PER_METER)
player_initial_pixel_y = int(SPAWN_Y_METERS * Display.PIXELS_PER_METER)

player = Player(
    x=player_initial_pixel_x, 
    y=player_initial_pixel_y
)

input_manager = UserInputManager()

chunk_loader = ChunkLoader()

camera = Camera(player)

npc_manager = NPCManager()
chest_manager = ChestManager()

inventory_view = InventoryView(screen, player.inventory, player)
chest_view = ChestView(screen, player.inventory, player)

FPS = 60
clock = pygame.time.Clock()

running = True
while running:

    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:

            if chest_view.is_open:
                chest_view.close()
            inventory_view.toggle_visibility()
            if inventory_view.is_open:
                input_manager.clear_movement_keys()
        
        if inventory_view.is_open:
            inventory_view.handle_event(event)
        elif chest_view.is_open:
            chest_view.handle_event(event)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_x, mouse_y = event.pos

                camera_offset_x, camera_offset_y = camera.get_offset()
                target_pixel_world_x = mouse_x + camera_offset_x
                target_pixel_world_y = mouse_y + camera_offset_y

                interacted_chest = chest_manager.interact_with_chests(target_pixel_world_x, target_pixel_world_y, player) 
                if interacted_chest:
                    chest_view.open(interacted_chest)
                    input_manager.clear_movement_keys()
                else:
                    target_tile_pixel_x = (target_pixel_world_x // Display.TILE_SIZE_PIXELS) * Display.TILE_SIZE_PIXELS
                    target_tile_pixel_y = (target_pixel_world_y // Display.TILE_SIZE_PIXELS) * Display.TILE_SIZE_PIXELS
                    
                    player.set_target(target_tile_pixel_x, target_tile_pixel_y) 
                    input_manager.clear_movement_keys()

            input_manager.handle_event(event)

    static_colliders_for_player = [
        chest.get_collision_rect() for chest in chest_manager.chests.values()
    ]

    dx, dy = 0, 0
    if not inventory_view.is_open and not chest_view.is_open: 
        dx, dy = input_manager.get_movement_vector()

    player.move(dx, dy, dt, static_colliders=static_colliders_for_player)
    player.update(dt)

    camera.update()
    
    camera_offset_x, camera_offset_y = camera.get_offset()

    chunk_loader.update(player.world_x, player.world_y)
    
    npc_manager.update(dt)
    chest_manager.update(dt) 

    screen.fill((0, 0, 0)) 

    for chunk in chunk_loader.get_chunks_to_draw():
        chunk.draw(screen, camera_offset_x, camera_offset_y)

    player.draw(screen, camera_offset_x, camera_offset_y) 
    
    npc_manager.draw(screen, camera_offset_x, camera_offset_y)
    chest_manager.draw(screen, camera_offset_x, camera_offset_y) 

    if player.target_x is not None and player.target_y is not None:
        target_screen_x = player.target_x - camera_offset_x
        target_screen_y = player.target_y - camera_offset_y
        
        game_display.draw_rect_outline(
            screen, 
            (255, 0, 0),
            target_screen_x, 
            target_screen_y, 
            Display.TILE_SIZE_PIXELS, 
            Display.TILE_SIZE_PIXELS, 
            outline_thickness=2 
        )

    world_x_m, world_y_m, pixel_x_on_map, pixel_y_on_map = \
        chunk_loader.get_player_coordinates_for_map_debug()

    debug_text_world = f"World (m): X={world_x_m:.2f}, Y={world_y_m:.2f}"
    debug_text_map = f"Map (px): X={pixel_x_on_map:.2f}, Y={pixel_y_on_map:.2f}"
    debug_chunk_coords = f"Chunk: ({chunk_loader.current_player_chunk_x}, {chunk_loader.current_player_chunk_y})"
    debug_player_pixel = f"Player (px): X={player.world_x:.0f}, Y={player.world_y:.0f}"
    debug_target_pixel = f"Target (px): {'N/A' if player.target_x is None else f'X={player.target_x:.0f}, Y={player.target_y:.0f}'}"
    
    game_display.draw_text(debug_text_world, 10, 10, (255, 255, 0))
    game_display.draw_text(debug_text_map, 10, 40, (255, 255, 0))
    game_display.draw_text(debug_chunk_coords, 10, 70, (255, 255, 0))
    game_display.draw_text(debug_player_pixel, 10, 100, (255, 255, 0))
    game_display.draw_text(debug_target_pixel, 10, 130, (255, 255, 0))

    inventory_view.draw()
    chest_view.draw() 

    pygame.display.flip()

player.inventory.save_inventory()
chest_manager.save_chests() 

pygame.quit()
sys.exit()
