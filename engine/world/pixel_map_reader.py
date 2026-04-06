import pygame
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class PixelMapReader:
    """
    Reads the main pixel map (pixel_map.png) to determine biome types and
    special zone designations for given world coordinates.
    """

    WORLD_SCALE_METERS_PER_PIXEL = 10

    STATIC_ZONE_COLOR = (255, 0, 0)
    ROAD_COLOR        = (0, 0, 0)
    OCEAN_COLOR       = (0, 0, 128)
    COAST_SAND_COLOR  = (240, 230, 128)
    FIELDS_COLOR      = (160, 200, 80)
    FOREST_COLOR      = (34, 139, 34)
    MOUNTAIN_COLOR    = (0, 100, 0)
    DESERT_COLOR      = (210, 180, 140)
    RIVER_COLOR       = (70, 130, 180)
    SNOW_COLOR        = (248, 248, 255)

    COLOR_MATCH_TOLERANCE = 5

    MAP_FILE_PATH = os.path.join(os.path.dirname(__file__), 'pixel_map.png')


    def __init__(self):
        self.pixel_map_surface = None
        self._load_pixel_map()

        self.biome_color_map = {

            self.STATIC_ZONE_COLOR: "static_zone",

            self.ROAD_COLOR: "road",

            self.SNOW_COLOR: "snow",
            self.MOUNTAIN_COLOR: "mountain",
            self.FOREST_COLOR: "forest",
            self.FIELDS_COLOR: "fields",
            self.DESERT_COLOR: "desert",
            self.COAST_SAND_COLOR: "coast",
            self.RIVER_COLOR: "river",
            self.OCEAN_COLOR: "ocean",

        }
        self.default_biome_name = "ocean"

    def _load_pixel_map(self):
        """Loads the pixel map image into a Pygame Surface."""
        if not os.path.exists(self.MAP_FILE_PATH):
            logging.error(f"Pixel map file not found: {self.MAP_FILE_PATH}")
            raise FileNotFoundError(f"Required pixel map '{self.MAP_FILE_PATH}' does not exist.")
        try:

            self.pixel_map_surface = pygame.image.load(self.MAP_FILE_PATH).convert_alpha()
            logging.info(f"Loaded pixel map: {self.MAP_FILE_PATH} ({self.pixel_map_surface.get_width()}x{self.pixel_map_surface.get_height()} pixels)")
        except pygame.error as e:
            logging.error(f"Could not load pixel map: {e}")
            raise

    def is_color_close(self, color1, color2, tolerance):
        """
        Checks if two RGB colors are within a given tolerance for each channel.
        color1 and color2 are (R, G, B) tuples.
        """

        diff_r = abs(color1[0] - color2[0])
        diff_g = abs(color1[1] - color2[1])
        diff_b = abs(color1[2] - color2[2])
        return diff_r <= tolerance and diff_g <= tolerance and diff_b <= tolerance

    def get_biome_type(self, world_x_meters, world_y_meters):
        """
        Determines the biome or special zone type at the given world coordinates.
        Applies a planetary wrapping effect for seamless world boundaries.

        Args:
            world_x_meters (float): The X coordinate in world meters.
            world_y_meters (float): The Y coordinate in world meters.
        Returns:
            str: The name of the biome (e.g., "forest", "ocean", "static_zone", "road").
        """
        if self.pixel_map_surface is None:
            logging.error("Pixel map not loaded. Cannot determine biome type.")
            return self.default_biome_name

        map_pixel_x = int(world_x_meters / self.WORLD_SCALE_METERS_PER_PIXEL)
        map_pixel_y = int(world_y_meters / self.WORLD_SCALE_METERS_PER_PIXEL)

        map_width = self.pixel_map_surface.get_width()
        map_height = self.pixel_map_surface.get_height()

        actual_map_pixel_x = (map_pixel_x % map_width + map_width) % map_width

        cycle_height = 2 * map_height
        
        normalized_y = map_pixel_y % cycle_height
        if normalized_y < 0:
            normalized_y += cycle_height

        if normalized_y < map_height:
            actual_map_pixel_y = normalized_y
        else:
            actual_map_pixel_y = cycle_height - 1 - normalized_y
        
        actual_map_pixel_x = max(0, min(map_width - 1, actual_map_pixel_x))
        actual_map_pixel_y = max(0, min(map_height - 1, actual_map_pixel_y))

        try:

            pixel_color_rgba = self.pixel_map_surface.get_at((actual_map_pixel_x, actual_map_pixel_y))

            pixel_color_rgb = (pixel_color_rgba[0], pixel_color_rgba[1], pixel_color_rgba[2])

            if self.is_color_close(pixel_color_rgb, self.STATIC_ZONE_COLOR, self.COLOR_MATCH_TOLERANCE):
                return self.biome_color_map[self.STATIC_ZONE_COLOR]

            if self.is_color_close(pixel_color_rgb, self.ROAD_COLOR, self.COLOR_MATCH_TOLERANCE):
                return self.biome_color_map[self.ROAD_COLOR]

            for color_rgb, biome_name in self.biome_color_map.items():
                if color_rgb == self.STATIC_ZONE_COLOR or color_rgb == self.ROAD_COLOR:
                    continue

                if self.is_color_close(pixel_color_rgb, color_rgb, self.COLOR_MATCH_TOLERANCE):
                    return biome_name

            logging.warning(f"Unknown pixel color {pixel_color_rgb} at map coordinates ({actual_map_pixel_x}, {actual_map_pixel_y}). Defaulting to '{self.default_biome_name}'.")
            return self.default_biome_name

        except IndexError:
            logging.error(f"IndexError accessing pixel map at ({actual_map_pixel_x}, {actual_map_pixel_y}). Defaulting to '{self.default_biome_name}'.")
            return self.default_biome_name
        except Exception as e:
            logging.error(f"An unexpected error occurred while reading pixel map: {e}. Defaulting to '{self.default_biome_name}'.")
            return self.default_biome_name
