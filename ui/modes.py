# ui/modes.py
# Three display modes: RACE, ECO, CARE.
# Each function draws the right-side gauge panel above the radar strip.

import pygame
import math
import config
from ui.gauges import (draw_analog_gauge, draw_bar_gauge,
                        draw_digital_block, _f, _polar, _angle_rad)

# Panel geometry (right side, above radar)
_PX  = config.MAP_PANEL_WIDTH        # left edge of right panel  (768)
_PW  = config.GAUGE_PANEL_WIDTH      # width of right panel       (512)
_GAH = config.GAUGE_AREA_HEIGHT      # height above radar         (322)
_PCX = _PX + _PW // 2               # horizontal centre          (1024)


# ── Shared: mode tab indicator ────────────────────────────────

def draw_mode_tabs(screen, current_mode, frame_count):
    """Three small tabs at the very top of the right panel."""
    modes  = [("race", "1 RACE"), ("eco", "2 ECO"), ("care", "3 CARE")]
    tab_w  = _PW // 3
    tab_h  = 22
    f      = _f(12, bold=True)

    for i, (key, label) in enumerate(modes):
        tx    = _PX + i * tab_w
        theme = config.THEMES[key]
        active = (key == current_mode)

        if active:
            # Pulsing glow when active
            pulse = (math.sin(frame_count * 0.06) + 1) / 2
            bg = tuple(int(c * (0.25 + 0.12 * pulse)) for c in theme["accent"])
            pygame.draw.rect(screen, bg, (tx, 0, tab_w, tab_h))
            pygame.draw.rect(screen, theme["accent"], (tx, 0, tab_w, tab_h), 1)
            text_color = theme["text"]
        else:
            pygame.draw.rect(screen, (25, 25, 28), (tx, 0, tab_w, tab_h))
            pygame.draw.rect(screen, (45, 45, 50), (tx, 0, tab_w, tab_h), 1)
            text_color = (80, 80, 88)

        surf = f.render(label, True, text_color)
        screen.blit(surf, (tx + (tab_w - surf.get_width()) // 2,
                           tab_h // 2 - surf.get_height() // 2))


# ── RACE MODE ─────────────────────────────────────────────────
# Large tachometer centred in the right panel.
# Speed + gear shown as digital insets. Boost bar at bottom.

def draw_race_panel(screen, data, theme, frame_count):
    speed  = data["speed"]
    rpm    = data["rpm"]
    gear   = data["gear"]
    engine = data["engine"]

    TAB_H   = 22     # reserved for mode tabs at top
    RADAR_Y = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT

    # ── Big tachometer ──────────────────────────────────────
    r   = 122
    cx  = _PCX
    cy  = TAB_H + (_GAH - TAB_H) // 2 + 5   # vertically centred in gauge area

    draw_analog_gauge(
        screen, rpm, 0, config.MAX_RPM,
        cx, cy, r,
        label="RPM", unit="×1000",
        theme=theme,
        major_step=1000, minor_step=500,
        scale_div=1000,
        redline=config.RPM_REDLINE,
    )

    # ── GEAR indicator (large, inside the upper face) ────────
    gear_y = cy - r + 52    # inside the face, upper area
    f_gear_lbl = _f(11)
    f_gear_num = _f(42, bold=True)

    g_lbl = f_gear_lbl.render("GEAR", True, theme["sub"])
    g_num = f_gear_num.render(str(gear), True, theme["accent"])
    screen.blit(g_lbl, (cx - g_lbl.get_width() // 2, gear_y))
    screen.blit(g_num, (cx - g_num.get_width() // 2, gear_y + 14))

    # ── Speed inset (lower-right face area) ──────────────────
    spd_bw, spd_bh = 90, 46
    spd_bx = cx + 42
    spd_by = cy + 38
    draw_digital_block(screen, "SPEED", str(int(speed)), "mph",
                       spd_bx, spd_by, spd_bw, spd_bh, theme)

    # ── Boost inset (lower-left face area) ────────────────────
    boost = engine.get("boost_psi", 0.0)
    bst_bw, bst_bh = 80, 46
    bst_bx = cx - 42 - bst_bw
    bst_by = cy + 38
    draw_digital_block(screen, "BOOST", f"{boost:.1f}", "psi",
                       bst_bx, bst_by, bst_bw, bst_bh, theme)

    # ── Throttle strip (between tach bottom and radar) ────────
    strip_y = RADAR_Y - 30
    strip_x = _PX + 24
    strip_w = _PW - 48

    draw_bar_gauge(screen,
                   engine["throttle"], 0, 100,
                   strip_x, strip_y, strip_w, 12,
                   "THROTTLE", "%", theme,
                   warn_ratio=0.88, danger_ratio=0.96)


# ── ECO MODE ─────────────────────────────────────────────────
# Centred speed gauge. Three economy bars below. Range indicator.

def draw_eco_panel(screen, data, theme, frame_count):
    speed = data["speed"]
    econ  = data["economy"]

    TAB_H  = 22
    r      = 108
    cx     = _PCX
    cy     = TAB_H + r + 28      # leave room for tabs + bezel top

    # ── Speed gauge ──────────────────────────────────────────
    draw_analog_gauge(
        screen, speed, 0, config.MAX_SPEED,
        cx, cy, r,
        label="SPEED", unit="mph",
        theme=theme,
        major_step=20, minor_step=10,
    )

    # ── Economy bars ─────────────────────────────────────────
    bar_x  = _PX + 24
    bar_w  = _PW - 48
    bar_h  = 12
    RADAR_Y = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT

    # Position bars in the space between gauge bottom and radar
    gauge_bottom = cy + r + 30   # approximate bottom of bezel
    available    = RADAR_Y - gauge_bottom - 10
    gap          = max(10, available // 4)
    by           = gauge_bottom + gap // 2

    draw_bar_gauge(screen,
                   econ["mpg_instant"], 0, 55,
                   bar_x, by, bar_w, bar_h,
                   "INSTANT MPG", "mpg", theme,
                   warn_ratio=1.0, danger_ratio=1.0)  # no warn for eco bars
    by += gap
    draw_bar_gauge(screen,
                   econ["mpg_trip"], 0, 55,
                   bar_x, by, bar_w, bar_h,
                   "TRIP AVG MPG", "mpg", theme,
                   warn_ratio=1.0, danger_ratio=1.0)
    by += gap
    draw_bar_gauge(screen,
                   econ["eco_score"], 0, 100,
                   bar_x, by, bar_w, bar_h,
                   "ECO SCORE", "/100", theme,
                   warn_ratio=1.0, danger_ratio=1.0)

    # ── Range display ─────────────────────────────────────────
    rng_bw, rng_bh = 110, 44
    rng_bx = cx - rng_bw // 2
    rng_by = cy + 28     # inside lower face area
    draw_digital_block(screen, "RANGE",
                       str(int(econ["range_mi"])), "miles",
                       rng_bx, rng_by, rng_bw, rng_bh, theme)


# ── CARE MODE ─────────────────────────────────────────────────
# Two small arc gauges (coolant + oil temp), battery + throttle bars,
# and a 4-corner tyre-pressure display.

def draw_care_panel(screen, data, theme, frame_count):
    engine = data["engine"]
    tyres  = data["tyres"]

    TAB_H   = 22
    RADAR_Y = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT

    r   = 88
    gap = 16
    # Two gauges side by side, vertically centred in gauge area
    total_gauge_w = 2 * (r + 22) + gap + 40   # bezel clearance
    cx_left  = _PCX - total_gauge_w // 4 - gap // 2
    cx_right = _PCX + total_gauge_w // 4 + gap // 2
    cy       = TAB_H + r + 28

    # ── Coolant temperature ───────────────────────────────────
    draw_analog_gauge(
        screen,
        engine["coolant_temp"],
        config.MIN_COOLANT, config.MAX_COOLANT,
        cx_left, cy, r,
        label="COOLANT", unit="°F",
        theme=theme,
        major_step=20, minor_step=10,
        redline=230,
    )

    # ── Oil temperature ───────────────────────────────────────
    draw_analog_gauge(
        screen,
        engine["oil_temp"],
        config.MIN_OIL, config.MAX_OIL,
        cx_right, cy, r,
        label="OIL TEMP", unit="°F",
        theme=theme,
        major_step=20, minor_step=10,
        redline=250,
    )

    # ── Bars: battery + throttle ──────────────────────────────
    bar_x   = _PX + 20
    bar_w   = _PW - 40
    bar_h   = 11
    gauge_bot = cy + r + 30
    avail     = RADAR_Y - gauge_bot - 55   # 55 reserved for tyre row
    gap_bar   = max(8, avail // 3)
    by        = gauge_bot + 4

    draw_bar_gauge(screen,
                   engine["battery_v"], 11.0, 15.0,
                   bar_x, by, bar_w, bar_h,
                   "BATTERY", "V", theme,
                   warn_ratio=0.88, danger_ratio=0.96)
    by += gap_bar
    draw_bar_gauge(screen,
                   engine["throttle"], 0, 100,
                   bar_x, by, bar_w, bar_h,
                   "THROTTLE", "%", theme,
                   warn_ratio=0.85, danger_ratio=0.95)

    # ── Tyre pressure grid (2×2, bottom strip) ────────────────
    tp_y    = RADAR_Y - 50
    tp_w    = 88
    tp_h    = 40
    centres = {
        "fl": (_PX + _PW // 4 - tp_w // 2,         tp_y),
        "fr": (_PX + _PW * 3 // 4 - tp_w // 2,     tp_y),
    }
    # Label row
    f_tp_h = _f(11)
    hdr = f_tp_h.render("TYRE PRESSURES (PSI)", True, theme["sub"])
    screen.blit(hdr, (_PCX - hdr.get_width() // 2, tp_y - 16))

    positions = [
        ("FL", tyres["fl"], _PX + 20),
        ("FR", tyres["fr"], _PX + _PW // 2 - tp_w // 2 - 10),
        ("RL", tyres["rl"], _PX + _PW // 2 + 10),
        ("RR", tyres["rr"], _PX + _PW - tp_w - 20),
    ]
    for label, psi, bx in positions:
        ok = 30.0 <= psi <= 35.0
        t_accent = theme if ok else {**theme, "accent": theme["arc_warn"],
                                      "text": theme["arc_warn"]}
        draw_digital_block(screen, label, f"{psi:.1f}", "psi",
                           bx, tp_y, tp_w, tp_h, t_accent)
