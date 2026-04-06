import pygame
from engine.player.inventory.player_inventory import PlayerInventory
from engine.player.player import Player 
from engine.items.base_item import BaseItem
from engine.items.weapons.swords.iron_sword import IronSword
from typing import List, Optional, Tuple

class InventoryView:
    """
    Displays the player's inventory as a pop-up window,
    following a specific layout with item selection and details.
    """
    def __init__(self, screen: pygame.Surface, player_inventory: PlayerInventory, player: Player):
        self.screen = screen
        self.player_inventory = player_inventory
        self.player: Player = player
        self.is_open = False

        self.width = 800
        self.height = 500
        self.x = (self.screen.get_width() - self.width) // 2
        self.y = (self.screen.get_height() - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.background_color = (30, 30, 30, 200)
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.highlight_color = (50, 150, 255)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.player_sprite_area_rel = pygame.Rect(10, 10, 150, self.height - 20)

        self.item_list_area_rel = pygame.Rect(self.player_sprite_area_rel.right + 10, 10, 250, self.height - 20)

        right_panel_x = self.item_list_area_rel.right + 10
        right_panel_width = self.width - right_panel_x - 10

        self.item_name_header_rel = pygame.Rect(right_panel_x, 10, right_panel_width, 30)
        self.item_value_header_rel = pygame.Rect(right_panel_x, self.item_name_header_rel.bottom + 5, right_panel_width, 30)

        self.selected_item_sprite_area_rel = pygame.Rect(right_panel_x, self.item_value_header_rel.bottom + 10, right_panel_width, 150)
        self.description_stats_area_rel = pygame.Rect(right_panel_x, self.selected_item_sprite_area_rel.bottom + 10, right_panel_width, self.height - self.selected_item_sprite_area_rel.bottom - 20)
        self.item_list_start_y_offset = 30
        self.item_list_line_height = self.font.get_height() + 5
        self.max_visible_items = (self.item_list_area_rel.height - self.item_list_start_y_offset) // self.item_list_line_height

        self.selected_item_index: Optional[int] = None
        self.selected_item: Optional[BaseItem] = None

    def toggle_visibility(self):
        """Toggles the inventory window open or closed."""
        self.is_open = not self.is_open
        print(f"Inventory is now {'open' if self.is_open else 'closed'}.")
        if self.is_open:
            print(self.player_inventory)
            self.selected_item_index = None
            self.selected_item = None
            if self.player_inventory.get_items():
                self.selected_item_index = 0
                self.selected_item = self.player_inventory.get_items()[0]


    def draw(self):
        """Draws the inventory window and its contents."""
        if not self.is_open:
            return

        main_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        main_surface.fill(self.background_color)
        pygame.draw.rect(main_surface, self.border_color, main_surface.get_rect(), 2) # Border
        self.screen.blit(main_surface, (self.x, self.y))

        player_sprite_abs_rect = self.get_abs_rect(self.player_sprite_area_rel)
        pygame.draw.rect(self.screen, self.border_color, player_sprite_abs_rect, 1)

        player_text = self.font.render("Player-Sprite", True, self.text_color)

        player_text_rect = player_text.get_rect(center=(player_sprite_abs_rect.centerx, player_sprite_abs_rect.top + 15))
        self.screen.blit(player_text, player_text_rect)

        player_draw_rect = player_sprite_abs_rect.inflate(-10, -10)
        player_draw_rect.top = player_text_rect.bottom + 5
        player_draw_rect.height = player_sprite_abs_rect.height - (player_draw_rect.top - player_sprite_abs_rect.top) - (player_sprite_abs_rect.height - player_draw_rect.bottom)
        
        player_sprite = self.player.get_current_sprite() 
        if player_sprite:

            sprite_width, sprite_height = player_sprite.get_size()
            target_width_ratio = player_draw_rect.width / sprite_width
            target_height_ratio = player_draw_rect.height / sprite_height

            scale_factor = min(target_width_ratio, target_height_ratio)
            
            scaled_sprite = pygame.transform.scale(player_sprite, (int(sprite_width * scale_factor), int(sprite_height * scale_factor)))
            
            scaled_sprite_rect = scaled_sprite.get_rect(center=player_draw_rect.center)
            self.screen.blit(scaled_sprite, scaled_sprite_rect)


        item_list_abs_rect = self.get_abs_rect(self.item_list_area_rel)
        pygame.draw.rect(self.screen, self.border_color, item_list_abs_rect, 1)

        item_name_header_text = self.font.render("Inventory (Items x Stack)", True, self.text_color)
        item_name_header_rect = item_name_header_text.get_rect(midleft=(item_list_abs_rect.left + 5, item_list_abs_rect.top + self.item_list_start_y_offset // 2))
        self.screen.blit(item_name_header_text, item_name_header_rect)


        current_y = item_list_abs_rect.top + self.item_list_start_y_offset
        current_items = self.player_inventory.get_items()
        
        for i, item in enumerate(current_items):
            if i >= self.max_visible_items:
                break

            item_text = f"{item.name} x{item.current_stack}"
            text_surface = self.font.render(item_text, True, self.text_color)
            
            item_rect = pygame.Rect(item_list_abs_rect.left + 5, current_y, item_list_abs_rect.width - 10, self.item_list_line_height - 5)
            
            if i == self.selected_item_index:
                pygame.draw.rect(self.screen, self.highlight_color, item_rect, 0)
                pygame.draw.rect(self.screen, self.text_color, item_rect, 1)

            self.screen.blit(text_surface, (item_rect.left, item_rect.centery - text_surface.get_height() // 2))
            current_y += self.item_list_line_height

        if self.selected_item:

            item_name_header_abs_rect = self.get_abs_rect(self.item_name_header_rel)
            pygame.draw.rect(self.screen, self.border_color, item_name_header_abs_rect, 1)
            name_text_surface = self.font.render(f"Name: {self.selected_item.name}", True, self.text_color)
            name_text_rect = name_text_surface.get_rect(midleft=(item_name_header_abs_rect.left + 5, item_name_header_abs_rect.centery))
            self.screen.blit(name_text_surface, name_text_rect)

            item_value_header_abs_rect = self.get_abs_rect(self.item_value_header_rel)
            pygame.draw.rect(self.screen, self.border_color, item_value_header_abs_rect, 1)
            value_text_surface = self.font.render(f"Value: {self.selected_item.value}g", True, self.text_color)
            value_text_rect = value_text_surface.get_rect(midleft=(item_value_header_abs_rect.left + 5, item_value_header_abs_rect.centery))
            self.screen.blit(value_text_surface, value_text_rect)

            selected_item_sprite_abs_rect = self.get_abs_rect(self.selected_item_sprite_area_rel)
            pygame.draw.rect(self.screen, self.border_color, selected_item_sprite_abs_rect, 1)
            
            item_sprite = self.selected_item.get_sprite()
            if item_sprite:

                sprite_width, sprite_height = item_sprite.get_size()
                target_width_ratio = selected_item_sprite_abs_rect.width / sprite_width
                target_height_ratio = selected_item_sprite_abs_rect.height / sprite_height
                scale_factor = min(target_width_ratio, target_height_ratio)
                
                scaled_item_sprite = pygame.transform.scale(item_sprite, (int(sprite_width * scale_factor), int(sprite_height * scale_factor)))
                scaled_item_sprite_rect = scaled_item_sprite.get_rect(center=selected_item_sprite_abs_rect.center)
                self.screen.blit(scaled_item_sprite, scaled_item_sprite_rect)

            description_stats_abs_rect = self.get_abs_rect(self.description_stats_area_rel)
            pygame.draw.rect(self.screen, self.border_color, description_stats_abs_rect, 1)
            
            current_y_for_text = description_stats_abs_rect.top + 5
            
            description_lines_rendered = self._render_text_with_wrapping(
                self.screen,
                self.selected_item.description,
                self.small_font,
                self.text_color,
                pygame.Rect(description_stats_abs_rect.left + 5, current_y_for_text,
                            description_stats_abs_rect.width - 10, description_stats_abs_rect.height - 10)
            )
            
            current_y_for_text += description_lines_rendered * self.small_font.get_height() + 5

            if self.selected_item is not None and isinstance(self.selected_item, IronSword): 
                iron_sword_item: IronSword = self.selected_item
                
                if current_y_for_text + self.small_font.get_height() <= description_stats_abs_rect.bottom:

                    damage_text = self.small_font.render(f"Damage: {iron_sword_item.damage}", True, self.text_color)
                    self.screen.blit(damage_text, (description_stats_abs_rect.left + 5, current_y_for_text))
                    current_y_for_text += self.small_font.get_height() + 5


    def handle_event(self, event: pygame.event.Event):
        """Handles events for the inventory view."""
        if not self.is_open:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            item_list_abs_rect = self.get_abs_rect(self.item_list_area_rel)

            if item_list_abs_rect.collidepoint(mouse_pos):
                local_y = mouse_pos[1] - (item_list_abs_rect.top + self.item_list_start_y_offset)
                
                clicked_index_in_visible_list = local_y // self.item_list_line_height

                current_items = self.player_inventory.get_items()
                if 0 <= clicked_index_in_visible_list < len(current_items) and \
                   clicked_index_in_visible_list < self.max_visible_items:
                    
                    self.selected_item_index = clicked_index_in_visible_list 
                    self.selected_item = current_items[clicked_index_in_visible_list] 

    def get_abs_rect(self, relative_rect: pygame.Rect) -> pygame.Rect:
        """Converts a relative Rect (relative to main inventory window) to an absolute screen Rect."""
        return pygame.Rect(
            self.x + relative_rect.x,
            self.y + relative_rect.y,
            relative_rect.width,
            relative_rect.height
        )

    def _render_text_with_wrapping(self, surface: pygame.Surface, text: str, font: pygame.font.Font, color: Tuple[int, int, int], rect: pygame.Rect) -> int:
        """
        Renders text within a rectangle, wrapping words if necessary.
        Returns the number of lines rendered.
        """
        if not text:
            return 0

        words = text.split(' ')
        lines: List[str] = []
        current_line: List[str] = []
        
        if rect.width <= 0:
            return 0

        for word in words:
            test_text = ' '.join(current_line + [word])
            
            if font.size(test_text)[0] > rect.width:
                if not current_line:

                    broken_word = ""
                    for char_idx, char in enumerate(word):
                        test_part = broken_word + char
                        if font.size(test_part)[0] > rect.width and broken_word:
                            lines.append(broken_word)
                            broken_word = char
                        else:
                            broken_word += char
                    if broken_word: lines.append(broken_word)
                else:
                    lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))

        y_offset = rect.top
        lines_rendered = 0
        for line in lines:
            line_surface = font.render(line, True, color)
            if y_offset + line_surface.get_height() <= rect.bottom:
                surface.blit(line_surface, (rect.left, y_offset))
                y_offset += line_surface.get_height()
                lines_rendered += 1
            else:
                break
        return lines_rendered
