# main.py
# Entry point for the sports dashboard.
# Opens the window and runs the main loop.

import pygame
import sys

# Import our own files
import config
import simulator

# --- Setup ---
pygame.init()  # Always call this first — starts up all pygame systems

screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Sports Dash")

clock = pygame.time.Clock()  # Used to control FPS

# --- Fonts ---
# pygame.font.SysFont("name", size) loads a font from your system
font_large  = pygame.font.SysFont("consolas", 48, bold=True)
font_medium = pygame.font.SysFont("consolas", 28)
font_small  = pygame.font.SysFont("consolas", 18)


# ─────────────────────────────────────────
# DRAW FUNCTIONS
# Each function is responsible for ONE panel
# ─────────────────────────────────────────

def draw_background():
    """Fill the whole screen dark, then draw panel dividers."""
    screen.fill(config.DARK_GRAY)

    # Draw a vertical dividing line between map and gauge panels
    pygame.draw.line(
        screen,
        config.ACCENT,
        (config.MAP_PANEL_WIDTH, 0),            # top point
        (config.MAP_PANEL_WIDTH, config.SCREEN_HEIGHT),  # bottom point
        2  # line thickness in pixels
    )

    # Draw a horizontal line dividing gauges from radar (right panel only)
    radar_top = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT
    pygame.draw.line(
        screen,
        config.ACCENT,
        (config.MAP_PANEL_WIDTH, radar_top),
        (config.SCREEN_WIDTH, radar_top),
        2
    )


def draw_map_panel(gps_data):
    """Left panel — GPS placeholder for now."""
    # We'll build a real map later. For now, just show coordinates.
    label = font_small.render("GPS / MAP", True, config.ACCENT)
    screen.blit(label, (20, 20))  # blit = "draw this surface at this position"

    lat_text = font_medium.render(f"LAT:  {gps_data['lat']:.5f}", True, config.WHITE)
    lon_text = font_medium.render(f"LON:  {gps_data['lon']:.5f}", True, config.WHITE)

    screen.blit(lat_text, (20, 60))
    screen.blit(lon_text, (20, 100))


def draw_gauge_panel(speed, rpm):
    """Top-right panel — Speed and RPM readouts."""
    x_offset = config.MAP_PANEL_WIDTH + 20  # start drawing 20px inside right panel

    # Section label
    label = font_small.render("GAUGES", True, config.ACCENT)
    screen.blit(label, (x_offset, 20))

    # Speed
    speed_label = font_small.render("SPEED (mph)", True, config.WHITE)
    speed_value = font_large.render(f"{int(speed)}", True, config.GREEN)
    screen.blit(speed_label, (x_offset, 50))
    screen.blit(speed_value, (x_offset, 75))

    # RPM
    rpm_label = font_small.render("RPM", True, config.WHITE)
    rpm_value  = font_large.render(f"{int(rpm)}", True, config.YELLOW)
    screen.blit(rpm_label, (x_offset, 150))
    screen.blit(rpm_value, (x_offset, 175))


def draw_radar_panel(radar_data):
    """Bottom-right panel — Radar alert display."""
    x_offset = config.MAP_PANEL_WIDTH + 20
    y_offset = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT + 10

    label = font_small.render("RADAR DETECTOR", True, config.ACCENT)
    screen.blit(label, (x_offset, y_offset))

    if radar_data["alert"]:
        # Show a red warning with band type
        alert_text = font_large.render(f"⚠ {radar_data['band']}", True, config.RED)
        bars_text   = font_medium.render(
            f"Signal: {'█' * radar_data['strength']}{'░' * (5 - radar_data['strength'])}",
            True, config.RED
        )
        screen.blit(alert_text, (x_offset, y_offset + 30))
        screen.blit(bars_text,  (x_offset, y_offset + 85))
    else:
        clear_text = font_medium.render("ALL CLEAR", True, config.GREEN)
        screen.blit(clear_text, (x_offset, y_offset + 40))


# ─────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────

def main():
    while True:

        # 1. HANDLE EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # User clicked the X button
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Press ESC to quit
                    pygame.quit()
                    sys.exit()

        # 2. UPDATE DATA — ask simulator for fresh values this frame
        speed       = simulator.get_speed()
        rpm         = simulator.get_rpm()
        gps_data    = simulator.get_gps()
        radar_data  = simulator.get_radar_alert()

        # 3. DRAW — paint everything onto the screen
        draw_background()
        draw_map_panel(gps_data)
        draw_gauge_panel(speed, rpm)
        draw_radar_panel(radar_data)

        # Flip = push everything we drew to the actual display
        pygame.display.flip()

        # Hold to our target FPS (30)
        clock.tick(config.FPS)


if __name__ == "__main__":
    main()