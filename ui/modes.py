# ui/modes.py
# Three display modes.  Each draw_*_panel() renders the right-side gauge
# area (above the radar strip).  All coordinates are absolute screen pixels.

import pygame
import math
import config
from ui.gauges import (draw_analog_gauge, draw_bar_gauge,
                        draw_digital_block, draw_led, _f, _polar, _angle_rad)

# ── Panel geometry ────────────────────────────────────────────
_PX   = config.MAP_PANEL_WIDTH        # 768  – left edge of right panel
_PW   = config.GAUGE_PANEL_WIDTH      # 512  – width of right panel
_SH   = config.SCREEN_HEIGHT          # 480
_GAH  = config.GAUGE_AREA_HEIGHT      # 322  – height above radar
_PCX  = _PX + _PW // 2               # 1024 – horizontal centre

_TAB_H   = 22                          # mode tab bar height
_RAD_Y   = _SH - config.RADAR_PANEL_HEIGHT   # 322 – top of radar strip
_BODY_Y  = _TAB_H                      # usable body starts here
_BODY_H  = _RAD_Y - _TAB_H            # 300 – usable height for gauges


# ══════════════════════════════════════════════════════════════
#  MODE TABS
# ══════════════════════════════════════════════════════════════

def draw_mode_tabs(screen, current_mode, frame_count):
    modes = [("race", "1  RACE"), ("eco", "2  ECO"), ("normal", "3  NORMAL")]
    tab_w = _PW // 3
    f     = _f(12, bold=True)

    for i, (key, label) in enumerate(modes):
        tx     = _PX + i * tab_w
        theme  = config.THEMES[key]
        active = (key == current_mode)

        if active:
            pulse  = (math.sin(frame_count * 0.07) + 1) / 2
            r, g, b = theme["accent"]
            bg = (int(r * (0.18 + 0.10 * pulse)),
                  int(g * (0.18 + 0.10 * pulse)),
                  int(b * (0.18 + 0.10 * pulse)))
            pygame.draw.rect(screen, bg, (tx, 0, tab_w, _TAB_H))
            pygame.draw.rect(screen, theme["accent"], (tx, 0, tab_w, _TAB_H), 1)
            tc = theme["text"]
        else:
            pygame.draw.rect(screen, (22, 22, 26), (tx, 0, tab_w, _TAB_H))
            pygame.draw.rect(screen, (42, 42, 48), (tx, 0, tab_w, _TAB_H), 1)
            tc = (72, 72, 80)

        s = f.render(label, True, tc)
        screen.blit(s, (tx + (tab_w - s.get_width()) // 2,
                        _TAB_H // 2 - s.get_height() // 2))


# ══════════════════════════════════════════════════════════════
#  SHARED HELPER: vertical pedal bar (F1-style)
# ══════════════════════════════════════════════════════════════

def _draw_pedal_bar(screen, value, x, y, w, h, fill_color, label, frame_count=0):
    """
    Vertical bar that fills from the BOTTOM up — like F1 telemetry overlays.
    Tick marks at 25 / 50 / 75 / 100 %.
    """
    f_lbl = _f(10)
    f_val = _f(11, bold=True)

    # Label at top
    lbl_s = f_lbl.render(label, True, (130, 130, 140))
    screen.blit(lbl_s, (x + (w - lbl_s.get_width()) // 2, y - 15))

    # Background track
    pygame.draw.rect(screen, (28, 28, 32), (x, y, w, h), border_radius=3)

    # Fill (bottom-up)
    ratio  = max(0.0, min(1.0, value / 100.0))
    fill_h = int(ratio * h)
    if fill_h > 2:
        # Gradient: darker at bottom, brighter near current level
        r, g, b = fill_color
        dark_col  = (max(0,r-60), max(0,g-60), max(0,b-60))
        pygame.draw.rect(screen, dark_col,
                         (x, y + h - fill_h, w, fill_h), border_radius=3)
        # Bright top slice (the "active" level indicator)
        slice_h = max(3, min(8, fill_h // 6))
        pygame.draw.rect(screen, fill_color,
                         (x, y + h - fill_h, w, slice_h), border_radius=3)

    # Tick marks at 25/50/75/100
    for pct in (25, 50, 75, 100):
        ty = y + h - int(pct / 100.0 * h)
        col = (80, 80, 88) if pct < int(value) else (48, 48, 55)
        pygame.draw.line(screen, col, (x, ty), (x + w, ty), 1)

    # Border
    pygame.draw.rect(screen, (55, 55, 65), (x, y, w, h), 1, border_radius=3)

    # Current % value at bottom
    pct_s = f_val.render(f"{int(value)}%", True, fill_color if value > 5 else (55,55,65))
    screen.blit(pct_s, (x + (w - pct_s.get_width()) // 2, y + h + 3))


# ══════════════════════════════════════════════════════════════
#  RACE MODE
#  Left edge: throttle bar (green, fills up)
#  Right edge: brake bar   (red,   fills up)
#  Centre: large tachometer  —  gear large in face, speed + boost insets
#  G-force bubble indicator inside the lower face area
# ══════════════════════════════════════════════════════════════

_BAR_W      = 20
_BAR_MARGIN = 6

def draw_race_panel(screen, data, theme, frame_count):
    speed    = data["speed"]
    rpm      = data["rpm"]
    gear     = data["gear"]
    throttle = data["throttle"]
    brake    = data["brake"]
    boost    = data["boost"]
    g        = data["g_force"]

    # ── Pedal bars ────────────────────────────────────────────
    bar_y = _BODY_Y + 18
    bar_h = _BODY_H - 36

    # Throttle — left edge
    throt_x = _PX + _BAR_MARGIN
    _draw_pedal_bar(screen, throttle, throt_x, bar_y, _BAR_W, bar_h,
                    (55, 200, 70), "T", frame_count)

    # Brake — right edge
    brake_x = _PX + _PW - _BAR_MARGIN - _BAR_W
    _draw_pedal_bar(screen, brake, brake_x, bar_y, _BAR_W, bar_h,
                    (215, 45, 38), "B", frame_count)

    # ── Tachometer (centered between bars) ───────────────────
    r  = 115
    cx = _PCX
    cy = _BODY_Y + _BODY_H // 2 + 8    # slight downward nudge

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

    # ── Content inside the tach face ─────────────────────────

    # GEAR — very large, upper-centre of face
    f_gear_label = _f(11)
    f_gear_num   = _f(56, bold=True)

    gl_s = f_gear_label.render("GEAR", True, theme["sub"])
    gn_s = f_gear_num.render(str(gear),  True, theme["accent"])
    screen.blit(gl_s, (cx - gl_s.get_width() // 2, cy - 68))
    screen.blit(gn_s, (cx - gn_s.get_width() // 2, cy - 52))

    # RPM digital (small, below gear)
    f_rpm_d = _f(13)
    rpm_s   = f_rpm_d.render(f"{int(rpm):,} RPM", True, theme["sub"])
    screen.blit(rpm_s, (cx - rpm_s.get_width() // 2, cy + 14))

    # ── Speed inset (lower-left of face) ─────────────────────
    spd_w, spd_h = 82, 44
    spd_x = cx - 46 - spd_w
    spd_y = cy + 32
    draw_digital_block(screen, "SPEED", str(int(speed)), "mph",
                       spd_x, spd_y, spd_w, spd_h, theme)

    # ── Boost inset (lower-right of face) ────────────────────
    bst_w, bst_h = 72, 44
    bst_x = cx + 46
    bst_y = cy + 32
    draw_digital_block(screen, "BOOST", f"{boost:.1f}", "psi",
                       bst_x, bst_y, bst_w, bst_h, theme)

    # ── G-force bubble ───────────────────────────────────────
    _draw_g_ball(screen, g["lat"], g["lon"], cx, cy + 82, 24, theme)


def _draw_g_ball(screen, lat_g, lon_g, cx, cy, r, theme):
    """
    Bullseye G-force indicator.
    Positive lon_g (acceleration) → ball moves toward top.
    Positive lat_g (right cornering) → ball moves right.
    """
    cx, cy = int(cx), int(cy)

    # Background
    pygame.draw.circle(screen, (22, 22, 26), (cx, cy), r)

    # Rings at 0.5G and 1.0G
    for ring_r, col in ((r // 2, (50,50,60)), (r, (50,50,60))):
        pygame.draw.circle(screen, col, (cx, cy), ring_r, 1)

    # Cross-hairs
    pygame.draw.line(screen, (48, 48, 58), (cx - r, cy), (cx + r, cy), 1)
    pygame.draw.line(screen, (48, 48, 58), (cx, cy - r), (cx, cy + r), 1)

    # Ball position (clamped inside circle)
    max_g = 1.5
    bx = cx + int(lat_g / max_g * r * 0.88)
    by = cy - int(lon_g / max_g * r * 0.88)
    dist = math.sqrt((bx - cx) ** 2 + (by - cy) ** 2)
    if dist > r * 0.88:
        s  = r * 0.88 / dist
        bx = cx + int((bx - cx) * s)
        by = cy + int((by - cy) * s)

    # Glow
    glow = pygame.Surface((20, 20), pygame.SRCALPHA)
    pr, pg, pb = theme["needle"]
    pygame.draw.circle(glow, (pr, pg, pb, 80), (10, 10), 9)
    screen.blit(glow, (bx - 10, by - 10))

    pygame.draw.circle(screen, theme["needle"], (bx, by), 4)
    pygame.draw.circle(screen, (255, 255, 255), (bx, by), 2)

    # Outer border
    pygame.draw.circle(screen, (55, 55, 65), (cx, cy), r, 1)

    # "G" label
    f = _f(9)
    s = f.render("G", True, (80, 80, 92))
    screen.blit(s, (cx - s.get_width() // 2, cy + r + 2))


# ══════════════════════════════════════════════════════════════
#  ECO MODE
#  Centred speed gauge with an ECO ZONE arc painted on its face.
#  Below: Tesla-style power/regen bar.
#  Instant MPG large digital.  Eco score arc.  Range block.
# ══════════════════════════════════════════════════════════════

def draw_eco_panel(screen, data, theme, frame_count):
    speed    = data["speed"]
    throttle = data["throttle"]
    brake    = data["brake"]
    econ     = data["economy"]

    r  = 100
    cx = _PCX
    cy = _BODY_Y + r + 22

    # ── Speed gauge with eco-zone arc overlay ────────────────
    draw_analog_gauge(
        screen, speed, 0, config.MAX_SPEED,
        cx, cy, r,
        label="SPEED", unit="mph",
        theme=theme,
        major_step=20, minor_step=10,
        show_center_text=True,
    )

    # Eco zone highlight arc (25–65 mph ideal range) drawn over the gauge
    _draw_eco_zone_arc(screen, cx, cy, r - 5, 25, 65,
                       config.MAX_SPEED, theme)

    # ── Power / regen bar ─────────────────────────────────────
    bar_x = _PX + 20
    bar_w = _PW - 40
    bar_h = 18
    # Position below the gauge bezel
    gauge_bot = cy + r + 26
    pwr_y     = gauge_bot + 4

    _draw_power_regen_bar(screen, throttle, brake, bar_x, pwr_y, bar_w, bar_h)

    # ── Eco stat blocks (below power bar) ────────────────────
    blk_y = pwr_y + bar_h + 20
    blk_h = 44
    blk_w = (_PW - 50) // 3
    avail = _RAD_Y - blk_y - 8
    if avail < blk_h:
        blk_h = max(30, avail)

    blocks = [
        ("INSTANT",  f"{econ['mpg_instant']:.0f}",  "MPG"),
        ("TRIP AVG", f"{econ['mpg_trip']:.1f}",       "MPG"),
        ("RANGE",    f"{int(econ['range_mi'])}",      "mi"),
    ]
    for i, (lbl, val, unit) in enumerate(blocks):
        bx = _PX + 20 + i * (blk_w + 5)
        draw_digital_block(screen, lbl, val, unit, bx, blk_y, blk_w, blk_h, theme)

    # ── Eco score arc gauge (small, lower-right area) ─────────
    score_cx = _PX + _PW - 52
    score_cy = blk_y + blk_h // 2
    _draw_eco_score(screen, econ["eco_score"], score_cx, score_cy, 28, theme)


def _draw_eco_zone_arc(screen, cx, cy, r, lo_mph, hi_mph, max_mph, theme):
    """Translucent green arc painted over the speed gauge showing the eco band."""
    a_lo = _angle_rad(lo_mph,  0, max_mph, 220, 260)
    a_hi = _angle_rad(hi_mph,  0, max_mph, 220, 260)
    rect = (cx - r, cy - r, r * 2, r * 2)

    # Draw as a thick translucent arc using a surface
    arc_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    arc_r    = r - 3
    ar       = (1, 1, arc_r * 2, arc_r * 2)
    pygame.draw.arc(arc_surf, (*theme["accent"], 45), ar, a_hi, a_lo, 7)
    screen.blit(arc_surf, (cx - r - 1, cy - r - 1))

    # Thin bright border lines at the zone edges
    for a, lbl in ((a_lo, f"{int(lo_mph)}"), (a_hi, f"{int(hi_mph)}")):
        ox, oy = _polar(cx, cy, r + 2, a)
        ix, iy = _polar(cx, cy, r - 10, a)
        pygame.draw.line(screen, theme["accent"],
                         (int(ox), int(oy)), (int(ix), int(iy)), 2)


def _draw_power_regen_bar(screen, throttle, brake, x, y, w, h):
    """
    Horizontal centred bar.
    Right half (orange→red)  = engine power demand (throttle).
    Left  half (green)        = regen / engine braking (brake).
    """
    cx = x + w // 2

    # Background
    pygame.draw.rect(screen, (28, 28, 32), (x, y, w, h), border_radius=4)

    # Right: power demand
    pw = int((throttle / 100.0) * (w // 2))
    if pw > 2:
        intensity = throttle / 100.0
        r_ch = int(180 + intensity * 75)
        g_ch = int(120 - intensity * 100)
        pygame.draw.rect(screen, (r_ch, max(0, g_ch), 10),
                         (cx, y + 1, pw, h - 2), border_radius=4)

    # Left: regen / braking
    bw = int((brake / 100.0) * (w // 2))
    if bw > 2:
        pygame.draw.rect(screen, (35, 185, 65),
                         (cx - bw, y + 1, bw, h - 2), border_radius=4)

    # Centre line
    pygame.draw.rect(screen, (180, 180, 190), (cx - 1, y - 2, 2, h + 4))

    # Border
    pygame.draw.rect(screen, (55, 55, 65), (x, y, w, h), 1, border_radius=4)

    # Labels
    f = _f(11)
    s_r = f.render("REGEN", True, (50, 170, 60))
    s_p = f.render("POWER", True, (190, 90, 20))
    screen.blit(s_r, (x + 4, y + (h - s_r.get_height()) // 2))
    screen.blit(s_p, (x + w - s_p.get_width() - 4, y + (h - s_p.get_height()) // 2))


def _draw_eco_score(screen, score, cx, cy, r, theme):
    """Small arc gauge showing eco score 0-100. Clockwise, full = perfect."""
    cx, cy = int(cx), int(cy)

    # Background circle
    pygame.draw.circle(screen, (22, 22, 26), (cx, cy), r + 4)
    pygame.draw.circle(screen, (40, 40, 46), (cx, cy), r + 4, 1)

    # Arc track
    rect = (cx - r, cy - r, r * 2, r * 2)
    pygame.draw.arc(screen, (40, 40, 44), rect,
                    math.radians(-40), math.radians(220), 5)

    # Filled arc
    a_val = _angle_rad(score, 0, 100, 220, 260)
    if score > 0:
        col = theme["arc"] if score >= 60 else theme["arc_warn"] if score >= 35 else theme["arc_danger"]
        pygame.draw.arc(screen, col, rect, a_val, math.radians(220), 5)

    # Score text
    f_n = _f(14, bold=True)
    f_l = _f(9)
    ns  = f_n.render(str(int(score)), True, theme["text"])
    ls  = f_l.render("ECO", True, theme["sub"])
    screen.blit(ns, (cx - ns.get_width() // 2, cy - ns.get_height() // 2 - 1))
    screen.blit(ls, (cx - ls.get_width() // 2, cy + 9))


# ══════════════════════════════════════════════════════════════
#  NORMAL MODE
#  Focused on calm daily driving guidance.
#  Speed gauge (centred).
#  Drive-style meter: GENTLE ▶ SPIRITED horizontal bar with needle.
#  Trip computer blocks.
#  Engine health LEDs (colour-coded status, no raw numbers).
# ══════════════════════════════════════════════════════════════

def draw_normal_panel(screen, data, theme, frame_count):
    speed        = data["speed"]
    drive_style  = data["drive_style"]    # 0=gentle, 100=spirited
    trip         = data["trip"]
    engine       = data["engine"]
    smooth       = trip["smooth_score"]

    r  = 100
    cx = _PCX
    cy = _BODY_Y + r + 22

    # ── Speed gauge ───────────────────────────────────────────
    draw_analog_gauge(
        screen, speed, 0, config.MAX_SPEED,
        cx, cy, r,
        label="SPEED", unit="mph",
        theme=theme,
        major_step=20, minor_step=10,
        show_center_text=True,
    )

    # ── Drive style meter ─────────────────────────────────────
    gauge_bot = cy + r + 26
    ds_x  = _PX + 22
    ds_w  = _PW - 44
    ds_y  = gauge_bot + 4
    ds_h  = 16
    _draw_style_meter(screen, drive_style, ds_x, ds_y, ds_w, ds_h, theme)

    # ── Smooth score arc (small, inside face) ─────────────────
    sm_cx = cx
    sm_cy = cy + 30
    _draw_smooth_arc(screen, smooth, sm_cx, sm_cy, 26, theme)

    # ── Trip computer blocks ───────────────────────────────────
    blk_y = ds_y + ds_h + 22
    blk_h = 40
    avail = _RAD_Y - blk_y - 52   # leave room for LED row
    if avail < blk_h:
        blk_h = max(28, avail)

    blk_w = (_PW - 50) // 3
    blocks = [
        ("DISTANCE", f"{trip['distance']:.1f}", "mi"),
        ("TRIP TIME", _fmt_time(trip["time_min"]),  ""),
        ("AVG SPEED", f"{trip['avg_speed']:.0f}",  "mph"),
    ]
    for i, (lbl, val, unit) in enumerate(blocks):
        bx = _PX + 22 + i * (blk_w + 4)
        draw_digital_block(screen, lbl, val, unit, bx, blk_y, blk_w, blk_h, theme)

    # ── Engine health LEDs ─────────────────────────────────────
    led_y    = _RAD_Y - 30
    led_items = _engine_health_leds(engine)
    spacing  = (_PW - 20) // max(1, len(led_items))
    for i, (lbl, status) in enumerate(led_items):
        lx = _PX + 14 + i * spacing
        draw_led(screen, lx, led_y, lbl, status, theme)


def _draw_style_meter(screen, score, x, y, w, h, theme):
    """
    Horizontal zoned bar (GENTLE left → SPIRITED right).
    A white needle marks the current driving style.
    """
    # Zone colours painted left-to-right
    zones = [
        (0.00, 0.35, (28, 110, 40)),   # green  – gentle
        (0.35, 0.65, (130, 85,  20)),  # amber  – normal
        (0.65, 1.00, (150, 30,  22)),  # red    – spirited
    ]
    for lo, hi, col in zones:
        zx = x + int(lo * w)
        zw = int((hi - lo) * w)
        pygame.draw.rect(screen, col, (zx, y, zw, h))

    # Needle
    nx = x + int(max(0, min(1, score / 100.0)) * w)
    pygame.draw.rect(screen, (240, 240, 245), (nx - 1, y - 4, 2, h + 8))

    # Border
    pygame.draw.rect(screen, (55, 55, 65), (x, y, w, h), 1, border_radius=2)

    # Labels
    f    = _f(11)
    f_st = _f(11, bold=True)
    s_g  = f.render("GENTLE",   True, (60, 180, 60))
    s_s  = f.render("SPIRITED", True, (200, 55, 45))
    screen.blit(s_g, (x,                          y - 16))
    screen.blit(s_s, (x + w - s_s.get_width(),    y - 16))

    # Style label centred above needle
    if score < 33:
        style_lbl, style_col = "SMOOTH DRIVING",  (60, 200, 70)
    elif score < 66:
        style_lbl, style_col = "NORMAL DRIVING",  (200, 180, 40)
    else:
        style_lbl, style_col = "SPIRITED DRIVING",(215, 60, 45)
    sl_s = f_st.render(style_lbl, True, style_col)
    screen.blit(sl_s, (x + w // 2 - sl_s.get_width() // 2, y - 16))


def _draw_smooth_arc(screen, score, cx, cy, r, theme):
    """
    Tiny arc gauge showing smooth-driving score inside the speed gauge face.
    This overlays the lower-center dead zone of the arc (where ticks don't reach).
    """
    cx, cy = int(cx), int(cy)
    rect = (cx - r, cy - r, r * 2, r * 2)
    pygame.draw.arc(screen, (35, 35, 40), rect,
                    math.radians(-40), math.radians(220), 4)
    a_val = _angle_rad(score, 0, 100, 220, 260)
    if score > 0:
        col = (50, 200, 70) if score >= 70 else (200, 180, 30) if score >= 40 else (210, 50, 40)
        pygame.draw.arc(screen, col, rect, a_val, math.radians(220), 4)
    f = _f(9)
    s = f.render(f"{int(score)}", True, theme["sub"])
    screen.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))


def _engine_health_leds(engine):
    """Return list of (label, status) pairs based on engine stats."""
    items = []

    # Coolant
    ct = engine["coolant_temp"]
    items.append(("COOLANT", "ok" if ct < 215 else "warn" if ct < 240 else "alert"))

    # Oil
    ot = engine["oil_temp"]
    items.append(("OIL", "ok" if ot < 230 else "warn" if ot < 255 else "alert"))

    # Battery
    bv = engine["battery_v"]
    items.append(("BATTERY", "ok" if bv >= 13.5 else "warn" if bv >= 12.0 else "alert"))

    return items


def _fmt_time(mins):
    m = int(mins)
    h = m // 60
    m = m % 60
    return f"{h}:{m:02d}" if h > 0 else f"{m}m"
