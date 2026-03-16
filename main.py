# main.py
# Entry point for the sports dashboard.
# Opens the window and runs the main loop.

import pygame
import sys

# Import our own files
import config
import simulator
from ui.gauges import draw_arc_gauge, draw_bar_gauge
from ui.radar_alert import draw_radar_panel
from ui.map_view import draw_map_panel

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


def draw_gauge_panel(speed, rpm):
    gauge_center_x = config.MAP_PANEL_WIDTH + (config.GAUGE_PANEL_WIDTH // 2)
    x_offset = config.MAP_PANEL_WIDTH + 20

    # Radar panel starts here — we must stay above this line
    radar_top = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT  # = 312px

    # Arc speedometer — reduced radius so it fits cleanly
    draw_arc_gauge(
        screen,
        value     = speed,
        max_value = config.MAX_SPEED,
        x         = gauge_center_x,
        y         = 130,          # moved up slightly
        radius    = 100,          # reduced from 120 → 100
        label     = "SPEED",
        unit      = "mph",
        color     = config.GREEN
    )

    # RPM bar — positioned well above the radar divider line
    # radar_top - 70 gives us comfortable padding above the line
    bar_y = radar_top - 70
    draw_bar_gauge(
        screen,
        value     = rpm,
        max_value = config.MAX_RPM,
        x         = x_offset,
        y         = bar_y,
        width     = config.GAUGE_PANEL_WIDTH - 40,
        height    = 22,
        label     = "RPM",
        color     = config.ACCENT
    )
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
    frame_count = 0

    while True:
        # 1. HANDLE EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # 2. UPDATE DATA
        speed      = simulator.get_speed()
        rpm        = simulator.get_rpm()
        gps_data   = simulator.get_gps()
        radar_data = simulator.get_radar_alert()

        # 3. DRAW
        draw_background()
        draw_map_panel(screen, gps_data)
        draw_gauge_panel(speed, rpm)
        draw_radar_panel(radar_data)

        pygame.display.flip()
        clock.tick(config.FPS)
        frame_count += 1   # increment every frame for animations


if __name__ == "__main__":
    main()