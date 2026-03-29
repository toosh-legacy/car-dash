# ui/radar_alert.py
# Compact radar strip — kept intentionally small and unobtrusive.
# Shows status clearly without dominating the display.

import pygame
import math
import config
from ui.gauges import _f


def draw_radar_panel(screen, radar_data, theme, frame_count):
    y  = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT  # 394
    h  = config.RADAR_PANEL_HEIGHT                          # 86
    px = config.MAP_PANEL_WIDTH                             # 768
    pw = config.GAUGE_PANEL_WIDTH                           # 512

    # Subtle strip background
    bg_surf = pygame.Surface((pw, h), pygame.SRCALPHA)
    bg_surf.fill((14, 13, 4, 200))
    screen.blit(bg_surf, (px, y))

    # ── Left: label ───────────────────────────────────────────
    f_lbl  = _f(10)
    f_big  = _f(20, bold=True)
    f_sub  = _f(10)

    lbl1 = f_lbl.render("RADAR", True, (88, 84, 58))
    lbl2 = f_lbl.render("DETECTOR", True, (88, 84, 58))
    lbl_x = px + 16
    screen.blit(lbl1, (lbl_x, y + h // 2 - lbl1.get_height() - 1))
    screen.blit(lbl2, (lbl_x, y + h // 2 + 1))

    # Vertical separator
    sep_x = px + 105
    pygame.draw.line(screen, (40, 38, 22), (sep_x, y + 14), (sep_x, y + h - 14), 1)

    # ── Right: status ─────────────────────────────────────────
    status_x = sep_x + 18

    if radar_data["alert"]:
        pulse    = (math.sin(frame_count * 0.22) + 1) / 2
        amber_r  = int(200 + pulse * 40)
        amber_g  = int(90  + pulse * 20)
        col      = (amber_r, amber_g, 0)

        band_s = f_big.render(f"\u26a0  {radar_data['band']}", True, col)
        screen.blit(band_s, (status_x, y + h // 2 - band_s.get_height() // 2))

        # Signal bars — right side
        sv   = radar_data["strength"]
        bx   = px + pw - 115
        by   = y + h // 2 - 14
        bw, bh_max, gap = 13, 26, 5
        for i in range(5):
            bh  = int(bh_max * (0.30 + i * 0.175))
            top = by + (bh_max - bh)
            bar_col = (210, 172, 22) if i < sv else (38, 36, 22)
            pygame.draw.rect(screen, bar_col,
                             (bx + i * (bw + gap), top, bw, bh), border_radius=2)

        sig_s = f_sub.render(f"{sv}/5", True, (160, 145, 60))
        screen.blit(sig_s, (bx + 5 * (bw + gap) - sig_s.get_width() // 2,
                             by + bh_max + 3))
    else:
        pulse = (math.sin(frame_count * 0.045) + 1) / 2
        g_ch  = int(50 + pulse * 22)
        clr_s = f_big.render("\u2713  ALL CLEAR", True, (25, g_ch + 10, 25))
        screen.blit(clr_s, (status_x, y + h // 2 - clr_s.get_height() // 2))
