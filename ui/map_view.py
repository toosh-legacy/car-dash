# ui/map_view.py
# Fetches and draws OpenStreetMap tiles centered on current GPS position.

import pygame
import math
import io
import requests
import config

# --- Tile cache ---
# Stores downloaded tiles so we don't re-fetch the same one every frame
# Key = (zoom, tile_x, tile_y), Value = pygame Surface
_tile_cache = {}

TILE_SIZE  = 256   # OSM tiles are always 256x256 pixels
ZOOM_LEVEL = 15    # Good detail for car navigation

HEADERS = {
    # OpenStreetMap requires a User-Agent header
    "User-Agent": "SportsDashSimulator/1.0"
}


def _lat_lon_to_tile(lat, lon, zoom):
    """Convert GPS coordinates to OSM tile x/y numbers."""
    n = 2 ** zoom
    tile_x = int((lon + 180.0) / 360.0 * n)
    tile_y = int(
        (1.0 - math.log(math.tan(math.radians(lat)) +
        1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n
    )
    return tile_x, tile_y


def _lat_lon_to_pixel_offset(lat, lon, zoom, center_tile_x, center_tile_y):
    """
    Returns how many pixels offset the GPS point is from the
    top-left corner of the center tile.
    Used to keep your position dot centered on screen.
    """
    n = 2 ** zoom
    # Fractional tile position
    frac_x = (lon + 180.0) / 360.0 * n
    frac_y = (1.0 - math.log(math.tan(math.radians(lat)) +
              1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n

    # Pixel offset from center tile origin
    px = (frac_x - center_tile_x) * TILE_SIZE
    py = (frac_y - center_tile_y) * TILE_SIZE
    return int(px), int(py)


def _fetch_tile(zoom, tile_x, tile_y):
    """
    Downloads a single map tile from OpenStreetMap.
    Returns a pygame Surface, or None if it fails.
    Caches results so each tile is only downloaded once.
    """
    key = (zoom, tile_x, tile_y)

    # Return cached tile if we already have it
    if key in _tile_cache:
        return _tile_cache[key]

    url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"

    try:
        response = requests.get(url, headers=HEADERS, timeout=3)
        if response.status_code == 200:
            # Convert raw image bytes → PIL image → pygame Surface
            image_bytes = io.BytesIO(response.content)
            pygame_surface = pygame.image.load(image_bytes)
            pygame_surface = pygame_surface.convert()  # optimize for blitting
            _tile_cache[key] = pygame_surface
            return pygame_surface
    except Exception:
        pass  # If fetch fails, return None — we'll draw a placeholder

    return None


def draw_map_panel(screen, gps_data):
    """
    Draws the GPS map panel on the left side of the screen.

    Parameters:
        screen   — pygame display surface
        gps_data — dict with 'lat' and 'lon' keys from simulator
    """

    lat = gps_data["lat"]
    lon = gps_data["lon"]

    panel_w = config.MAP_PANEL_WIDTH
    panel_h = config.SCREEN_HEIGHT

    # Get the center tile for our GPS position
    center_tx, center_ty = _lat_lon_to_tile(lat, lon, ZOOM_LEVEL)

    # How many tiles do we need to fill the panel?
    # Panel is 768px wide, tiles are 256px — so we need a 3x3 grid minimum
    tiles_x = math.ceil(panel_w / TILE_SIZE) + 2   # +2 for overlap on edges
    tiles_y = math.ceil(panel_h / TILE_SIZE) + 2

    half_x = tiles_x // 2
    half_y = tiles_y // 2

    # Pixel offset of GPS point within center tile
    offset_px, offset_py = _lat_lon_to_pixel_offset(
        lat, lon, ZOOM_LEVEL, center_tx, center_ty
    )

    # Where on screen should the GPS position appear?
    # We want it centered in the panel
    gps_screen_x = panel_w // 2
    gps_screen_y = panel_h // 2

    # Draw each tile in the grid
    for dx in range(-half_x, half_x + 1):
        for dy in range(-half_y, half_y + 1):
            tile_x = center_tx + dx
            tile_y = center_ty + dy

            # Where on screen does this tile go?
            screen_x = gps_screen_x + dx * TILE_SIZE - offset_px
            screen_y = gps_screen_y + dy * TILE_SIZE - offset_py

            # Skip tiles completely outside the panel
            if screen_x > panel_w or screen_y > panel_h:
                continue
            if screen_x + TILE_SIZE < 0 or screen_y + TILE_SIZE < 0:
                continue

            tile_surface = _fetch_tile(ZOOM_LEVEL, tile_x, tile_y)

            if tile_surface:
                screen.blit(tile_surface, (screen_x, screen_y))
            else:
                # Placeholder if tile failed to load
                pygame.draw.rect(
                    screen,
                    (40, 40, 40),
                    (screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                )

    # --- Clip to panel boundary ---
    # Draw a black rectangle outside the panel to hide any tile overflow
    pygame.draw.rect(screen, config.DARK_GRAY, (panel_w, 0, config.SCREEN_WIDTH, panel_h))

    # --- GPS position dot ---
    # Outer ring
    pygame.draw.circle(screen, config.ACCENT, (gps_screen_x, gps_screen_y), 12)
    # Inner dot
    pygame.draw.circle(screen, config.WHITE, (gps_screen_x, gps_screen_y), 6)

    # --- Crosshair lines ---
    pygame.draw.line(screen, config.ACCENT,
                     (gps_screen_x - 20, gps_screen_y),
                     (gps_screen_x + 20, gps_screen_y), 1)
    pygame.draw.line(screen, config.ACCENT,
                     (gps_screen_x, gps_screen_y - 20),
                     (gps_screen_x, gps_screen_y + 20), 1)

    # --- Coordinate overlay ---
    font_small = pygame.font.SysFont("consolas", 14)
    coord_text = font_small.render(f"  {lat:.5f}, {lon:.5f}", True, config.WHITE)

    # Draw a semi-dark background behind the text for readability
    bg = pygame.Surface((coord_text.get_width() + 10, 22))
    bg.set_alpha(180)
    bg.fill((0, 0, 0))
    screen.blit(bg,        (8, panel_h - 28))
    screen.blit(coord_text,(8, panel_h - 26))