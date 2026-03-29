# ui/gauges.py
# Analog gauge renderer — the visual core of the dashboard.

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


# ── Gauge sub-components ──────────────────────────────────────

def _draw_bezel(screen, cx, cy, r):
    pygame.draw.circle(screen, (42, 42, 47), (cx, cy), r + 22)
    pygame.draw.circle(screen, (80, 80, 88), (cx, cy), r + 18)
    pygame.draw.circle(screen, (52, 52, 58), (cx, cy), r + 13)
    pygame.draw.circle(screen, (30, 30, 34), (cx, cy), r +  9)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), r +  4)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), r)


def _draw_ticks(screen, cx, cy, r, min_val, max_val,
                major_step, minor_step, start_deg, sweep_deg,
                scale_div=1, redline=None, accent_color=None):
    fnt = _f(max(10, min(13, r // 10)))

    if minor_step:
        v = min_val
        while v <= max_val + 1e-6:
            a  = _angle_rad(v, min_val, max_val, start_deg, sweep_deg)
            ox, oy = _polar(cx, cy, r,     a)
            ix, iy = _polar(cx, cy, r - 7, a)
            col = (145, 25, 25) if (redline and v >= redline) else config.TICK_MINOR
            pygame.draw.line(screen, col,
                             (int(ox), int(oy)), (int(ix), int(iy)), 1)
            v += minor_step

    if major_step:
        v = min_val
        while v <= max_val + 1e-6:
            a  = _angle_rad(v, min_val, max_val, start_deg, sweep_deg)
            ox, oy = _polar(cx, cy, r,      a)
            ix, iy = _polar(cx, cy, r - 15, a)
            col = (accent_color or config.TICK_MAJOR) if (redline and v >= redline) else config.TICK_MAJOR
            pygame.draw.line(screen, col,
                             (int(ox), int(oy)), (int(ix), int(iy)), 2)

            num = v / scale_div
            label = str(int(num)) if num == int(num) else f"{num:.1f}"
            nx, ny = _polar(cx, cy, r - 28, a)
            surf = fnt.render(label, True, col)
            screen.blit(surf, (int(nx) - surf.get_width() // 2,
                               int(ny) - surf.get_height() // 2))
            v += major_step


def _draw_needle(screen, cx, cy, angle_rad, tip_r, color):
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    cos_p = math.cos(angle_rad + math.pi / 2)
    sin_p = math.sin(angle_rad + math.pi / 2)

    def pt(fwd, side):
        return (int(cx + fwd * cos_a + side * cos_p),
                int(cy - fwd * sin_a - side * sin_p))

    tip = pt(tip_r, 0)
    rl  = pt(tip_r - 14,  1.2)
    rr  = pt(tip_r - 14, -1.2)
    bl  = pt(0,  4.5)
    br  = pt(0, -4.5)
    cw  = pt(-22, 0)
    cwl = pt(-16,  5)
    cwr = pt(-16, -5)

    pygame.draw.polygon(screen, color, [tip, rl, bl, cwl, cw, cwr, br, rr])
    pygame.draw.line(screen, (255, 255, 255), pt(2, 0), pt(tip_r - 4, 0), 1)


def _draw_center_cap(screen, cx, cy, accent):
    pygame.draw.circle(screen, (55, 55, 62), (cx, cy), 13)
    pygame.draw.circle(screen, config.GAUGE_FACE, (cx, cy), 10)
    pygame.draw.circle(screen, accent,           (cx, cy),  6)
    pygame.draw.circle(screen, (220, 220, 225),  (cx, cy),  2)


# ── Main analog gauge ─────────────────────────────────────────

def draw_analog_gauge(screen, value, min_val, max_val, cx, cy, radius,
                      label, unit, theme,
                      start_deg=220, sweep_deg=260,
                      major_step=None, minor_step=None,
                      scale_div=1, redline=None,
                      show_center_text=True):
    """
    Full analog gauge: bezel, ticks, arc, needle, optional center text.

    show_center_text=False  lets the caller draw custom content inside the face.
    """
    cx, cy = int(cx), int(cy)
    accent = theme["accent"]

    _draw_bezel(screen, cx, cy, radius)

    track_r = radius - 5
    rect    = (cx - track_r, cy - track_r, track_r * 2, track_r * 2)
    a_start = math.radians(start_deg)
    a_end   = math.radians(start_deg - sweep_deg)

    # Track groove
    pygame.draw.arc(screen, (38, 38, 42), rect, a_end, a_start, 6)

    # Redline zone (always visible, dim red)
    if redline is not None and redline < max_val:
        a_rl = _angle_rad(redline, min_val, max_val, start_deg, sweep_deg)
        pygame.draw.arc(screen, (90, 15, 15), rect, a_end, a_rl, 6)

    # Active fill arc
    a_val = _angle_rad(value, min_val, max_val, start_deg, sweep_deg)
    if value > min_val:
        ratio = (value - min_val) / (max_val - min_val)
        if redline and value >= redline:
            arc_color = theme["arc_danger"]
        elif ratio > 0.78:
            arc_color = theme["arc_warn"]
        else:
            arc_color = theme["arc"]
        pygame.draw.arc(screen, arc_color, rect, a_val, a_start, 6)

    _draw_ticks(screen, cx, cy, radius, min_val, max_val,
                major_step, minor_step, start_deg, sweep_deg,
                scale_div=scale_div, redline=redline, accent_color=accent)

    _draw_needle(screen, cx, cy, a_val, track_r - 8, theme["needle"])
    _draw_center_cap(screen, cx, cy, theme["needle"])

    if show_center_text:
        f_lbl  = _f(max(10, radius // 11))
        f_val  = _f(max(18, radius // 5), bold=True)
        f_unit = _f(max(10, radius // 11))

        lbl_s  = f_lbl.render(label,          True, theme["sub"])
        val_s  = f_val.render(str(int(value)), True, theme["text"])
        unit_s = f_unit.render(unit,           True, theme["sub"])

        screen.blit(lbl_s,  (cx - lbl_s.get_width()  // 2, cy - 34))
        screen.blit(val_s,  (cx - val_s.get_width()   // 2, cy -  8))
        screen.blit(unit_s, (cx - unit_s.get_width()  // 2,
                             cy + val_s.get_height() - 6))


# ── Bar gauge ─────────────────────────────────────────────────

def draw_bar_gauge(screen, value, min_val, max_val, x, y, w, h,
                   label, unit, theme,
                   warn_ratio=0.80, danger_ratio=0.92,
                   show_value=True):
    ratio = max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    if   ratio >= danger_ratio: fill_color = theme["arc_danger"]
    elif ratio >= warn_ratio:   fill_color = theme["arc_warn"]
    else:                       fill_color = theme["arc"]

    f_lbl = _f(13)
    f_val = _f(13, bold=True)

    lbl_s = f_lbl.render(label, True, theme["sub"])
    screen.blit(lbl_s, (x, y - 18))
    if show_value:
        val_s = f_val.render(f"{value:.1f} {unit}", True, theme["text"])
        screen.blit(val_s, (x + w - val_s.get_width(), y - 18))

    pygame.draw.rect(screen, (35, 35, 40), (x, y, w, h), border_radius=3)
    fw = int(ratio * w)
    if fw > 4:
        pygame.draw.rect(screen, fill_color, (x, y, fw, h), border_radius=3)
    pygame.draw.rect(screen, theme["accent"], (x, y, w, h), 1, border_radius=3)


# ── Digital block ─────────────────────────────────────────────

def draw_digital_block(screen, label, value_str, unit, x, y, w, h, theme):
    pygame.draw.rect(screen, (22, 22, 26), (x, y, w, h), border_radius=5)
    pygame.draw.rect(screen, theme["accent"], (x, y, w, h), 1, border_radius=5)

    f_lbl = _f(11)
    f_val = _f(20, bold=True)
    f_unt = _f(11)

    lbl_s = f_lbl.render(label,     True, theme["sub"])
    val_s = f_val.render(value_str, True, theme["text"])
    unt_s = f_unt.render(unit,      True, theme["sub"])

    total_h = lbl_s.get_height() + 2 + val_s.get_height() + 1 + unt_s.get_height()
    top = y + max(2, (h - total_h) // 2)

    screen.blit(lbl_s, (x + (w - lbl_s.get_width()) // 2, top))
    screen.blit(val_s, (x + (w - val_s.get_width()) // 2,
                        top + lbl_s.get_height() + 2))
    screen.blit(unt_s, (x + (w - unt_s.get_width()) // 2,
                        top + lbl_s.get_height() + 2 + val_s.get_height() + 1))


# ── LED status indicator ──────────────────────────────────────

def draw_led(screen, x, y, label, status, theme):
    """
    Simple LED dot + label.  status: 'ok', 'warn', 'alert'
    """
    colors = {"ok": (50, 200, 70), "warn": (230, 160, 20), "alert": (220, 40, 40)}
    col = colors.get(status, (100, 100, 110))
    # Glow halo
    halo_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(halo_surf, (*col, 55), (10, 10), 9)
    screen.blit(halo_surf, (x - 9, y - 9))
    # Main dot
    pygame.draw.circle(screen, col, (x, y), 5)
    pygame.draw.circle(screen, (200, 200, 200), (x, y), 2)
    # Label
    f = _f(11)
    s = f.render(label, True, theme["sub"])
    screen.blit(s, (x + 10, y - s.get_height() // 2))
