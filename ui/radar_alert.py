# ui/radar_alert.py
import pygame
import math
import config

def draw_radar_panel(screen, radar_data, frame_count):

    # Panel boundaries
    x          = config.MAP_PANEL_WIDTH + 10
    y          = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT + 8
    pan_w      = config.GAUGE_PANEL_WIDTH - 20
    pan_h      = config.RADAR_PANEL_HEIGHT - 16

    # Fonts
    font_title  = pygame.font.SysFont("consolas", 15)
    font_band   = pygame.font.SysFont("consolas", 36, bold=True)
    font_status = pygame.font.SysFont("consolas", 28, bold=True)
    font_small  = pygame.font.SysFont("consolas", 14)

    # --- Draw solid panel background ---
    # This replaces the transparent glow — much more visible on dark screens
    if radar_data["alert"]:
        # Pulse the background between dark red and bright red
        pulse = (math.sin(frame_count * 0.15) + 1) / 2   # 0.0 → 1.0
        r = int(80 + pulse * 120)   # red channel pulses from 80 to 200
        bg_color = (r, 0, 0)
    else:
        # Subtle slow green pulse for all clear
        pulse = (math.sin(frame_count * 0.05) + 1) / 2
        g = int(20 + pulse * 30)    # very subtle green
        bg_color = (0, g, 0)

    # Draw the solid background rectangle for the panel
    pygame.draw.rect(screen, bg_color, (x, y, pan_w, pan_h), border_radius=6)

    # Draw accent border around panel
    pygame.draw.rect(screen, config.ACCENT, (x, y, pan_w, pan_h), 2, border_radius=6)

    # --- Panel title ---
    title_surf = font_title.render("RADAR DETECTOR", True, config.ACCENT)
    screen.blit(title_surf, (x + 10, y + 8))

    if radar_data["alert"]:

        # --- Band label ---
        band_surf = font_band.render(f"⚠  {radar_data['band']}", True, config.WHITE)
        screen.blit(band_surf, (x + 10, y + 28))

        # --- Signal strength bars ---
        bar_x     = x + 10
        bar_y     = y + 82
        bar_w     = 18
        bar_h_max = 32
        gap       = 10
        strength  = radar_data["strength"]

        for i in range(5):
            bar_h   = int(bar_h_max * (0.4 + i * 0.15))
            bar_top = bar_y + (bar_h_max - bar_h)
            color   = config.WHITE if i < strength else (80, 30, 30)
            pygame.draw.rect(screen, color, (bar_x + i * (bar_w + gap), bar_top, bar_w, bar_h))

        # Strength label
        s_surf = font_small.render(f"SIGNAL: {strength}/5", True, config.WHITE)
        screen.blit(s_surf, (x + 10, y + 122))

    else:

        # --- All clear ---
        clear_surf = font_status.render("✓  ALL CLEAR", True, config.GREEN)
        screen.blit(clear_surf, (x + 10, y + 35))

        sub_surf = font_small.render("No signals detected", True, (180, 180, 180))
        screen.blit(sub_surf, (x + 10, y + 72))