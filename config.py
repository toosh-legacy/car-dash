# config.py
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 480
FPS           = 60

# Base palette
BLACK     = (0, 0, 0)
WHITE     = (255, 255, 255)
DARK_GRAY = (18, 18, 20)
MID_GRAY  = (50, 50, 55)

# Gauge chrome / bezel shared colors
BEZEL_RIM   = (45, 45, 50)
BEZEL_LIGHT = (85, 85, 92)
BEZEL_DARK  = (30, 30, 34)
GAUGE_FACE  = (15, 15, 17)
TICK_MAJOR  = (215, 215, 220)
TICK_MINOR  = (105, 105, 115)

# ── Display mode themes ────────────────────────────────────────
THEMES = {
    "race": {
        "name":       "RACE",
        "accent":     (210,  45,  38),   # vivid red
        "needle":     (255,  60,  50),
        "arc":        (195,  40,  30),
        "arc_warn":   (255, 155,  20),
        "arc_danger": (220,  18,  18),
        "text":       (255, 215, 205),
        "sub":        (165,  85,  75),
        "divider":    (180,  30,  25),
        "bg_tint":    ( 28,   8,   8),
    },
    "eco": {
        "name":       "ECO",
        "accent":     ( 55, 195,  75),   # fresh green
        "needle":     ( 75, 225,  95),
        "arc":        ( 50, 180,  68),
        "arc_warn":   (195, 195,  35),
        "arc_danger": (215,  75,  35),
        "text":       (195, 255, 208),
        "sub":        ( 65, 150,  85),
        "divider":    ( 40, 160,  60),
        "bg_tint":    (  8,  25,  12),
    },
    "care": {
        "name":       "CARE",
        "accent":     (  0, 155, 225),   # steel blue
        "needle":     ( 35, 185, 255),
        "arc":        (  0, 145, 210),
        "arc_warn":   (255, 155,  18),
        "arc_danger": (215,  45,  38),
        "text":       (185, 228, 255),
        "sub":        ( 50, 120, 172),
        "divider":    (  0, 130, 195),
        "bg_tint":    (  6,  16,  28),
    },
}

# ── Layout ─────────────────────────────────────────────────────
MAP_PANEL_WIDTH    = int(SCREEN_WIDTH  * 0.60)   # 768 px
GAUGE_PANEL_WIDTH  = int(SCREEN_WIDTH  * 0.40)   # 512 px
RADAR_PANEL_HEIGHT = int(SCREEN_HEIGHT * 0.33)   # 158 px
GAUGE_AREA_HEIGHT  = SCREEN_HEIGHT - RADAR_PANEL_HEIGHT  # 322 px

# ── Gauge limits ───────────────────────────────────────────────
MAX_SPEED   = 160   # mph
MAX_RPM     = 8000
RPM_REDLINE = 6500
MAX_COOLANT = 260   # °F
MAX_OIL     = 280   # °F
MIN_OIL     = 160
MIN_COOLANT = 140
