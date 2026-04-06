import pygame

class UserInputManager:
    """
    Manages user input events and provides the current state of relevant controls.
    """
    def __init__(self):

        self._keys_pressed = {
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_w: False,
            pygame.K_s: False,
        }
        self._mouse_buttons_pressed = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
        }

    def handle_event(self, event):
        """
        Processes a single Pygame event to update the state of keys.
        This method should be called for every event in the Pygame event queue.
        """

        if event.type == pygame.KEYDOWN:

            if event.key in self._keys_pressed:
                self._keys_pressed[event.key] = True

        elif event.type == pygame.KEYUP:

            if event.key in self._keys_pressed:
                self._keys_pressed[event.key] = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in self._mouse_buttons_pressed:
                self._mouse_buttons_pressed[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in self._mouse_buttons_pressed:
                self._mouse_buttons_pressed[event.button] = False


    def get_movement_vector(self):
        """
        Calculates and returns the normalized movement vector (dx, dy)
        based on the currently pressed directional keys.
        """
        dx, dy = 0, 0
        if self._keys_pressed[pygame.K_a]:
            dx -= 1
        if self._keys_pressed[pygame.K_d]:
            dx += 1
        if self._keys_pressed[pygame.K_w]:
            dy -= 1
        if self._keys_pressed[pygame.K_s]:
            dy += 1
        return dx, dy

    def clear_movement_keys(self):
        for key in self._keys_pressed:
            self._keys_pressed[key] = False

    def is_mouse_button_down(self, button: int) -> bool:
        """
        Returns True if the specified mouse button is currently pressed down.
        """
        return self._mouse_buttons_pressed.get(button, False)
