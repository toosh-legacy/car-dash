# ui/map_view.py
# GPS map panel — left 60% of the screen.
# Downloads and caches OpenStreetMap tiles, draws position marker.

import pygame
import math
import io
import requests
import config
from ui.gauges import _f

_tile_cache = {}
TILE_SIZE   = 256
ZOOM_LEVEL  = 15

HEADERS = {"User-Agent": "CarDash/2.0"}


def _lat_lon_to_tile(lat, lon, zoom):
    n = 2 ** zoom
    tx = int((lon + 180.0) / 360.0 * n)
    ty = int(
        (1.0 - math.log(math.tan(math.radians(lat)) +
         1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n
    )
    return tx, ty


def _lat_lon_to_pixel_offset(lat, lon, zoom, ctx, cty):
    n  = 2 ** zoom
    fx = (lon + 180.0) / 360.0 * n
    fy = (1.0 - math.log(math.tan(math.radians(lat)) +
           1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n
    return int((fx - ctx) * TILE_SIZE), int((fy - cty) * TILE_SIZE)


def _fetch_tile(zoom, tx, ty):
    key = (zoom, tx, ty)
    if key in _tile_cache:
        return _tile_cache[key]
    url = f"https://tile.openstreetmap.org/{zoom}/{tx}/{ty}.png"
    try:
        r = requests.get(url, headers=HEADERS, timeout=3)
        if r.status_code == 200:
            surf = pygame.image.load(io.BytesIO(r.content)).convert()
            _tile_cache[key] = surf
            return surf
    except Exception:
        pass
    return None


def draw_map_panel(screen, gps_data, mode, theme):
    lat, lon   = gps_data["lat"], gps_data["lon"]
    pw, ph     = config.MAP_PANEL_WIDTH, config.SCREEN_HEIGHT

    ctx, cty   = _lat_lon_to_tile(lat, lon, ZOOM_LEVEL)
    tiles_x    = math.ceil(pw / TILE_SIZE) + 2
    tiles_y    = math.ceil(ph / TILE_SIZE) + 2
    hx, hy     = tiles_x // 2, tiles_y // 2
    opx, opy   = _lat_lon_to_pixel_offset(lat, lon, ZOOM_LEVEL, ctx, cty)

    gps_sx, gps_sy = pw // 2, ph // 2

    # ── Draw tiles ───────────────────────────────────────────
    for dx in range(-hx, hx + 1):
        for dy in range(-hy, hy + 1):
            tx   = ctx + dx
            ty   = cty + dy
            sx   = gps_sx + dx * TILE_SIZE - opx
            sy   = gps_sy + dy * TILE_SIZE - opy

            if sx > pw or sy > ph or sx + TILE_SIZE < 0 or sy + TILE_SIZE < 0:
                continue

            tile = _fetch_tile(ZOOM_LEVEL, tx, ty)
            if tile:
                screen.blit(tile, (sx, sy))
            else:
                pygame.draw.rect(screen, (38, 38, 42),
                                 (sx, sy, TILE_SIZE, TILE_SIZE))

    # ── Dark overlay (night-mode tint) ───────────────────────
    overlay = pygame.Surface((pw, ph), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 68))    # ~27% dark tint
    screen.blit(overlay, (0, 0))

    # ── Clip right edge ──────────────────────────────────────
    pygame.draw.rect(screen, config.DARK_GRAY,
                     (pw, 0, config.SCREEN_WIDTH - pw, ph))

    # ── GPS position marker ───────────────────────────────────
    accent = theme["accent"]
    # Outer glow ring
    for off, alpha in ((18, 35), (14, 60), (10, 100)):
        ring = pygame.Surface((off * 2, off * 2), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*accent, alpha), (off, off), off)
        screen.blit(ring, (gps_sx - off, gps_sy - off))
    # Solid ring + centre dot
    pygame.draw.circle(screen, accent,         (gps_sx, gps_sy), 9)
    pygame.draw.circle(screen, config.DARK_GRAY, (gps_sx, gps_sy), 5)
    pygame.draw.circle(screen, (255, 255, 255), (gps_sx, gps_sy), 3)

    # ── Crosshair ────────────────────────────────────────────
    cr_len, cr_gap = 22, 10
    col_cr = (*accent, 160)
    for dx_cr, dy_cr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        start = (gps_sx + dx_cr * cr_gap, gps_sy + dy_cr * cr_gap)
        end   = (gps_sx + dx_cr * (cr_gap + cr_len),
                 gps_sy + dy_cr * (cr_gap + cr_len))
        pygame.draw.line(screen, accent, start, end, 1)

    # ── Mode badge (top-left of map) ─────────────────────────
    badge_w, badge_h = 90, 26
    badge_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
    badge_surf.fill((*theme["bg_tint"], 200))
    pygame.draw.rect(badge_surf, accent, (0, 0, badge_w, badge_h), 1, border_radius=4)
    f_badge = _f(13, bold=True)
    b_text  = f_badge.render(f"  {theme['name']} MODE", True, accent)
    badge_surf.blit(b_text, (4, (badge_h - b_text.get_height()) // 2))
    screen.blit(badge_surf, (8, 8))

    # ── Coordinate overlay (bottom-left) ─────────────────────
    f_coord = _f(13)
    coord_s = f_coord.render(f"  {lat:.5f}, {lon:.5f}", True, (210, 210, 210))
    bg      = pygame.Surface((coord_s.get_width() + 12, 22), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 170))
    screen.blit(bg,      (6, ph - 28))
    screen.blit(coord_s, (6, ph - 26))
