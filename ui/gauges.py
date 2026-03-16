# ui/gauges.py
# Draws the speedometer arc gauge and RPM bar gauge.
# These functions receive the screen and a value, and draw onto the screen.

import pygame
import math
import config

def draw_arc_gauge(screen, value, max_value, x, y, radius, label, unit, color):
    """
    Draws a circular arc gauge (used for speedometer).
    
    Parameters:
        screen     — the pygame display surface to draw on
        value      — current reading (e.g. 97.5)
        max_value  — maximum possible value (e.g. 160)
        x, y       — center point of the gauge
        radius     — size of the arc
        label      — text shown above the number (e.g. "SPEED")
        unit       — text shown below the number (e.g. "mph")
        color      — color of the active arc
    """

    # --- Background arc (full range, dark) ---
    # Arcs in pygame go counter-clockwise from the right (east = 0 radians)
    # We want our gauge to sweep from bottom-left to bottom-right (like a real speedo)
    start_angle = math.radians(220)   # where the arc starts (left side)
    end_angle   = math.radians(-40)   # where the arc ends (right side)

    # Draw the dim "empty" track first
    pygame.draw.arc(
        screen,
        config.DARK_GRAY,
        (x - radius, y - radius, radius * 2, radius * 2),  # bounding box
        end_angle,    # pygame draws CCW so we swap start/end for visual direction
        start_angle,
        8             # thickness of the arc line in pixels
    )

    # --- Active arc (fills based on current value) ---
    # Map value to an angle within our sweep range
    sweep = math.radians(260)  # total sweep = 260 degrees (from 220 to -40)
    value_angle = start_angle - (value / max_value) * sweep

    if value > 0:
        pygame.draw.arc(
            screen,
            color,
            (x - radius, y - radius, radius * 2, radius * 2),
            value_angle,
            start_angle,
            8
        )

    # --- Needle line ---
    # Calculate the endpoint of the needle using trigonometry
    needle_length = radius - 10
    needle_x = x + needle_length * math.cos(value_angle)
    needle_y = y - needle_length * math.sin(value_angle)
    pygame.draw.line(screen, config.WHITE, (x, y), (int(needle_x), int(needle_y)), 3)

    # --- Center dot ---
    pygame.draw.circle(screen, config.WHITE, (x, y), 6)

    # --- Text: label, value, unit ---
    font_label = pygame.font.SysFont("consolas", 16)
    font_value = pygame.font.SysFont("consolas", 36, bold=True)
    font_unit  = pygame.font.SysFont("consolas", 14)

    label_surf = font_label.render(label, True, config.ACCENT)
    value_surf = font_value.render(str(int(value)), True, config.WHITE)
    unit_surf  = font_unit.render(unit, True, config.ACCENT)

    # Center each text element horizontally on x
    screen.blit(label_surf, (x - label_surf.get_width() // 2, y - 20))
    screen.blit(value_surf, (x - value_surf.get_width() // 2, y + 10))
    screen.blit(unit_surf,  (x - unit_surf.get_width()  // 2, y + 48))


def draw_bar_gauge(screen, value, max_value, x, y, width, height, label, color):
    """
    Draws a horizontal bar gauge (used for RPM).

    Parameters:
        screen     — pygame display surface
        value      — current reading
        max_value  — maximum value
        x, y       — top-left corner of the bar
        width      — total width of the bar
        height     — height of the bar
        label      — label shown above
        color      — fill color
    """

    font_label = pygame.font.SysFont("consolas", 16)
    font_value = pygame.font.SysFont("consolas", 22, bold=True)

    # Label above the bar
    label_surf = font_label.render(label, True, config.ACCENT)
    screen.blit(label_surf, (x, y - 22))

    # Background track
    pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height), border_radius=4)

    # Filled portion — proportional to value
    fill_width = int((value / max_value) * width)

    # Color shifts red when RPM is high (above 75%)
    if value / max_value > 0.75:
        fill_color = config.RED
    elif value / max_value > 0.50:
        fill_color = config.YELLOW
    else:
        fill_color = color

    if fill_width > 0:
        pygame.draw.rect(screen, fill_color, (x, y, fill_width, height), border_radius=4)

    # Border around the bar
    pygame.draw.rect(screen, config.ACCENT, (x, y, width, height), 2, border_radius=4)

    # Value text to the right of the bar
    value_surf = font_value.render(f"{int(value)} RPM", True, config.WHITE)
    screen.blit(value_surf, (x, y + height + 6))