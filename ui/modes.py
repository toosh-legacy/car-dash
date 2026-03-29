# ui/modes.py
# Three display modes for the right-side instrument panel.
#
# Layout (right panel, 512 × 480 px):
#
#  ┌─────────────────────────────────┐  y = 0
#  │  TAB BAR  (22 px)               │
#  ├─────────────────────────────────┤  y = 22
#  │                                 │
#  │   MAIN GAUGE AREA  (300 px)     │  y = 22 … 322
#  │                                 │
#  ├─────────────────────────────────┤  y = 322
#  │   MINI GAUGE ROW   ( 72 px)     │  y = 322 … 394
#  │   coolant | oil | battery       │
#  ├─────────────────────────────────┤  y = 394
#  │   RADAR STRIP      ( 86 px)     │  y = 394 … 480
#  └─────────────────────────────────┘

import pygame
import math
import config
from ui.gauges import (draw_analog_gauge, draw_mini_arc,
                        draw_bar_gauge, draw_digital_block, _f,
                        _polar, _angle_rad)

# ── Geometry constants ────────────────────────────────────────
_PX  = config.MAP_PANEL_WIDTH        # 768  left edge of right panel
_PW  = config.GAUGE_PANEL_WIDTH      # 512
_PCX = _PX + _PW // 2               # 1024 horizontal centre
_TAB = 22                            # tab bar height
_MG  = config.MAIN_GAUGE_HEIGHT      # 322  bottom of main gauge area
_GAH = config.GAUGE_AREA_HEIGHT      # 394  bottom of mini-gauge row


# ══════════════════════════════════════════════════════════════
#  SHARED: mode tab bar
# ══════════════════════════════════════════════════════════════

def draw_mode_tabs(screen, current_mode, frame_count):
    modes = [("race", "1  RACE"), ("eco", "2  ECO"), ("normal", "3  NORMAL")]
    tab_w = _PW // 3
    f     = _f(12, bold=True)

    for i, (key, label) in enumerate(modes):
        tx     = _PX + i * tab_w
        active = (key == current_mode)
        theme  = config.DASH_THEME

        if active:
            pulse = (math.sin(frame_count * 0.07) + 1) / 2
            acc   = theme["accent"]
            bg    = tuple(int(c * (0.15 + 0.10 * pulse)) for c in acc)
            pygame.draw.rect(screen, bg, (tx, 0, tab_w, _TAB))
            pygame.draw.rect(screen, acc, (tx, 0, tab_w, _TAB), 1)
            tc = theme["text"]
        else:
            pygame.draw.rect(screen, (18, 17, 10), (tx, 0, tab_w, _TAB))
            pygame.draw.rect(screen, (40, 38, 24), (tx, 0, tab_w, _TAB), 1)
            tc = (70, 66, 44)

        s = f.render(label, True, tc)
        screen.blit(s, (tx + (tab_w - s.get_width()) // 2,
                        _TAB // 2 - s.get_height() // 2))


# ══════════════════════════════════════════════════════════════
#  SHARED: mini gauge strip
#  Shown in every mode — coolant / oil / battery.
#  No numbers elsewhere in the UI repeat these values.
# ══════════════════════════════════════════════════════════════

def draw_mini_gauge_strip(screen, engine, theme):
    y_strip = _MG          # 322
    strip_h = _GAH - _MG  # 72

    # Strip background
    bg = pygame.Surface((_PW, strip_h), pygame.SRCALPHA)
    bg.fill((12, 11, 4, 215))
    screen.blit(bg, (_PX, y_strip))

    # Top separator line
    pygame.draw.line(screen, (65, 60, 30),
                     (_PX, y_strip), (_PX + _PW, y_strip), 1)

    # Mini gauge radius and center y
    r  = 24
    cy = y_strip + 30    # 352

    # Three horizontal positions
    cx_l = _PX + 88      # 856
    cx_c = _PCX          # 1024
    cx_r = _PX + _PW - 88  # 1192

    draw_mini_arc(screen,
                  engine["coolant_temp"],
                  config.MIN_COOLANT, config.MAX_COOLANT,
                  cx_l, cy, r,
                  "COOLANT", "°F", theme, redline=228)

    draw_mini_arc(screen,
                  engine["oil_temp"],
                  config.MIN_OIL, config.MAX_OIL,
                  cx_c, cy, r,
                  "OIL", "°F", theme, redline=248)

    draw_mini_arc(screen,
                  engine["battery_v"],
                  config.MIN_BATT, config.MAX_BATT,
                  cx_r, cy, r,
                  "BATT", "V", theme)

    # Thin vertical separators between gauges
    for sep_cx in ((cx_l + cx_c) // 2, (cx_c + cx_r) // 2):
        pygame.draw.line(screen, (38, 36, 20),
                         (sep_cx, y_strip + 8), (sep_cx, y_strip + strip_h - 8), 1)


# ══════════════════════════════════════════════════════════════
#  RACE MODE
#
#  Left bar  — throttle (functional green, fills upward)
#  Right bar — brake    (functional red,   fills upward)
#  Centre    — large tachometer
#              ├── Gear number (large, upper face)
#              ├── Speed digital inset (lower face, left)
#              └── Boost digital inset (lower face, right)
#  G-force bubble inside lower face deadzone
# ══════════════════════════════════════════════════════════════

_BAR_W = 20
_BAR_M = 6   # bar margin from panel edge

def draw_race_panel(screen, data, theme, frame_count):
    speed    = data["speed"]
    rpm      = data["rpm"]
    gear     = data["gear"]
    throttle = data["throttle"]
    brake    = data["brake"]
    boost    = data["boost"]
    g        = data["g_force"]

    bar_y = _TAB + 14
    bar_h = _MG - bar_y - 8

    # ── Throttle bar (left, functional green) ─────────────────
    _draw_pedal_bar(screen, throttle,
                    _PX + _BAR_M, bar_y, _BAR_W, bar_h,
                    (42, 188, 58), "T", frame_count)

    # ── Brake bar (right, functional red) ─────────────────────
    _draw_pedal_bar(screen, brake,
                    _PX + _PW - _BAR_M - _BAR_W, bar_y, _BAR_W, bar_h,
                    (205, 42, 35), "B", frame_count)

    # ── Tachometer ────────────────────────────────────────────
    r  = 125
    cx = _PCX
    cy = _TAB + (_MG - _TAB) // 2 + 5   # vertically centred ≈ 172

    draw_analog_gauge(
        screen, rpm, 0, config.MAX_RPM,
        cx, cy, r,
        label="", unit="",
        theme=theme,
        major_step=1000, minor_step=500,
        scale_div=1000,
        redline=config.RPM_REDLINE,
        show_center_text=False,
    )

    # ── Gear — large, upper face ──────────────────────────────
    f_glbl = _f(11)
    f_gnum = _f(58, bold=True)
    gl_s   = f_glbl.render("GEAR", True, theme["sub"])
    gn_s   = f_gnum.render(str(gear),  True, theme["accent"])
    screen.blit(gl_s, (cx - gl_s.get_width() // 2, cy - 72))
    screen.blit(gn_s, (cx - gn_s.get_width() // 2, cy - 58))

    # ── Speed inset block (lower-left quadrant of face) ───────
    sb_w, sb_h = 78, 42
    sb_x = cx - 46 - sb_w
    sb_y = cy + 30
    draw_digital_block(screen, "SPEED", str(int(speed)), "mph",
                       sb_x, sb_y, sb_w, sb_h, theme)

    # ── Boost inset block (lower-right quadrant of face) ──────
    bb_w, bb_h = 68, 42
    bb_x = cx + 46
    bb_y = cy + 30
    draw_digital_block(screen, "BOOST", f"{boost:.1f}", "psi",
                       bb_x, bb_y, bb_w, bb_h, theme)

    # ── G-force bubble (bottom face deadzone) ─────────────────
    _draw_g_ball(screen, g["lat"], g["lon"], cx, cy + 82, 22, theme)


def _draw_pedal_bar(screen, value, x, y, w, h, fill_color, label, frame_count):
    """Vertical bar filling upward — F1 telemetry style."""
    f_lbl = _f(10)
    f_pct = _f(10, bold=True)

    # Label above
    lbl_s = f_lbl.render(label, True, (95, 90, 65))
    screen.blit(lbl_s, (x + (w - lbl_s.get_width()) // 2, y - 13))

    # Background
    pygame.draw.rect(screen, (24, 23, 15), (x, y, w, h), border_radius=3)

    # Fill (bottom-up)
    ratio  = max(0.0, min(1.0, value / 100.0))
    fill_h = int(ratio * h)
    if fill_h > 3:
        dr, dg, db = fill_color
        dark = (max(0, dr - 60), max(0, dg - 60), max(0, db - 60))
        pygame.draw.rect(screen, dark,
                         (x, y + h - fill_h, w, fill_h), border_radius=3)
        # Bright leading edge
        edge_h = max(3, min(7, fill_h // 6))
        pygame.draw.rect(screen, fill_color,
                         (x, y + h - fill_h, w, edge_h), border_radius=3)

    # Tick lines at 25 / 50 / 75 %
    for pct in (25, 50, 75):
        ty  = y + h - int(pct / 100.0 * h)
        col = (60, 56, 36) if pct <= int(value) else (36, 34, 20)
        pygame.draw.line(screen, col, (x, ty), (x + w, ty), 1)

    # Border
    pygame.draw.rect(screen, (50, 46, 28), (x, y, w, h), 1, border_radius=3)

    # % value below
    pct_s = f_pct.render(f"{int(value)}%",
                          True, fill_color if value > 5 else (45, 42, 25))
    screen.blit(pct_s, (x + (w - pct_s.get_width()) // 2, y + h + 2))


def _draw_g_ball(screen, lat_g, lon_g, cx, cy, r, theme):
    """Bullseye G-force indicator. Dot moves: lateral left/right, longitudinal up/down."""
    cx, cy = int(cx), int(cy)

    pygame.draw.circle(screen, (18, 17, 10), (cx, cy), r)
    # Rings at 0.5G and 1.0G
    pygame.draw.circle(screen, (42, 40, 26), (cx, cy), r // 2, 1)
    pygame.draw.circle(screen, (42, 40, 26), (cx, cy), r,      1)
    # Cross-hairs
    pygame.draw.line(screen, (40, 38, 24), (cx - r, cy), (cx + r, cy), 1)
    pygame.draw.line(screen, (40, 38, 24), (cx, cy - r), (cx, cy + r), 1)

    # Ball (clamped to circle)
    max_g = 1.5
    bx = cx + int(lat_g / max_g * r * 0.88)
    by = cy - int(lon_g / max_g * r * 0.88)
    dist = math.sqrt((bx - cx) ** 2 + (by - cy) ** 2)
    if dist > r * 0.88:
        s  = r * 0.88 / dist
        bx = cx + int((bx - cx) * s)
        by = cy + int((by - cy) * s)

    # Glow halo
    ar, ag, ab = theme["accent"]
    glow = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(glow, (ar, ag, ab, 80), (8, 8), 7)
    screen.blit(glow, (bx - 8, by - 8))

    pygame.draw.circle(screen, theme["accent"], (bx, by), 4)
    pygame.draw.circle(screen, (240, 240, 244), (bx, by), 2)

    # "G" label
    f = _f(9)
    s = f.render("G", True, (75, 70, 48))
    screen.blit(s, (cx - s.get_width() // 2, cy + r + 2))


# ══════════════════════════════════════════════════════════════
#  ECO MODE
#
#  Centre — speed gauge with translucent eco-zone arc overlay
#            (25–65 mph sweet spot painted on the face)
#  Below gauge:
#    Power/regen bar  (amber=consumption | green=coasting)
#    Instant MPG  |  Trip Avg MPG  |  Range
#  No digital speed — the gauge IS the speed display.
# ══════════════════════════════════════════════════════════════

def draw_eco_panel(screen, data, theme, frame_count):
    speed    = data["speed"]
    throttle = data["throttle"]
    brake    = data["brake"]
    econ     = data["economy"]

    r  = 108
    cx = _PCX
    cy = _TAB + r + (r + 22)   # ensure bezel clears tab bar
    # cy = 22 + 108 + 130 = ... let me compute properly:
    # bezel top must be >= TAB (22). bezel top = cy - (r+22).
    # cy - (r+22) >= 22  →  cy >= r+44 = 152
    cy = r + 44  # = 152

    # ── Speed gauge ───────────────────────────────────────────
    draw_analog_gauge(
        screen, speed, 0, config.MAX_SPEED,
        cx, cy, r,
        label="SPEED", unit="mph",
        theme=theme,
        major_step=20, minor_step=10,
        show_center_text=True,
    )

    # Eco zone arc overlay (25–65 mph)
    _draw_eco_zone(screen, cx, cy, r - 4, 25, 65, config.MAX_SPEED, theme)

    # ── Below gauge: power/regen bar ─────────────────────────
    bezel_bot = cy + r + 22     # bottom of bezel
    bar_x = _PX + 24
    bar_w = _PW - 48
    bar_h = 14

    # Label row
    f_bar_lbl = _f(11)
    regen_s = f_bar_lbl.render("← REGEN", True, (42, 175, 58))
    power_s = f_bar_lbl.render("POWER →", True, (195, 120, 18))
    bar_lbl_y = bezel_bot + 6
    screen.blit(regen_s, (bar_x, bar_lbl_y))
    screen.blit(power_s, (bar_x + bar_w - power_s.get_width(), bar_lbl_y))

    bar_y = bar_lbl_y + regen_s.get_height() + 3
    _draw_power_regen_bar(screen, throttle, brake, bar_x, bar_y, bar_w, bar_h)

    # ── Stat blocks: instant MPG | trip MPG | range ───────────
    blk_y = bar_y + bar_h + 10
    blk_h = min(40, _MG - blk_y - 4)
    blk_w = (_PW - 50) // 3

    for i, (lbl, val, unit) in enumerate([
        ("INSTANT", f"{econ['mpg_instant']:.0f}", "MPG"),
        ("TRIP AVG", f"{econ['mpg_trip']:.1f}",   "MPG"),
        ("RANGE",   f"{int(econ['range_mi'])}",   "mi"),
    ]):
        bx = _PX + 22 + i * (blk_w + 3)
        if blk_h >= 28:
            draw_digital_block(screen, lbl, val, unit,
                               bx, blk_y, blk_w, blk_h, theme)


def _draw_eco_zone(screen, cx, cy, r, lo, hi, max_val, theme):
    """Translucent amber arc marking the efficient speed band."""
    a_lo = _angle_rad(lo, 0, max_val, 220, 260)
    a_hi = _angle_rad(hi, 0, max_val, 220, 260)

    surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    ar   = (1, 1, r * 2, r * 2)
    acc  = theme["accent"]
    pygame.draw.arc(surf, (*acc, 38), ar, a_hi, a_lo, 7)
    screen.blit(surf, (cx - r - 1, cy - r - 1))

    # Boundary tick marks at zone edges
    for a in (a_lo, a_hi):
        ox, oy = _polar(cx, cy, r + 2, a)
        ix, iy = _polar(cx, cy, r - 10, a)
        pygame.draw.line(screen, acc, (int(ox), int(oy)), (int(ix), int(iy)), 2)


def _draw_power_regen_bar(screen, throttle, brake, x, y, w, h):
    """Bidirectional bar: right = power demand (amber-red), left = regen (green)."""
    mid = x + w // 2

    pygame.draw.rect(screen, (24, 22, 12), (x, y, w, h), border_radius=4)

    # Power (right half)
    pw = int((throttle / 100.0) * (w // 2))
    if pw > 2:
        t  = throttle / 100.0
        rc = int(175 + t * 65)
        gc = int(110 - t * 100)
        pygame.draw.rect(screen, (rc, max(0, gc), 5),
                         (mid, y + 1, pw, h - 2), border_radius=4)

    # Regen (left half)
    bw = int((brake / 100.0) * (w // 2))
    if bw > 2:
        pygame.draw.rect(screen, (28, 168, 55),
                         (mid - bw, y + 1, bw, h - 2), border_radius=4)

    # Centre marker
    pygame.draw.rect(screen, (165, 155, 100), (mid - 1, y - 2, 2, h + 4))
    pygame.draw.rect(screen, (50, 46, 26), (x, y, w, h), 1, border_radius=4)


# ══════════════════════════════════════════════════════════════
#  NORMAL MODE
#
#  Centre — speed gauge  (same size as eco)
#            └── smooth-score tiny arc inside lower deadzone
#  Below gauge:
#    Drive style meter  GENTLE ──── SPIRITED
#    Trip blocks: distance | time | avg speed
#  Engine health in mini gauge strip (shared — no LEDs needed here).
# ══════════════════════════════════════════════════════════════

def draw_normal_panel(screen, data, theme, frame_count):
    speed       = data["speed"]
    drive_style = data["drive_style"]
    trip        = data["trip"]
    smooth      = trip["smooth_score"]

    r  = 108
    cy = r + 44   # same as eco

    cx = _PCX

    # ── Speed gauge ───────────────────────────────────────────
    draw_analog_gauge(
        screen, speed, 0, config.MAX_SPEED,
        cx, cy, r,
        label="SPEED", unit="mph",
        theme=theme,
        major_step=20, minor_step=10,
        show_center_text=True,
    )

    # Smooth-score arc inside lower deadzone of face
    _draw_smooth_arc(screen, smooth, cx, cy + 32, 22, theme)

    # ── Drive style meter ─────────────────────────────────────
    bezel_bot = cy + r + 22
    ds_x = _PX + 24
    ds_w = _PW - 48
    ds_h = 14
    ds_y = bezel_bot + 18    # leave room for label above

    _draw_style_meter(screen, drive_style, ds_x, ds_y, ds_w, ds_h, theme)

    # ── Trip computer blocks ───────────────────────────────────
    blk_y = ds_y + ds_h + 10
    blk_h = min(40, _MG - blk_y - 4)
    blk_w = (_PW - 50) // 3

    for i, (lbl, val, unit) in enumerate([
        ("DISTANCE", f"{trip['distance']:.1f}", "mi"),
        ("TIME",     _fmt_time(trip["time_min"]), ""),
        ("AVG SPEED", f"{trip['avg_speed']:.0f}", "mph"),
    ]):
        bx = _PX + 22 + i * (blk_w + 3)
        if blk_h >= 28:
            draw_digital_block(screen, lbl, val, unit,
                               bx, blk_y, blk_w, blk_h, theme)


def _draw_smooth_arc(screen, score, cx, cy, r, theme):
    """Tiny arc gauge showing smooth-driving score. Green = smooth, amber/red = rough."""
    cx, cy = int(cx), int(cy)
    rect   = (cx - r, cy - r, r * 2, r * 2)
    pygame.draw.arc(screen, (30, 28, 18), rect,
                    math.radians(-40), math.radians(220), 3)
    a_val = _angle_rad(score, 0, 100, 220, 260)
    if score > 0:
        if   score >= 70: col = (42, 195, 62)
        elif score >= 40: col = (200, 172, 28)
        else:             col = (205, 45, 35)
        pygame.draw.arc(screen, col, rect, a_val, math.radians(220), 3)
    f = _f(9)
    s = f.render(f"{int(score)}", True, theme["sub"])
    screen.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))


def _draw_style_meter(screen, score, x, y, w, h, theme):
    """
    Colour-zoned horizontal bar. White needle marks current driving style.
    Green = gentle / amber = normal / orange-red = spirited.
    """
    # Zone fills
    zones = [
        (0.00, 0.33, (22, 95, 32)),
        (0.33, 0.66, (118, 78, 16)),
        (0.66, 1.00, (135, 28, 18)),
    ]
    for lo, hi, col in zones:
        zx = x + int(lo * w)
        zw = int((hi - lo) * w)
        pygame.draw.rect(screen, col, (zx, y, zw, h))

    # Needle
    nx = x + int(max(0.0, min(1.0, score / 100.0)) * w)
    pygame.draw.rect(screen, (232, 232, 238), (nx - 1, y - 4, 2, h + 8))

    # Border
    pygame.draw.rect(screen, (52, 48, 28), (x, y, w, h), 1)

    # Labels above
    f    = _f(11)
    f_st = _f(11, bold=True)
    screen.blit(f.render("GENTLE",   True, (42, 175, 52)),
                (x, y - 16))
    screen.blit(f.render("SPIRITED", True, (195, 50, 40)),
                (x + w - f.render("SPIRITED", True, (0,0,0)).get_width(), y - 16))

    if   score < 33: style, sc = "SMOOTH DRIVING",   (42, 185, 52)
    elif score < 66: style, sc = "NORMAL DRIVING",   (195, 172, 35)
    else:            style, sc = "SPIRITED DRIVING",  (205, 50, 38)
    sl_s = f_st.render(style, True, sc)
    screen.blit(sl_s, (x + w // 2 - sl_s.get_width() // 2, y - 16))


def _fmt_time(mins):
    m = int(mins);  h = m // 60;  m = m % 60
    return f"{h}:{m:02d}" if h > 0 else f"{m}m"
