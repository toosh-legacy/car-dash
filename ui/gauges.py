# ui/gauges.py
# Analog gauge renderer.
# Visual language: classic VDO / Porsche — black face, white markings, amber arc.

import pygame
import math
import config

# ── Font cache ────────────────────────────────────────────────
_font_cache = {}

def _f(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
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
    ratio = max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
    return math.radians(start_deg - ratio * sweep_deg)


def _polar(cx, cy, r, angle_rad):
    return (cx + r * math.cos(angle_rad),
            cy - r * math.sin(angle_rad))


# ── Bezel — warm-toned chrome ring ───────────────────────────

def _draw_bezel(screen, cx, cy, r):
    """
    Layered circles give the illusion of a machined aluminium bezel.
    Warm highlights lean toward the amber-black palette.
    """
    pygame.draw.circle(screen, (38, 36, 30),  (cx, cy), r + 22)   # outer shadow
    pygame.draw.circle(screen, (72, 68, 54),  (cx, cy), r + 18)   # warm highlight
    pygame.draw.circle(screen, (50, 48, 38),  (cx, cy), r + 14)   # mid ring
    pygame.draw.circle(screen, (28, 27, 20),  (cx, cy), r +  9)   # inner ring
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), r +  4)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), r)


# ── Tick marks + numbers ──────────────────────────────────────

def _draw_ticks(screen, cx, cy, r, min_val, max_val,
                major_step, minor_step, start_deg, sweep_deg,
                scale_div=1, redline=None, danger_color=None):
    fnt = _f(max(10, min(13, r // 10)))

    # Minor ticks
    if minor_step:
        v = min_val
        while v <= max_val + 1e-6:
            a  = _angle_rad(v, min_val, max_val, start_deg, sweep_deg)
            ox, oy = _polar(cx, cy, r,     a)
            ix, iy = _polar(cx, cy, r - 7, a)
            if redline and v >= redline:
                col = (100, 42, 5)
            else:
                col = config.TICK_MINOR
            pygame.draw.line(screen, col,
                             (int(ox), int(oy)), (int(ix), int(iy)), 1)
            v += minor_step

    # Major ticks + numbers
    if major_step:
        v = min_val
        while v <= max_val + 1e-6:
            a  = _angle_rad(v, min_val, max_val, start_deg, sweep_deg)
            ox, oy = _polar(cx, cy, r,      a)
            ix, iy = _polar(cx, cy, r - 16, a)

            if redline and v >= redline:
                col = danger_color or (180, 80, 10)
            else:
                col = config.TICK_MAJOR

            pygame.draw.line(screen, col,
                             (int(ox), int(oy)), (int(ix), int(iy)), 2)

            # Number
            num   = v / scale_div
            label = str(int(num)) if num == int(num) else f"{num:.1f}"
            nx, ny = _polar(cx, cy, r - 30, a)
            surf   = fnt.render(label, True, col)
            screen.blit(surf, (int(nx) - surf.get_width() // 2,
                               int(ny) - surf.get_height() // 2))
            v += major_step


# ── Needle ────────────────────────────────────────────────────

def _draw_needle(screen, cx, cy, angle_rad, tip_r, color):
    """Tapered white needle with a small counterweight stub."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    cos_p = math.cos(angle_rad + math.pi / 2)
    sin_p = math.sin(angle_rad + math.pi / 2)

    def pt(fwd, side):
        return (int(cx + fwd * cos_a + side * cos_p),
                int(cy - fwd * sin_a - side * sin_p))

    tip  = pt(tip_r,  0)
    rl   = pt(tip_r - 14,  1.0)
    rr   = pt(tip_r - 14, -1.0)
    bl   = pt(0,  4.0)
    br   = pt(0, -4.0)
    cwl  = pt(-16,  5)
    cwr  = pt(-16, -5)
    cw   = pt(-22, 0)

    pygame.draw.polygon(screen, color, [tip, rl, bl, cwl, cw, cwr, br, rr])
    # Centre highlight line
    pygame.draw.line(screen, (255, 255, 255), pt(2, 0), pt(tip_r - 5, 0), 1)


def _draw_center_cap(screen, cx, cy, accent):
    """Pivot cap — classic small chrome button look."""
    pygame.draw.circle(screen, (52, 50, 40),  (cx, cy), 12)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), 9)
    pygame.draw.circle(screen, accent,         (cx, cy), 5)
    pygame.draw.circle(screen, (215, 215, 220),(cx, cy), 2)


# ── Main analog gauge ─────────────────────────────────────────

def draw_analog_gauge(screen, value, min_val, max_val, cx, cy, radius,
                      label, unit, theme,
                      start_deg=220, sweep_deg=260,
                      major_step=None, minor_step=None,
                      scale_div=1, redline=None,
                      show_center_text=True):
    cx, cy = int(cx), int(cy)
    accent = theme["accent"]

    _draw_bezel(screen, cx, cy, radius)

    track_r = radius - 5
    rect    = (cx - track_r, cy - track_r, track_r * 2, track_r * 2)
    a_start = math.radians(start_deg)
    a_end   = math.radians(start_deg - sweep_deg)

    # Track groove
    pygame.draw.arc(screen, (32, 30, 22), rect, a_end, a_start, 5)

    # Redline zone (always painted, dim amber-orange)
    if redline is not None and redline < max_val:
        a_rl = _angle_rad(redline, min_val, max_val, start_deg, sweep_deg)
        pygame.draw.arc(screen, (88, 36, 5), rect, a_end, a_rl, 5)

    # Active arc
    a_val = _angle_rad(value, min_val, max_val, start_deg, sweep_deg)
    if value > min_val:
        ratio = (value - min_val) / (max_val - min_val)
        if redline and value >= redline:
            arc_color = theme["arc_danger"]
        elif ratio > 0.78:
            arc_color = theme["arc_warn"]
        else:
            arc_color = theme["arc"]
        pygame.draw.arc(screen, arc_color, rect, a_val, a_start, 5)

    _draw_ticks(screen, cx, cy, radius, min_val, max_val,
                major_step, minor_step, start_deg, sweep_deg,
                scale_div=scale_div, redline=redline,
                danger_color=theme["arc_danger"])

    _draw_needle(screen, cx, cy, a_val, track_r - 8, theme["needle"])
    _draw_center_cap(screen, cx, cy, theme["needle"])

    if show_center_text:
        f_lbl  = _f(max(10, radius // 11))
        f_val  = _f(max(18, radius // 5), bold=True)
        f_unit = _f(max(10, radius // 11))

        lbl_s  = f_lbl.render(label,           True, theme["sub"])
        val_s  = f_val.render(str(int(value)),  True, theme["text"])
        unit_s = f_unit.render(unit,            True, theme["sub"])

        screen.blit(lbl_s,  (cx - lbl_s.get_width()  // 2, cy - 34))
        screen.blit(val_s,  (cx - val_s.get_width()   // 2, cy -  8))
        screen.blit(unit_s, (cx - unit_s.get_width()  // 2,
                             cy + val_s.get_height() - 6))


# ── Mini arc gauge (for secondary instrument row) ─────────────

def draw_mini_arc(screen, value, min_val, max_val, cx, cy, r,
                  label, unit, theme, redline=None):
    """
    Small analog gauge for the secondary health-metric row.
    Thin warm bezel, minimal ticks, value text inside face.
    """
    cx, cy = int(cx), int(cy)

    # Thin warm bezel
    pygame.draw.circle(screen, (35, 33, 26), (cx, cy), r + 7)
    pygame.draw.circle(screen, (62, 58, 44), (cx, cy), r + 5)  # warm highlight
    pygame.draw.circle(screen, (24, 23, 17), (cx, cy), r + 3)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), r)

    # Arc track
    rect    = (cx - r + 1, cy - r + 1, (r - 1) * 2, (r - 1) * 2)
    a_start = math.radians(220)
    a_end   = math.radians(-40)
    pygame.draw.arc(screen, (32, 30, 20), rect, a_end, a_start, 3)

    # Redline zone
    if redline and redline < max_val:
        a_rl = _angle_rad(redline, min_val, max_val, 220, 260)
        pygame.draw.arc(screen, (80, 32, 4), rect, a_end, a_rl, 3)

    # Active fill
    a_val = _angle_rad(value, min_val, max_val, 220, 260)
    if value > min_val:
        if redline and value >= redline:
            col = theme["arc_danger"]
        elif (value - min_val) / (max_val - min_val) > 0.80:
            col = theme["arc_warn"]
        else:
            col = theme["arc"]
        pygame.draw.arc(screen, col, rect, a_val, a_start, 3)

    # Needle — simple thin line
    nx, ny = _polar(cx, cy, r - 3, a_val)
    pygame.draw.line(screen, theme["needle"], (cx, cy), (int(nx), int(ny)), 1)
    pygame.draw.circle(screen, theme["needle"], (cx, cy), 2)

    # Value inside face
    f_val = _f(9, bold=True)
    if "°" in unit or unit == "°F":
        v_str = f"{value:.0f}°"
    elif unit == "V":
        v_str = f"{value:.1f}"
    else:
        v_str = f"{value:.0f}"
    v_s = f_val.render(v_str, True, theme["text"])
    screen.blit(v_s, (cx - v_s.get_width() // 2, cy - v_s.get_height() // 2 - 1))

    # Label below gauge
    f_lbl = _f(9)
    l_s   = f_lbl.render(label, True, theme["sub"])
    screen.blit(l_s, (cx - l_s.get_width() // 2, cy + r + 4))


# ── Horizontal bar gauge ──────────────────────────────────────

def draw_bar_gauge(screen, value, min_val, max_val, x, y, w, h,
                   label, unit, theme,
                   warn_ratio=0.80, danger_ratio=0.92,
                   show_value=True):
    ratio = max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
    if   ratio >= danger_ratio: fill_color = theme["arc_danger"]
    elif ratio >= warn_ratio:   fill_color = theme["arc_warn"]
    else:                       fill_color = theme["arc"]

    f_lbl = _f(12)
    f_val = _f(12, bold=True)

    lbl_s = f_lbl.render(label, True, theme["sub"])
    screen.blit(lbl_s, (x, y - 16))
    if show_value:
        val_s = f_val.render(f"{value:.1f} {unit}", True, theme["text"])
        screen.blit(val_s, (x + w - val_s.get_width(), y - 16))

    pygame.draw.rect(screen, (30, 28, 18), (x, y, w, h), border_radius=3)
    fw = int(ratio * w)
    if fw > 4:
        pygame.draw.rect(screen, fill_color, (x, y, fw, h), border_radius=3)
    pygame.draw.rect(screen, (55, 50, 32), (x, y, w, h), 1, border_radius=3)


# ── Digital block ─────────────────────────────────────────────

def draw_digital_block(screen, label, value_str, unit, x, y, w, h, theme):
    pygame.draw.rect(screen, (18, 17, 10), (x, y, w, h), border_radius=5)
    pygame.draw.rect(screen, (55, 50, 30), (x, y, w, h), 1, border_radius=5)

    f_lbl = _f(10)
    f_val = _f(19, bold=True)
    f_unt = _f(10)

    lbl_s = f_lbl.render(label,     True, theme["sub"])
    val_s = f_val.render(value_str, True, theme["text"])
    unt_s = f_unt.render(unit,      True, theme["sub"])

    total_h = lbl_s.get_height() + 2 + val_s.get_height() + 1 + unt_s.get_height()
    top     = y + max(2, (h - total_h) // 2)

    screen.blit(lbl_s, (x + (w - lbl_s.get_width()) // 2, top))
    screen.blit(val_s, (x + (w - val_s.get_width()) // 2,
                        top + lbl_s.get_height() + 2))
    screen.blit(unt_s, (x + (w - unt_s.get_width()) // 2,
                        top + lbl_s.get_height() + 2 + val_s.get_height() + 1))


# ── LED status dot ────────────────────────────────────────────

def draw_led(screen, x, y, label, status, theme):
    colors = {"ok": (48, 195, 68), "warn": (220, 155, 18), "alert": (210, 42, 38)}
    col    = colors.get(status, (90, 88, 65))
    halo   = pygame.Surface((18, 18), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*col, 55), (9, 9), 8)
    screen.blit(halo, (x - 9, y - 9))
    pygame.draw.circle(screen, col, (x, y), 5)
    pygame.draw.circle(screen, (205, 205, 210), (x, y), 2)
    f = _f(10)
    s = f.render(label, True, theme["sub"])
    screen.blit(s, (x + 9, y - s.get_height() // 2))
