# ui/gauges.py
# Analog gauge renderer — the visual core of the dashboard.
# Draws proper gauge faces with bezels, tick marks, needles, and arcs.

import pygame
import math
import config

# ── Font cache (avoid re-creating fonts every frame) ──────────
_font_cache = {}

def _f(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        # Try sporty condensed fonts, fall back to consolas
        for name in ("bahnschrift", "arial narrow", "verdana", "consolas"):
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    _font_cache[key] = f
                    break
            except Exception:
                pass
        else:
            _font_cache[key] = pygame.font.Font(None, size)
    return _font_cache[key]


# ── Geometry helpers ──────────────────────────────────────────

def _angle_rad(value, min_val, max_val, start_deg, sweep_deg):
    """Map a value to an angle in radians. CW sweep (value increases CW)."""
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0.0, min(1.0, ratio))
    return math.radians(start_deg - ratio * sweep_deg)


def _polar(cx, cy, r, angle_rad):
    """Point on a circle from center, at angle (pygame Y-flipped)."""
    return (cx + r * math.cos(angle_rad),
            cy - r * math.sin(angle_rad))


# ── Gauge sub-components ──────────────────────────────────────

def _draw_bezel(screen, cx, cy, r):
    """Layered metallic ring around the gauge face."""
    pygame.draw.circle(screen, (42, 42, 47), (cx, cy), r + 22)
    pygame.draw.circle(screen, (78, 78, 86), (cx, cy), r + 18)
    pygame.draw.circle(screen, (55, 55, 62), (cx, cy), r + 14)
    pygame.draw.circle(screen, (32, 32, 36), (cx, cy), r +  9)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), r +  4)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), r)


def _draw_ticks(screen, cx, cy, r, min_val, max_val,
                major_step, minor_step, start_deg, sweep_deg,
                scale_div=1, redline=None, accent_color=None):
    """Major + minor tick marks with number labels on major ticks."""
    fnt = _f(max(10, min(13, r // 10)))

    # Minor ticks
    if minor_step:
        v = min_val
        while v <= max_val + 1e-6:
            a = _angle_rad(v, min_val, max_val, start_deg, sweep_deg)
            ox, oy = _polar(cx, cy, r,     a)
            ix, iy = _polar(cx, cy, r - 7, a)
            color = config.TICK_MINOR
            if redline and v >= redline:
                color = (160, 40, 40)
            pygame.draw.line(screen, color,
                             (int(ox), int(oy)), (int(ix), int(iy)), 1)
            v += minor_step

    # Major ticks + numbers
    if major_step:
        v = min_val
        while v <= max_val + 1e-6:
            a = _angle_rad(v, min_val, max_val, start_deg, sweep_deg)
            ox, oy = _polar(cx, cy, r,      a)
            ix, iy = _polar(cx, cy, r - 15, a)

            color = config.TICK_MAJOR
            if redline and v >= redline and accent_color:
                color = accent_color   # redline ticks glow in theme color

            pygame.draw.line(screen, color,
                             (int(ox), int(oy)), (int(ix), int(iy)), 2)

            # Number label
            num = v / scale_div
            label = str(int(num)) if num == int(num) else f"{num:.1f}"
            nx, ny = _polar(cx, cy, r - 28, a)
            surf = fnt.render(label, True, color)
            screen.blit(surf, (int(nx) - surf.get_width() // 2,
                               int(ny) - surf.get_height() // 2))
            v += major_step


def _draw_needle(screen, cx, cy, angle_rad, tip_r, color):
    """Tapered kite-shaped needle with a short counterweight stub."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    cos_p = math.cos(angle_rad + math.pi / 2)
    sin_p = math.sin(angle_rad + math.pi / 2)

    def pt(fwd, side):
        return (int(cx + fwd * cos_a + side * cos_p),
                int(cy - fwd * sin_a - side * sin_p))

    tip  = pt(tip_r,  0)
    rl   = pt(tip_r - 14,  1.2)
    rr   = pt(tip_r - 14, -1.2)
    bl   = pt(0,  4.5)
    br   = pt(0, -4.5)
    cw   = pt(-22, 0)           # counterweight tip
    cwl  = pt(-16,  5)
    cwr  = pt(-16, -5)

    pygame.draw.polygon(screen, color,
                        [tip, rl, bl, cwl, cw, cwr, br, rr])
    # Bright center stripe for depth
    pygame.draw.line(screen, (255, 255, 255),
                     pt(2, 0), pt(tip_r - 4, 0), 1)


def _draw_center_cap(screen, cx, cy, accent):
    pygame.draw.circle(screen, (55, 55, 62), (cx, cy), 13)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), 10)
    pygame.draw.circle(screen, accent,           (cx, cy),  6)
    pygame.draw.circle(screen, (220, 220, 225),  (cx, cy),  2)


# ── Main gauge drawing function ───────────────────────────────

def draw_analog_gauge(screen, value, min_val, max_val, cx, cy, radius,
                      label, unit, theme,
                      start_deg=220, sweep_deg=260,
                      major_step=None, minor_step=None,
                      scale_div=1, redline=None):
    """
    Draw a full analog gauge with bezel, tick marks, arc, and needle.

    Args:
        value       — current sensor reading
        min_val     — gauge minimum
        max_val     — gauge maximum
        cx, cy      — center of gauge in pixels
        radius      — radius of the tick-mark ring
        label       — text shown inside face (e.g. "RPM")
        unit        — text below value (e.g. "mph")
        theme       — dict from config.THEMES[mode]
        start_deg   — angle at min_val (default 220 = bottom-left)
        sweep_deg   — total degrees swept CW (default 260)
        major_step  — value increment for major ticks
        minor_step  — value increment for minor ticks
        scale_div   — divide tick numbers by this (e.g. 1000 for RPM)
        redline     — value where redline starts (None = no redline)
    """
    cx, cy = int(cx), int(cy)
    accent = theme["accent"]

    # 1. Metallic bezel
    _draw_bezel(screen, cx, cy, radius)

    # 2. Subtle arc channel (track groove)
    track_r = radius - 5
    rect = (cx - track_r, cy - track_r, track_r * 2, track_r * 2)
    a_start = math.radians(start_deg)
    a_end   = math.radians(start_deg - sweep_deg)
    pygame.draw.arc(screen, (38, 38, 42), rect, a_end, a_start, 6)

    # 3. Redline zone (always visible as a dim red strip)
    if redline is not None and redline < max_val:
        a_rl = _angle_rad(redline, min_val, max_val, start_deg, sweep_deg)
        pygame.draw.arc(screen, (90, 15, 15), rect, a_end, a_rl, 6)

    # 4. Active arc (0 → current value)
    a_val = _angle_rad(value, min_val, max_val, start_deg, sweep_deg)
    if value > min_val:
        if redline and value >= redline:
            arc_color = theme["arc_danger"]
        elif (value - min_val) / (max_val - min_val) > 0.78:
            arc_color = theme["arc_warn"]
        else:
            arc_color = theme["arc"]
        pygame.draw.arc(screen, arc_color, rect, a_val, a_start, 6)

    # 5. Tick marks and labels
    _draw_ticks(screen, cx, cy, radius, min_val, max_val,
                major_step, minor_step, start_deg, sweep_deg,
                scale_div=scale_div, redline=redline, accent_color=accent)

    # 6. Needle
    _draw_needle(screen, cx, cy, a_val, track_r - 8, theme["needle"])

    # 7. Center pivot cap
    _draw_center_cap(screen, cx, cy, theme["needle"])

    # 8. Center text (label / value / unit)
    f_lbl  = _f(max(10, radius // 11))
    f_val  = _f(max(18, radius // 5), bold=True)
    f_unit = _f(max(10, radius // 11))

    lbl_s  = f_lbl.render(label,        True, theme["sub"])
    val_s  = f_val.render(str(int(value)), True, theme["text"])
    unit_s = f_unit.render(unit,        True, theme["sub"])

    screen.blit(lbl_s,  (cx - lbl_s.get_width()  // 2, cy - 34))
    screen.blit(val_s,  (cx - val_s.get_width()   // 2, cy -  8))
    screen.blit(unit_s, (cx - unit_s.get_width()  // 2,
                         cy + val_s.get_height() - 6))


# ── Horizontal bar gauge (eco / care panels) ──────────────────

def draw_bar_gauge(screen, value, min_val, max_val, x, y, w, h,
                   label, unit, theme, warn_ratio=0.80, danger_ratio=0.92,
                   show_value=True):
    """Slim horizontal bar with label, value text, and color zones."""
    ratio = max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    if ratio >= danger_ratio:
        fill_color = theme["arc_danger"]
    elif ratio >= warn_ratio:
        fill_color = theme["arc_warn"]
    else:
        fill_color = theme["arc"]

    f_lbl = _f(13)
    f_val = _f(13, bold=True)

    # Label (left) and value (right) on same line above bar
    lbl_s = f_lbl.render(label, True, theme["sub"])
    screen.blit(lbl_s, (x, y - 18))

    if show_value:
        val_s = f_val.render(f"{value:.1f} {unit}", True, theme["text"])
        screen.blit(val_s, (x + w - val_s.get_width(), y - 18))

    # Background track
    pygame.draw.rect(screen, (35, 35, 40), (x, y, w, h), border_radius=3)

    # Fill
    fw = int(ratio * w)
    if fw > 4:
        pygame.draw.rect(screen, fill_color, (x, y, fw, h), border_radius=3)

    # Border
    pygame.draw.rect(screen, theme["accent"], (x, y, w, h), 1, border_radius=3)


# ── Small digital readout block ───────────────────────────────

def draw_digital_block(screen, label, value_str, unit, x, y, w, h, theme):
    """A small inset panel showing a labeled digital value."""
    pygame.draw.rect(screen, (22, 22, 26), (x, y, w, h), border_radius=5)
    pygame.draw.rect(screen, theme["accent"], (x, y, w, h), 1, border_radius=5)

    f_lbl = _f(11)
    f_val = _f(20, bold=True)
    f_unt = _f(11)

    lbl_s = f_lbl.render(label,      True, theme["sub"])
    val_s = f_val.render(value_str,  True, theme["text"])
    unt_s = f_unt.render(unit,       True, theme["sub"])

    # Stack vertically, centered in block
    total_h = lbl_s.get_height() + 2 + val_s.get_height() + 1 + unt_s.get_height()
    top = y + (h - total_h) // 2

    screen.blit(lbl_s, (x + (w - lbl_s.get_width()) // 2, top))
    screen.blit(val_s, (x + (w - val_s.get_width()) // 2, top + lbl_s.get_height() + 2))
    screen.blit(unt_s, (x + (w - unt_s.get_width()) // 2,
                        top + lbl_s.get_height() + 2 + val_s.get_height() + 1))
