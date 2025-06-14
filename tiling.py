import math
from typing import Generator

from pymupdf import Rect, Point


def cover_with_tiles(region: Rect, tile_size: Point) -> Generator[Rect, None, None]:
    tile_count_h, tile_count_v = math.ceil(region.width / tile_size.x), math.ceil(region.height / tile_size.y)
    tiled_width, tiled_height = tile_count_h * tile_size.x, tile_count_v * tile_size.y
    region_center_x, region_center_y = Point((region.x0 + region.x1) / 2, (region.y0 + region.y1) / 2)
    tiled_tl = Point(region_center_x - tiled_width / 2, region_center_y - tiled_height / 2)

    for row in range(tile_count_v):
        for col in range(tile_count_h):
            x, y = tiled_tl.x + tile_size.x * col, tiled_tl.y + tile_size.y * row
            yield Rect(x, y, x + tile_size.x, y + tile_size.y)
