from engine.world.chunk import Chunk
from engine.world.outdoor.biomes.fields import FieldsBiome
from engine.world.outdoor.biomes.coast import CoastBiome
from engine.world.outdoor.biomes.desert import DesertBiome
from engine.world.outdoor.biomes.mountain import MountainBiome
from engine.world.outdoor.biomes.forest import ForestBiome
from engine.world.outdoor.biomes.ocean import OceanBiome
from engine.world.outdoor.biomes.river import RiverBiome
from engine.world.outdoor.biomes.snow import SnowBiome
from engine.world.outdoor.biomes.road import RoadBiome
from engine.world.pixel_map_reader import PixelMapReader
import random

class WorldGenerator:
    """
    Generates chunks for the game world based on specified biomes.
    """

    TILE_SIZE_IN_METERS = 2

    CHUNK_SIZE_METERS = Chunk.CHUNK_SIZE_TILES * TILE_SIZE_IN_METERS

    def __init__(self, seed=None):
        self.seed = seed
        self.biomes = {
            "fields": FieldsBiome(),
            "coast": CoastBiome(),
            "desert": DesertBiome(),
            "mountain": MountainBiome(),
            "forest": ForestBiome(),
            "ocean": OceanBiome(),
            "river": RiverBiome(),
            "snow": SnowBiome(),
            "road": RoadBiome()

        }
        self.biome_names = list(self.biomes.keys())

        random.seed(seed if seed is not None else 42)

        self.pixel_map_reader = PixelMapReader()

    def generate_chunk(self, chunk_x, chunk_y):
        """
        Generates a new Chunk at the given chunk coordinates,
        determining its biome based on the pixel_map.png.
        """
        new_chunk = Chunk(chunk_x, chunk_y)

        world_center_x = (chunk_x * self.CHUNK_SIZE_METERS) + (self.CHUNK_SIZE_METERS / 2)
        world_center_y = (chunk_y * self.CHUNK_SIZE_METERS) + (self.CHUNK_SIZE_METERS / 2)

        selected_biome_name = self.pixel_map_reader.get_biome_type(world_center_x, world_center_y)

        selected_biome_generator = self.biomes.get(selected_biome_name)

        if selected_biome_name == "static_zone":
            print(f"DEBUG: Chunk ({chunk_x}, {chunk_y}) flagged as STATIC ZONE. Special loading logic will be needed here.")
            selected_biome_generator = self.biomes.get("ocean")
            print("         (Currently defaulting to Ocean for static zones for demonstration purposes.)")

        if selected_biome_generator:
            print(f"Generating chunk ({chunk_x}, {chunk_y}) as {selected_biome_name} biome (from map data).")
            new_chunk.populate(selected_biome_generator.generate_tile)
        else:

            print(f"WARNING: No generator found for biome '{selected_biome_name}' from map. Defaulting to Ocean.")
            new_chunk.populate(self.biomes["ocean"].generate_tile)

        return new_chunk
