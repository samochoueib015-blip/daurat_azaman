import pygame
import os
import math
from engine.display import Display
from game_config import PLAYER_SPRITE_DIRECTIONS_ORDER
from utils.direction import get_direction_from_vector
from engine.npc.npc_race import RACE_REGISTRY

class NPC(pygame.sprite.Sprite):
    """
    Base class for all Non-Player Characters (NPCs).
    """

    IDLE_SPRITE_SHEET_COLS = 4
    IDLE_SPRITE_SHEET_ROWS = 2

    def __init__(self, x_world, y_world, race_key, name="Unnamed NPC"):
        super().__init__()

        self.world_x = float(x_world)
        self.world_y = float(y_world)

        self.name = name

        self.race = RACE_REGISTRY.get(race_key.lower())
        if not self.race:
            raise ValueError(f"Unknown race_key: {race_key}. Must be in {list(RACE_REGISTRY.keys())}")

        self.width = self.race.default_width_pixels
        self.height = self.race.default_height_pixels
        self.speed = self.race.default_speed_pixels_per_sec
        self.color = self.race.default_color

        print(f"DEBUG NPC Init: '{self.name}' (Race: {self.race.name}) initialized with:")
        print(f"  - Speed: {self.speed} px/s")
        print(f"  - Dimensions: {self.width}x{self.height} px")

        self.idle_sprite_sheet = None
        self._idle_sprite_rects = {}
        self.current_direction_key = "S"

        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(int(self.world_x), int(self.world_y)))

        self._is_moving = False
        self._animation_frame_index = 0
        self._animation_timer = 0.0

        self.target_x = None
        self.target_y = None
        self.TARGET_REACH_TOLERANCE = 10

        self._load_sprites()

    def _load_sprites(self):
        """
        Loads the NPC idle sprite sheet and calculates sub-rectangles for each direction.
        If loading fails, self.image remains the colored rectangle.
        """
        game_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if not self.race or not self.race.idle_sprite_sheet_path:
            print(f"Warning: No idle sprite sheet path defined for race {self.race.name if self.race else 'UNKNOWN'}.")
            self.image.fill(self.color)
            self.idle_sprite_sheet = None
            return

        sprite_full_path = os.path.join(game_root_dir, self.race.idle_sprite_sheet_path)

        if not os.path.exists(sprite_full_path):
            print(f"Error: NPC sprite sheet not found at {sprite_full_path} for {self.name} ({self.race.name}). Falling back to colored rect.")
            self.image.fill(self.color)
            self.idle_sprite_sheet = None
            return

        try:
            self.idle_sprite_sheet = pygame.image.load(sprite_full_path).convert_alpha()

            expected_sheet_width = self.IDLE_SPRITE_SHEET_COLS * self.width
            expected_sheet_height = self.IDLE_SPRITE_SHEET_ROWS * self.height

            if self.idle_sprite_sheet.get_width() != expected_sheet_width or \
               self.idle_sprite_sheet.get_height() != expected_sheet_height:
                print(f"Warning: {self.race.name} idle sheet ({self.idle_sprite_sheet.get_width()}x{self.idle_sprite_sheet.get_height()}) "
                      f"expected ({expected_sheet_width}x{expected_sheet_height}). Check {self.race.idle_sprite_sheet_path}. Falling back to colored rect.")
                self.image.fill(self.color)
                self.idle_sprite_sheet = None
                return

            if self.IDLE_SPRITE_SHEET_COLS * self.IDLE_SPRITE_SHEET_ROWS < len(PLAYER_SPRITE_DIRECTIONS_ORDER):
                print(f"Warning: NPC idle sheet frames ({self.IDLE_SPRITE_SHEET_COLS*self.IDLE_SPRITE_SHEET_ROWS}) "
                      f"are fewer than primary directions ({len(PLAYER_SPRITE_DIRECTIONS_ORDER)}). Some directions may not have a distinct frame. Check sheet or config.")
            elif self.IDLE_SPRITE_SHEET_COLS * self.IDLE_SPRITE_SHEET_ROWS > len(PLAYER_SPRITE_DIRECTIONS_ORDER):
                print(f"Warning: NPC idle sheet frames ({self.IDLE_SPRITE_SHEET_COLS*self.IDLE_SPRITE_SHEET_ROWS}) "
                      f"are more than primary directions ({len(PLAYER_SPRITE_DIRECTIONS_ORDER)}). Redundant frames may exist. Check sheet or config.")

            for i, direction_key in enumerate(PLAYER_SPRITE_DIRECTIONS_ORDER):
                if i < self.IDLE_SPRITE_SHEET_COLS * self.IDLE_SPRITE_SHEET_ROWS:
                    col = i % self.IDLE_SPRITE_SHEET_COLS
                    row = i // self.IDLE_SPRITE_SHEET_COLS
                    x_offset = col * self.width
                    y_offset = row * self.height
                    self._idle_sprite_rects[direction_key] = pygame.Rect(x_offset, y_offset, self.width, self.height)
                else:
                    self._idle_sprite_rects[direction_key] = self._idle_sprite_rects.get("S")

            if "S" in self._idle_sprite_rects:
                self.image = self.idle_sprite_sheet.subsurface(self._idle_sprite_rects["S"])
            elif self._idle_sprite_rects:
                self.image = self.idle_sprite_sheet.subsurface(list(self._idle_sprite_rects.values())[0])
            else:
                print(f"Warning: No valid sprite rects generated for {self.name}. Falling back to colored rect.")
                self.image.fill(self.color)


        except pygame.error as e:
            print(f"Error loading NPC sprite sheet for {self.name} ({self.race.name}): {e}")
            print(f"Attempted to load from: {sprite_full_path}. Falling back to colored rect.")
            self.idle_sprite_sheet = None
            self.image.fill(self.color)
    def set_target(self, x, y):
        """Sets a target for the NPC to move towards."""
        self.target_x = float(x)
        self.target_y = float(y)

    def move(self, dt):
        """
        Updates the NPC's world position based on its target.
        This provides basic auto-movement behavior.
        """
        if self.target_x is None or self.target_y is None:
            self._is_moving = False
            if self.idle_sprite_sheet and self.current_direction_key in self._idle_sprite_rects:
                self.image = self.idle_sprite_sheet.subsurface(self._idle_sprite_rects[self.current_direction_key])
            return

        vec_x = self.target_x - self.world_x
        vec_y = self.target_y - self.world_y

        distance_to_target = math.hypot(vec_x, vec_y)

        if distance_to_target < self.TARGET_REACH_TOLERANCE:
            self.world_x = self.target_x
            self.world_y = self.target_y
            self.target_x = None
            self.target_y = None
            self._is_moving = False
            if self.idle_sprite_sheet and self.current_direction_key in self._idle_sprite_rects:
                self.image = self.idle_sprite_sheet.subsurface(self._idle_sprite_rects[self.current_direction_key])
            return

        self._is_moving = True

        if distance_to_target > 0:
            normalized_dx = vec_x / distance_to_target
            normalized_dy = vec_y / distance_to_target
        else:
            normalized_dx = 0
            normalized_dy = 0
            self._is_moving = False
            return

        dir_x_int = 0
        if normalized_dx > 0.5: dir_x_int = 1
        elif normalized_dx < -0.5: dir_x_int = -1

        dir_y_int = 0
        if normalized_dy > 0.5: dir_y_int = 1
        elif normalized_dy < -0.5: dir_y_int = -1
        
        if dir_x_int != 0 or dir_y_int != 0:
            self.current_direction_key = get_direction_from_vector(dir_x_int, dir_y_int, self.current_direction_key)
        
        if self.idle_sprite_sheet and self.current_direction_key in self._idle_sprite_rects:
            self.image = self.idle_sprite_sheet.subsurface(self._idle_sprite_rects[self.current_direction_key])

        delta_x = normalized_dx * self.speed * dt
        delta_y = normalized_dy * self.speed * dt

        if (delta_x > 0 and self.world_x + delta_x > self.target_x) or \
           (delta_x < 0 and self.world_x + delta_x < self.target_x):
            self.world_x = self.target_x
            delta_x = 0

        if (delta_y > 0 and self.world_y + delta_y > self.target_y) or \
           (delta_y < 0 and self.world_y + delta_y < self.target_y):
            self.world_y = self.target_y
            delta_y = 0

        self.world_x += delta_x
        self.world_y += delta_y

        if abs(self.world_x - self.target_x) < self.TARGET_REACH_TOLERANCE and \
           abs(self.world_y - self.target_y) < self.TARGET_REACH_TOLERANCE:
            self.world_x = self.target_x
            self.world_y = self.target_y
            self.target_x = None
            self.target_y = None
            self._is_moving = False
            if self.idle_sprite_sheet and self.current_direction_key in self._idle_sprite_rects:
                self.image = self.idle_sprite_sheet.subsurface(self._idle_sprite_rects[self.current_direction_key])


    def update(self, dt):
        """
        Updates the NPC's state, including movement.
        """
        self.move(dt)
    def draw(self, screen, camera_offset_x, camera_offset_y):
        """
        Draws the NPC on the screen, applying camera offset.
        NOTE: Pygame sprite groups handle blitting self.image at self.rect.
        """
        screen_x = int(self.world_x - camera_offset_x)
        screen_y = int(self.world_y - camera_offset_y)

        self.rect.topleft = (screen_x, screen_y)
        
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            print(f"DEBUG NPC.draw: Warning, self.image is None for {self.name}. Drawing fallback rectangle.")
            fallback_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, (255, 0, 255), fallback_rect, 1)
            pygame.draw.rect(screen, self.color, fallback_rect, 0)
