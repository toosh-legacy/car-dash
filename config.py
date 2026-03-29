# config.py
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 480
FPS           = 60

# ── Base shared colors ─────────────────────────────────────────
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
DARK_GRAY   = (12, 12, 14)        # near-black background
GAUGE_FACE  = (13, 13, 15)        # gauge face (flat black)
TICK_MAJOR  = (225, 225, 228)     # white tick marks
TICK_MINOR  = (100, 98,  90)      # warm-gray minor ticks

# ── Porsche amber/white/black — single theme for all modes ─────
# Inspired by classic VDO instrument clusters: black face,
# white markings, amber-yellow accent, warm-gray sub-text.
DASH_THEME = {
    "name":       "DASH",
    "accent":     (222, 188,  36),   # classic amber-yellow
    "needle":     (238, 238, 242),   # near-white needle
    "arc":        (198, 165,  24),   # arc fill (slightly darker amber)
    "arc_warn":   (218, 138,  12),   # warning zone (deep amber)
    "arc_danger": (205,  92,   8),   # redline / danger (dark orange-amber)
    "text":       (235, 235, 238),   # near-white text
    "sub":        (155, 148, 108),   # warm gray sub-text
    "divider":    (110,  92,  14),   # dark amber divider lines
    "bg_tint":    ( 16,  14,   3),   # very dark warm tint for right panel
}

# All modes use the same visual theme — layout/content distinguishes them
THEMES = {
    "race":   DASH_THEME,
    "eco":    DASH_THEME,
    "normal": DASH_THEME,
}

# ── Layout ─────────────────────────────────────────────────────
MAP_PANEL_WIDTH    = int(SCREEN_WIDTH  * 0.60)   # 768 px  — map panel
GAUGE_PANEL_WIDTH  = int(SCREEN_WIDTH  * 0.40)   # 512 px  — instruments
RADAR_PANEL_HEIGHT = int(SCREEN_HEIGHT * 0.18)   #  86 px  — compact radar strip
MINI_GAUGE_H       = 72                           #  72 px  — small gauge row
GAUGE_AREA_HEIGHT  = SCREEN_HEIGHT - RADAR_PANEL_HEIGHT          # 394 px total instruments
MAIN_GAUGE_HEIGHT  = GAUGE_AREA_HEIGHT - MINI_GAUGE_H            # 322 px main gauges

# ── Gauge limits ───────────────────────────────────────────────
MAX_SPEED   = 160   # mph
MAX_RPM     = 8000
RPM_REDLINE = 6500
MIN_COOLANT = 140   # °F
MAX_COOLANT = 260
MIN_OIL     = 160
MAX_OIL     = 280
MIN_BATT    = 11.0  # V
MAX_BATT    = 15.0
