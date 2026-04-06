import pygame
import os
from engine.display import Display
from game_config import PLAYER_SPRITE_SHEET_PATH, PLAYER_SPRITE_DIRECTIONS_ORDER, PLAYER_SWALK_SHEET_PATH 
from utils.direction import get_direction_from_vector
import math
from engine.player.inventory.player_inventory import PlayerInventory
from typing import Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.world.objects.chest import Chest

class Player:
    """
    Represents the player character in the game.
    """

    DEFAULT_WIDTH = int(1 * Display.PIXELS_PER_METER)
    DEFAULT_HEIGHT = int(2 * Display.PIXELS_PER_METER)

    DEFAULT_COLOR = (255, 0, 0)
    DEFAULT_SPEED = 150

    WALK_ANIMATION_FPS = 16
    
    TARGET_REACH_TOLERANCE = 10

    def __init__(self, x: float, y: float, width: Optional[int] = None, height: Optional[int] = None, 
                 color: Optional[tuple] = None, speed: Optional[int] = None):
        self.world_x: float = float(x)
        self.world_y: float = float(y)

        self.width: int = width if width is not None else self.DEFAULT_WIDTH
        self.height: int = height if height is not None else self.DEFAULT_HEIGHT
        self.color: tuple = color if color is not None else self.DEFAULT_COLOR

        self.speed: int = speed if speed is not None else self.DEFAULT_SPEED 

        self.rect: pygame.Rect = pygame.Rect(0, 0, self.width, self.height)

        self.idle_sprite_sheet: Optional[pygame.Surface] = None
        self.walk_sprite_sheet: Optional[pygame.Surface] = None
        self._idle_sprite_rects: Dict[str, pygame.Rect] = {}
        self._walk_frames_south_rects: List[pygame.Rect] = []

        self.current_direction_key: str = "S"

        self._is_moving: bool = False
        self._animation_frame_index: int = 0
        self._animation_timer: float = 0.0

        self.target_x: Optional[float] = None
        self.target_y: Optional[float] = None

        self._load_sprites()

        self.inventory: PlayerInventory = PlayerInventory()

    def _load_sprites(self):
        """
        Loads the player sprite sheets and calculates sub-rectangles for each.
        """
        try:

            game_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            idle_full_path = os.path.join(game_root_dir, PLAYER_SPRITE_SHEET_PATH)
            self.idle_sprite_sheet = pygame.image.load(idle_full_path).convert_alpha()

            walk_full_path = os.path.join(game_root_dir, PLAYER_SWALK_SHEET_PATH)
            self.walk_sprite_sheet = pygame.image.load(walk_full_path).convert_alpha()

            IDLE_SPRITE_SHEET_COLS = 4 
            IDLE_SPRITE_SHEET_ROWS = 2 

            expected_idle_sheet_width = IDLE_SPRITE_SHEET_COLS * self.width
            expected_idle_sheet_height = IDLE_SPRITE_SHEET_ROWS * self.height


            if self.idle_sprite_sheet and (self.idle_sprite_sheet.get_width() != expected_idle_sheet_width or \
               self.idle_sprite_sheet.get_height() != expected_idle_sheet_height):
                print(f"Warning: Idle sheet ({self.idle_sprite_sheet.get_width()}x{self.idle_sprite_sheet.get_height()}) "
                      f"expected ({expected_idle_sheet_width}x{expected_idle_sheet_height}). Check {PLAYER_SPRITE_SHEET_PATH}")
            
            for i, direction_key in enumerate(PLAYER_SPRITE_DIRECTIONS_ORDER):
                col = i % IDLE_SPRITE_SHEET_COLS 
                row = i // IDLE_SPRITE_SHEET_COLS 

                x_offset = col * self.width
                y_offset = row * self.height
                
                self._idle_sprite_rects[direction_key] = pygame.Rect(x_offset, y_offset, self.width, self.height)

            if self.walk_sprite_sheet:

                for i in range(IDLE_SPRITE_SHEET_COLS * IDLE_SPRITE_SHEET_ROWS): 
                    col = i % IDLE_SPRITE_SHEET_COLS
                    row = i // IDLE_SPRITE_SHEET_COLS

                    x_offset = col * self.width
                    y_offset = row * self.height

                    self._walk_frames_south_rects.append(pygame.Rect(x_offset, y_offset, self.width, self.height))
            else:
                 self._walk_frames_south_rects = []

        except pygame.error as e:
            print(f"Error loading player sprite sheet: {e}")
            print(f"Attempted to load from: {idle_full_path} or {walk_full_path}")
            self.idle_sprite_sheet = None
            self.walk_sprite_sheet = None
            self._idle_sprite_rects = {}
            self._walk_frames_south_rects = []
            return

    def get_current_sprite(self) -> Optional[pygame.Surface]:
        """
        Returns the current Pygame Surface of the player's sprite or animation frame.
        Useful for displaying in UI.
        """
        if self._is_moving and self.current_direction_key == "S" and self.walk_sprite_sheet and self._walk_frames_south_rects:
            frame_rect = self._walk_frames_south_rects[self._animation_frame_index]
            return self.walk_sprite_sheet.subsurface(frame_rect)
        elif self.idle_sprite_sheet and self.current_direction_key in self._idle_sprite_rects:
            sprite_rect = self._idle_sprite_rects[self.current_direction_key]
            return self.idle_sprite_sheet.subsurface(sprite_rect)
        return None

    def set_target(self, x: float, y: float):
        self.target_x = float(x)
        self.target_y = float(y)

    def move(self, keyboard_dx: float, keyboard_dy: float, dt: float, static_colliders: Optional[List[pygame.Rect]] = None):
        """
        Updates the player's world position based on keyboard input or auto-movement target.
        Keyboard input takes precedence.
        :param static_colliders: A list of pygame.Rect objects representing impassable static objects.
        """

        effective_dx, effective_dy = keyboard_dx, keyboard_dy
        
        distance_to_target: Optional[float] = None 

        if effective_dx == 0 and effective_dy == 0 and self.target_x is not None and self.target_y is not None:

            vec_x = self.target_x - self.world_x
            vec_y = self.target_y - self.world_y

            distance_to_target = math.hypot(vec_x, vec_y)

            if distance_to_target < self.TARGET_REACH_TOLERANCE:

                self.world_x = self.target_x
                self.world_y = self.target_y
                self.target_x = None
                self.target_y = None
                self._is_moving = False
                return

            if distance_to_target > 0:
                effective_dx = vec_x / distance_to_target
                effective_dy = vec_y / distance_to_target
            else:
                effective_dx, effective_dy = 0, 0
                
        else:
            self.target_x = None
            self.target_y = None

        if effective_dx != 0 or effective_dy != 0:
            self._is_moving = True
            
            magnitude = math.hypot(effective_dx, effective_dy)
            if magnitude > 0:
                normalized_dx = effective_dx / magnitude
                normalized_dy = effective_dy / magnitude
            else:
                normalized_dx = 0
                normalized_dy = 0

            if keyboard_dx != 0 or keyboard_dy != 0:
                self.current_direction_key = get_direction_from_vector(keyboard_dx, keyboard_dy, self.current_direction_key)
            elif self.target_x is not None:
                dir_x = 0
                if normalized_dx > 0.5: dir_x = 1
                elif normalized_dx < -0.5: dir_x = -1

                dir_y = 0
                if normalized_dy > 0.5: dir_y = 1
                elif normalized_dy < -0.5: dir_y = -1
                
                if dir_x != 0 or dir_y != 0:
                    self.current_direction_key = get_direction_from_vector(dir_x, dir_y, self.current_direction_key)

            potential_new_world_x = self.world_x + normalized_dx * self.speed * dt
            potential_new_world_y = self.world_y + normalized_dy * self.speed * dt

            player_future_rect_x = pygame.Rect(potential_new_world_x, self.world_y, self.width, self.height)
            player_future_rect_y = pygame.Rect(self.world_x, potential_new_world_y, self.width, self.height)
            
            if static_colliders:

                for collider_rect in static_colliders:
                    if player_future_rect_x.colliderect(collider_rect):
                        if normalized_dx > 0:
                            potential_new_world_x = collider_rect.left - self.width
                        elif normalized_dx < 0:
                            potential_new_world_x = collider_rect.right

                        player_future_rect_y = pygame.Rect(potential_new_world_x, potential_new_world_y, self.width, self.height)
                        break 
                
                for collider_rect in static_colliders:
                    if player_future_rect_y.colliderect(collider_rect):
                        if normalized_dy > 0:
                            potential_new_world_y = collider_rect.top - self.height
                        elif normalized_dy < 0:
                            potential_new_world_y = collider_rect.bottom
                        break

            if self.target_x is not None and self.target_y is not None and distance_to_target is not None:
                current_vec_x = self.target_x - self.world_x
                current_vec_y = self.target_y - self.world_y
                
                if (current_vec_x * (self.target_x - potential_new_world_x)) < 0:
                    potential_new_world_x = self.target_x
                if (current_vec_y * (self.target_y - potential_new_world_y)) < 0:
                    potential_new_world_y = self.target_y
                
                new_distance_to_target = math.hypot(self.target_x - potential_new_world_x, self.target_y - potential_new_world_y)
                if new_distance_to_target < self.TARGET_REACH_TOLERANCE:
                    self.world_x = self.target_x
                    self.world_y = self.target_y
                    self.target_x = None
                    self.target_y = None
                    self._is_moving = False
                    return

            self.world_x = potential_new_world_x
            self.world_y = potential_new_world_y
            
        else:
            self._is_moving = False
            self.target_x = None

    def update(self, dt: float):
        """
        Updates the player's animation state based on delta time.
        """
        if self._is_moving:

            if self.current_direction_key == "S" and self.walk_sprite_sheet and self._walk_frames_south_rects:
                self._animation_timer += dt
                if self._animation_timer >= 1.0 / self.WALK_ANIMATION_FPS:
                    self._animation_frame_index = (self._animation_frame_index + 1) % len(self._walk_frames_south_rects)
                    self._animation_timer = 0.0
            else:
                self._animation_frame_index = 0
                self._animation_timer = 0.0
        else:
            self._animation_frame_index = 0
            self._animation_timer = 0.0

    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        """
        Draws the player on the given screen surface, using the appropriate sprite or animation frame.
        Applies camera offset to draw player at correct screen position.
        """
        screen_x = self.world_x - camera_offset_x
        screen_y = self.world_y - camera_offset_y

        self.rect.topleft = (int(screen_x), int(screen_y))

        current_sprite_surface = self.get_current_sprite()
        
        if current_sprite_surface:
            screen.blit(current_sprite_surface, self.rect)
        else:

            pygame.draw.rect(screen, self.color, self.rect)
