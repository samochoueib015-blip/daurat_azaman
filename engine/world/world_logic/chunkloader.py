from engine.world.outdoor.world_generator import WorldGenerator
from engine.world.chunk import Chunk
from engine.display import Display
from engine.world.pixel_map_reader import PixelMapReader

class ChunkLoader:
    """
    Manages loading, unloading, and providing access to chunks around the player.
    """
    LOAD_RADIUS = 4

    def __init__(self):
        self.loaded_chunks = {}
        self.world_generator = WorldGenerator()
        self.current_player_chunk_x = -9999999
        self.current_player_chunk_y = -9999999
        self.player_world_x_meters = 0.0
        self.player_world_y_meters = 0.0

    def _get_chunk(self, chunk_x, chunk_y):
        """
        Retrieves a chunk from memory or generates it if it doesn't exist.
        """
        chunk_coords = (chunk_x, chunk_y)
        if chunk_coords not in self.loaded_chunks:
            self.loaded_chunks[chunk_coords] = self.world_generator.generate_chunk(chunk_x, chunk_y)
        return self.loaded_chunks[chunk_coords]

    def update(self, player_world_x, player_world_y):
        """
        Updates the loaded chunks based on the player's current world position in pixels.
        Loads new chunks and unloads distant ones if the player crosses a chunk boundary.
        :param player_world_x: Player's x-coordinate in absolute world pixels.
        :param player_world_y: Player's y-coordinate in absolute world pixels.
        """
        self.player_world_x_meters = player_world_x / Display.PIXELS_PER_METER
        self.player_world_y_meters = player_world_y / Display.PIXELS_PER_METER

        player_chunk_x = int(self.player_world_x_meters / self.world_generator.CHUNK_SIZE_METERS)
        player_chunk_y = int(self.player_world_y_meters / self.world_generator.CHUNK_SIZE_METERS)

        if player_chunk_x != self.current_player_chunk_x or \
           player_chunk_y != self.current_player_chunk_y:
            
            self.current_player_chunk_x = player_chunk_x
            self.current_player_chunk_y = player_chunk_y
            self._load_and_unload_chunks()

    def _load_and_unload_chunks(self):
        """
        Determines which chunks should be loaded/unloaded based on the current player chunk.
        """
        chunks_to_keep = set()

        min_cx = self.current_player_chunk_x - self.LOAD_RADIUS
        max_cx = self.current_player_chunk_x + self.LOAD_RADIUS
        min_cy = self.current_player_chunk_y - self.LOAD_RADIUS
        max_cy = self.current_player_chunk_y + self.LOAD_RADIUS

        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                chunk_coords = (cx, cy)
                chunks_to_keep.add(chunk_coords)
                if chunk_coords not in self.loaded_chunks:
                    self.loaded_chunks[chunk_coords] = self.world_generator.generate_chunk(cx, cy)


        chunks_to_remove = [c for c in self.loaded_chunks if c not in chunks_to_keep]
        for c in chunks_to_remove:
            del self.loaded_chunks[c]

    def get_chunks_to_draw(self):
        """
        Returns a list of all currently loaded chunks.
        """
        return list(self.loaded_chunks.values())

    def get_player_coordinates_for_map_debug(self):
        """
        Returns the player's world coordinates (in meters) and their
        corresponding pixel coordinates on the pixel_map.png for debugging.
        """
        world_x_m = self.player_world_x_meters
        world_y_m = self.player_world_y_meters

        pixel_x_on_map = world_x_m / PixelMapReader.WORLD_SCALE_METERS_PER_PIXEL
        pixel_y_on_map = world_y_m / PixelMapReader.WORLD_SCALE_METERS_PER_PIXEL

        return (world_x_m, world_y_m, pixel_x_on_map, pixel_y_on_map)

    def get_tile_world_pixel_coords(self, global_tile_x, global_tile_y):
        """
        Calculates the top-left pixel coordinates in the world for a given global tile index.
        """
        world_pixel_x = global_tile_x * Display.TILE_SIZE_PIXELS
        world_pixel_y = global_tile_y * Display.TILE_SIZE_PIXELS
        return world_pixel_x, world_pixel_y
