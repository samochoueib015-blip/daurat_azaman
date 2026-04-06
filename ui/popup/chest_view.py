import pygame
from engine.world.objects.chest import Chest
from engine.player.inventory.player_inventory import PlayerInventory
from engine.items.base_item import BaseItem
from engine.items.item_registry import get_item_class 
from typing import List, Optional, Tuple

class ChestView:
    """
    Displays the contents of a chest and allows transferring items
    between the chest and the player's inventory.
    """
    def __init__(self, screen: pygame.Surface, player_inventory: PlayerInventory, player):
        self.screen = screen
        self.player_inventory = player_inventory
        self.player = player 
        self.is_open = False
        self.opened_chest: Optional[Chest] = None

        self.width = 1000 
        self.height = 600
        self.x = (self.screen.get_width() - self.width) // 2
        self.y = (self.screen.get_height() - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.background_color = (30, 30, 30, 200)
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.highlight_color = (50, 150, 255)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.player_panel_rel = pygame.Rect(10, 10, self.width // 2 - 20, self.height - 20)
        self.player_item_list_start_y_offset = 30
        self.player_max_visible_items = (self.player_panel_rel.height - self.player_item_list_start_y_offset) // (self.font.get_height() + 5)
        self.player_selected_item_index: Optional[int] = None
        self.player_selected_item: Optional[BaseItem] = None

        self.chest_panel_rel = pygame.Rect(self.width // 2 + 10, 10, self.width // 2 - 20, self.height - 20)
        self.chest_item_list_start_y_offset = 30
        self.chest_max_visible_items = (self.chest_panel_rel.height - self.chest_item_list_start_y_offset) // (self.font.get_height() + 5)
        self.chest_selected_item_index: Optional[int] = None
        self.chest_selected_item: Optional[BaseItem] = None

        self.item_list_line_height = self.font.get_height() + 5
        
        self.transfer_button = pygame.Rect(self.x + self.width // 2 - 50, self.y + self.height - 40, 100, 30)

    def open(self, chest: Chest):
        """Opens the chest view for a specific chest."""
        self.opened_chest = chest
        self.is_open = True
        self.player_selected_item_index = None
        self.player_selected_item = None
        self.chest_selected_item_index = None
        self.chest_selected_item = None
        if self.player_inventory.get_items():
            self.player_selected_item_index = 0
            self.player_selected_item = self.player_inventory.get_items()[0]
        if self.opened_chest and self.opened_chest.inventory.get_items():
            self.chest_selected_item_index = 0
            self.chest_selected_item = self.opened_chest.inventory.get_items()[0]
        print(f"Chest '{self.opened_chest.chest_id}' view opened." if self.opened_chest else "Error opening chest: No chest provided.")
        if self.opened_chest:
            self.opened_chest.is_open = True

    def close(self):
        """Closes the chest view."""
        if self.opened_chest:
            self.opened_chest.is_open = False
            self.opened_chest.inventory.save_inventory()
            self.opened_chest = None
        self.is_open = False
        print("Chest view closed.")

    def draw(self):
        """Draws the chest view and its contents."""
        if not self.is_open or not self.opened_chest:
            return
        
        assert self.opened_chest is not None, "chest_view.draw called when opened_chest is None"

        main_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        main_surface.fill(self.background_color)
        pygame.draw.rect(main_surface, self.border_color, main_surface.get_rect(), 2)
        self.screen.blit(main_surface, (self.x, self.y))

        self._draw_inventory_panel(
            self.player_panel_rel, 
            "Player Inventory", 
            self.player_inventory.get_items(), 
            self.player_selected_item_index, 
            self.player_item_list_start_y_offset, 
            self.player_max_visible_items,
            is_player_panel=True
        )

        self._draw_inventory_panel(
            self.chest_panel_rel, 
            f"Chest: {self.opened_chest.chest_id}", 
            self.opened_chest.inventory.get_items(), 
            self.chest_selected_item_index, 
            self.chest_item_list_start_y_offset, 
            self.chest_max_visible_items,
            is_player_panel=False
        )

        self._draw_item_details_panels()

        transfer_abs_rect = self.get_abs_rect(pygame.Rect(self.width // 2 - 50, self.height - 40, 100, 30))
        pygame.draw.rect(self.screen, self.highlight_color, transfer_abs_rect)
        pygame.draw.rect(self.screen, self.border_color, transfer_abs_rect, 2)
        transfer_text = self.font.render("Transfer", True, self.text_color)
        self.screen.blit(transfer_text, transfer_text.get_rect(center=transfer_abs_rect.center))

    def _draw_inventory_panel(self, rel_rect: pygame.Rect, title: str, 
                               items: List[BaseItem], selected_index: Optional[int],
                               start_y_offset: int, max_visible_items: int,
                               is_player_panel: bool):
        """Helper to draw inventory lists."""
        abs_rect = self.get_abs_rect(rel_rect)
        pygame.draw.rect(self.screen, self.border_color, abs_rect, 1)

        title_text = self.font.render(title, True, self.text_color)
        title_text_rect = title_text.get_rect(midleft=(abs_rect.left + 5, abs_rect.top + start_y_offset // 2))
        self.screen.blit(title_text, title_text_rect)

        current_y = abs_rect.top + start_y_offset
        for i, item in enumerate(items):
            if i >= max_visible_items:
                break

            item_text = f"{item.name} x{item.current_stack}"
            text_surface = self.font.render(item_text, True, self.text_color)
            
            item_rect = pygame.Rect(abs_rect.left + 5, current_y, abs_rect.width - 10, self.item_list_line_height - 5)
            
            if i == selected_index:
                pygame.draw.rect(self.screen, self.highlight_color, item_rect, 0)
                pygame.draw.rect(self.screen, self.text_color, item_rect, 1)

            self.screen.blit(text_surface, (item_rect.left, item_rect.centery - text_surface.get_height() // 2))
            current_y += self.item_list_line_height

    def _draw_item_details_panels(self):
        """Draws detail panels for selected items from both inventories."""
        
        item_to_show_details: Optional[BaseItem] = None
        
        if self.player_selected_item:
            item_to_show_details = self.player_selected_item
        elif self.chest_selected_item:
            item_to_show_details = self.chest_selected_item

        if item_to_show_details:
            detail_panel_x = self.x + 10
            detail_panel_y = self.y + self.height - 180
            detail_panel_width = self.width - 20 
            detail_panel_height = 170

            detail_panel_abs_rect = pygame.Rect(detail_panel_x, detail_panel_y, detail_panel_width, detail_panel_height)
            pygame.draw.rect(self.screen, (20, 20, 20), detail_panel_abs_rect)
            pygame.draw.rect(self.screen, self.border_color, detail_panel_abs_rect, 1)

            name_surface = self.font.render(f"Name: {item_to_show_details.name}", True, self.text_color)
            self.screen.blit(name_surface, (detail_panel_abs_rect.left + 10, detail_panel_abs_rect.top + 10))

            value_surface = self.font.render(f"Value: {item_to_show_details.value}g", True, self.text_color)
            self.screen.blit(value_surface, (detail_panel_abs_rect.left + 10, detail_panel_abs_rect.top + 35))

            item_sprite_rect = pygame.Rect(detail_panel_abs_rect.left + detail_panel_abs_rect.width - 70, detail_panel_abs_rect.top + 10, 60, 60)
            item_sprite = item_to_show_details.get_sprite()
            if item_sprite:
                sprite_width, sprite_height = item_sprite.get_size()
                aspect_ratio = sprite_width / sprite_height
                
                if aspect_ratio > 1:
                    scaled_width = 60
                    scaled_height = int(60 / aspect_ratio)
                else:
                    scaled_height = 60
                    scaled_width = int(60 * aspect_ratio)

                scaled_item_sprite = pygame.transform.scale(item_sprite, (scaled_width, scaled_height))
                scaled_sprite_rect = scaled_item_sprite.get_rect(center=item_sprite_rect.center)
                self.screen.blit(scaled_item_sprite, scaled_sprite_rect)
            
            description_rect = pygame.Rect(detail_panel_abs_rect.left + 10, detail_panel_abs_rect.top + 60, 
                                           detail_panel_abs_rect.width - 20, detail_panel_abs_rect.height - 70)
            self._render_text_with_wrapping(
                self.screen,
                item_to_show_details.description,
                self.small_font,
                self.text_color,
                description_rect
            )

    def handle_event(self, event: pygame.event.Event):
        """Handles events for the chest view."""
        if not self.is_open or not self.opened_chest:
            return
        
        assert self.opened_chest is not None, "chest_view.handle_event called when opened_chest is None"

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_pos = (event.pos[0] - self.x, event.pos[1] - self.y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player_panel_abs_rect = self.get_abs_rect(self.player_panel_rel)
                if player_panel_abs_rect.collidepoint(event.pos):
                    local_y = event.pos[1] - (player_panel_abs_rect.top + self.player_item_list_start_y_offset)
                    clicked_index = local_y // self.item_list_line_height
                    current_player_items = self.player_inventory.get_items()
                    if 0 <= clicked_index < len(current_player_items):
                        self.player_selected_item_index = clicked_index
                        self.player_selected_item = current_player_items[clicked_index]
                        self.chest_selected_item = None
                        self.chest_selected_item_index = None
                    return

                chest_panel_abs_rect = self.get_abs_rect(self.chest_panel_rel)
                if chest_panel_abs_rect.collidepoint(event.pos):
                    local_y = event.pos[1] - (chest_panel_abs_rect.top + self.chest_item_list_start_y_offset)
                    clicked_index = local_y // self.item_list_line_height
                    current_chest_items = self.opened_chest.inventory.get_items() 
                    if 0 <= clicked_index < len(current_chest_items):
                        self.chest_selected_item_index = clicked_index
                        self.chest_selected_item = current_chest_items[clicked_index]
                        self.player_selected_item = None
                        self.player_selected_item_index = None
                    return

                transfer_abs_rect = self.get_abs_rect(pygame.Rect(self.width // 2 - 50, self.height - 40, 100, 30))
                if transfer_abs_rect.collidepoint(event.pos):
                    self._handle_transfer()
                    return

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()

    def _handle_transfer(self):
        """
        Attempts to transfer the currently selected item.
        If player item is selected, transfer to chest.
        If chest item is selected, transfer to player.
        """
        assert self.opened_chest is not None, "_handle_transfer called when opened_chest is None"

        quantity_to_transfer = 1

        if self.player_selected_item:
            item = self.player_selected_item
            if self.player_inventory.remove_item(item, quantity_to_transfer):
                item_class = get_item_class(item.item_id)
                if item_class:
                    transferred_item_instance = item_class() 
                    if self.opened_chest.inventory.add_item(transferred_item_instance, quantity_to_transfer): 
                        print(f"Transferred {quantity_to_transfer} {item.name} from Player to Chest.")
                    else:
                        self.player_inventory.add_item(item, quantity_to_transfer)
                        print(f"Failed to transfer {item.name} to Chest (full).")
                else:
                    self.player_inventory.add_item(item, quantity_to_transfer)
                    print(f"Failed to find item class for {item.name}.")
            else:
                print(f"Failed to remove {item.name} from Player inventory.")

        elif self.chest_selected_item:
            item = self.chest_selected_item
            if self.opened_chest.inventory.remove_item(item, quantity_to_transfer): 
                item_class = get_item_class(item.item_id)
                if item_class:
                    transferred_item_instance = item_class()
                    if self.player_inventory.add_item(transferred_item_instance, quantity_to_transfer):
                        print(f"Transferred {quantity_to_transfer} {item.name} from Chest to Player.")
                    else:
                        self.opened_chest.inventory.add_item(item, quantity_to_transfer)
                        print(f"Failed to transfer {item.name} to Player (full).")
                else: 
                    self.opened_chest.inventory.add_item(item, quantity_to_transfer)
                    print(f"Failed to find item class for {item.name}.")
            else:
                print(f"Failed to remove {item.name} from Chest inventory.")
        else:
            print("No item selected for transfer.")

        self._update_selections_after_transfer()

    def _update_selections_after_transfer(self):
        """Ensures selected item indices are still valid after item removal/addition."""
        
        current_player_items = self.player_inventory.get_items()
        
        if self.player_selected_item_index is not None and self.player_selected_item:
            if self.player_selected_item_index < len(current_player_items) and \
               current_player_items[self.player_selected_item_index] is self.player_selected_item:
                pass
            else:
                found_new_index = -1
                for i, item in enumerate(current_player_items):
                    if item.item_id == self.player_selected_item.item_id:
                        found_new_index = i
                        break
                if found_new_index != -1:
                    self.player_selected_item_index = found_new_index
                    self.player_selected_item = current_player_items[found_new_index]
                else:
                    self.player_selected_item_index = None
                    self.player_selected_item = None
        
        if self.player_selected_item_index is None and current_player_items:
            self.player_selected_item_index = 0
            self.player_selected_item = current_player_items[0]
        elif not current_player_items:
            self.player_selected_item_index = None
            self.player_selected_item = None


        assert self.opened_chest is not None, "opened_chest is None in _update_selections_after_transfer"
        current_chest_items = self.opened_chest.inventory.get_items() 

        if self.chest_selected_item_index is not None and self.chest_selected_item:
            if self.chest_selected_item_index < len(current_chest_items) and \
               current_chest_items[self.chest_selected_item_index] is self.chest_selected_item:
                pass
            else:
                found_new_index = -1
                for i, item in enumerate(current_chest_items):
                    if item.item_id == self.chest_selected_item.item_id:
                        found_new_index = i
                        break
                if found_new_index != -1:
                    self.chest_selected_item_index = found_new_index
                    self.chest_selected_item = current_chest_items[found_new_index]
                else:
                    self.chest_selected_item_index = None
                    self.chest_selected_item = None
        
        if self.chest_selected_item_index is None and current_chest_items:
            self.chest_selected_item_index = 0
            self.chest_selected_item = current_chest_items[0]
        elif not current_chest_items:
            self.chest_selected_item_index = None
            self.chest_selected_item = None

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
