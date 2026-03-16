# config.py
# This file holds all global settings for the dashboard.
# --- Screen ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 480
FPS = 30  # Frames per second 
# --- Colors (R, G, B) ---
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
RED         = (220, 50, 50)
GREEN       = (50, 205, 50)
YELLOW      = (255, 215, 0)
DARK_GRAY   = (25, 25, 25)
ACCENT      = (0, 200, 255)   # The main "sports" highlight color (cyan-blue)

# --- Layout: how we split the screen ---
# Left panel = map (60% of width)
# Right panel = gauges + radar (40% of width)
MAP_PANEL_WIDTH     = int(SCREEN_WIDTH * 0.60)   # = 768px
GAUGE_PANEL_WIDTH   = int(SCREEN_WIDTH * 0.40)   # = 512px
RADAR_PANEL_HEIGHT  = int(SCREEN_HEIGHT * 0.35)  # bottom of right panel

# --- Gauge limits ---
MAX_SPEED = 160   # mph
MAX_RPM   = 8000  # RPM