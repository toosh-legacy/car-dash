# main.py
# Entry point for the sports dashboard.
# Opens the window and runs the main loop.

import pygame
import sys

import config 
import sim

# for the setup of the game window and main loop
pygame.init()

screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Sports Car Dashboard")

clock = pygame.time.Clock() # for controlling frame rate

# --- Fonts ---
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