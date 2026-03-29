# ui/radar_alert.py
# Radar detector panel — bottom strip of the right panel.

import pygame
import math
import config
from ui.gauges import _f


def draw_radar_panel(screen, radar_data, theme, frame_count):
    x    = config.MAP_PANEL_WIDTH + 10
    y    = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT + 6
    pw   = config.GAUGE_PANEL_WIDTH - 20
    ph   = config.RADAR_PANEL_HEIGHT - 12

    accent = theme["accent"]

    # ── Panel background ─────────────────────────────────────
    if radar_data["alert"]:
        pulse   = (math.sin(frame_count * 0.18) + 1) / 2
        r_ch    = int(70 + pulse * 100)
        bg_col  = (r_ch, 8, 8)
        brd_col = (200, 30, 30)
    else:
        pulse   = (math.sin(frame_count * 0.05) + 1) / 2
        g_ch    = int(14 + pulse * 18)
        bg_col  = (6, g_ch, 6)
        brd_col = theme["divider"]

    pygame.draw.rect(screen, bg_col, (x, y, pw, ph), border_radius=7)
    pygame.draw.rect(screen, brd_col, (x, y, pw, ph), 2, border_radius=7)

    # ── Title bar ────────────────────────────────────────────
    f_title = _f(12)
    title_s = f_title.render("RADAR DETECTOR", True, accent)
    screen.blit(title_s, (x + 10, y + 7))

    if radar_data["alert"]:
        # ── Band label ────────────────────────────────────────
        f_band = _f(32, bold=True)
        band_s = f_band.render(f"\u26a0  {radar_data['band']}", True, (255, 255, 255))
        screen.blit(band_s, (x + 10, y + 24))

        # ── Signal strength bars ──────────────────────────────
        str_val = radar_data["strength"]
        bx, by0 = x + 10, y + 68
        bw, bh_max, gap = 20, 36, 9
        for i in range(5):
            bh  = int(bh_max * (0.35 + i * 0.165))
            top = by0 + (bh_max - bh)
            col = (220, 220, 220) if i < str_val else (70, 25, 25)
            pygame.draw.rect(screen, col,
                             (bx + i * (bw + gap), top, bw, bh),
                             border_radius=2)

        f_sig = _f(12)
        sig_s = f_sig.render(f"SIGNAL  {str_val}/5", True, (200, 200, 200))
        screen.blit(sig_s, (x + 10, y + ph - 20))

    else:
        # ── All clear ────────────────────────────────────────
        f_clr = _f(26, bold=True)
        f_sub = _f(12)
        clr_s = f_clr.render("\u2713  ALL CLEAR", True, (80, 220, 90))
        sub_s = f_sub.render("No signals detected", True, (100, 130, 100))
        screen.blit(clr_s, (x + 10, y + 26))
        screen.blit(sub_s, (x + 10, y + 62))
