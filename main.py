# main.py
# Entry point. Runs the main loop and delegates rendering to mode modules.
#
# Controls:
#   1  →  RACE mode     (tachometer, boost, gear)
#   2  →  ECO  mode     (speed, MPG, eco score)
#   3  →  CARE mode     (temps, battery, tyre pressures)
#   ESC / Q  →  quit

import pygame
import sys
import math

import config
import simulator
from ui.map_view   import draw_map_panel
from ui.radar_alert import draw_radar_panel
from ui.modes       import draw_mode_tabs, draw_race_panel, draw_eco_panel, draw_care_panel

# ── Init ──────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Car Dash")
clock  = pygame.time.Clock()

# ── Smooth interpolation state ────────────────────────────────
# Instead of jumping to the raw simulator value each frame,
# we lerp toward it — this gives needle glide like a real gauge.

_sm = {
    "speed":    60.0,
    "rpm":      3000.0,
    "coolant":  195.0,
    "oil":      210.0,
    "battery":  14.1,
    "throttle": 35.0,
    "boost":    0.0,
    "mpg_inst": 28.0,
    "eco":      72.0,
}

def _lerp(key, target, rate=0.07):
    _sm[key] += (target - _sm[key]) * rate
    return _sm[key]


# ── Background ────────────────────────────────────────────────

def draw_background(theme):
    screen.fill(config.DARK_GRAY)

    # Right panel tint (very subtle)
    tint_surf = pygame.Surface((config.GAUGE_PANEL_WIDTH, config.SCREEN_HEIGHT),
                               pygame.SRCALPHA)
    tint_surf.fill((*theme["bg_tint"], 90))
    screen.blit(tint_surf, (config.MAP_PANEL_WIDTH, 0))

    # Vertical divider
    div_x = config.MAP_PANEL_WIDTH
    for off, col in ((2, (30, 30, 34)), (0, theme["divider"])):
        pygame.draw.line(screen, col,
                         (div_x + off, 0),
                         (div_x + off, config.SCREEN_HEIGHT), 1)

    # Horizontal divider (gauge area / radar)
    radar_y = config.SCREEN_HEIGHT - config.RADAR_PANEL_HEIGHT
    for off, col in ((1, (30, 30, 34)), (0, theme["divider"])):
        pygame.draw.line(screen, col,
                         (config.MAP_PANEL_WIDTH, radar_y + off),
                         (config.SCREEN_WIDTH,    radar_y + off), 1)


# ── Main loop ─────────────────────────────────────────────────

def main():
    current_mode = "race"
    frame_count  = 0

    while True:
        # 1. Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_1:
                    current_mode = "race"
                if event.key == pygame.K_2:
                    current_mode = "eco"
                if event.key == pygame.K_3:
                    current_mode = "care"

        theme = config.THEMES[current_mode]

        # 2. Collect raw sensor data
        raw_speed   = simulator.get_speed()
        raw_rpm     = simulator.get_rpm()
        raw_engine  = simulator.get_engine_stats()
        raw_economy = simulator.get_fuel_economy()
        gps_data    = simulator.get_gps()
        radar_data  = simulator.get_radar_alert()
        tyre_data   = simulator.get_tire_pressures()
        gear        = simulator.get_gear()

        # 3. Smooth values
        speed    = _lerp("speed",    raw_speed,              rate=0.08)
        rpm      = _lerp("rpm",      raw_rpm,                rate=0.07)
        coolant  = _lerp("coolant",  raw_engine["coolant_temp"], rate=0.04)
        oil      = _lerp("oil",      raw_engine["oil_temp"],    rate=0.04)
        battery  = _lerp("battery",  raw_engine["battery_v"],   rate=0.05)
        throttle = _lerp("throttle", raw_engine["throttle"],    rate=0.10)
        boost    = _lerp("boost",    raw_engine["boost_psi"],   rate=0.09)
        mpg_inst = _lerp("mpg_inst", raw_economy["mpg_instant"],rate=0.06)
        eco_sc   = _lerp("eco",      raw_economy["eco_score"],  rate=0.04)

        data = {
            "speed":   speed,
            "rpm":     rpm,
            "gear":    gear,
            "gps":     gps_data,
            "radar":   radar_data,
            "tyres":   tyre_data,
            "engine": {
                "coolant_temp": coolant,
                "oil_temp":     oil,
                "battery_v":    battery,
                "throttle":     throttle,
                "boost_psi":    boost,
            },
            "economy": {
                "mpg_instant": mpg_inst,
                "mpg_trip":    raw_economy["mpg_trip"],
                "eco_score":   eco_sc,
                "range_mi":    raw_economy["range_mi"],
            },
        }

        # 4. Draw
        draw_background(theme)
        draw_map_panel(screen, gps_data, current_mode, theme)

        # Mode tabs (top of right panel)
        draw_mode_tabs(screen, current_mode, frame_count)

        if current_mode == "race":
            draw_race_panel(screen, data, theme, frame_count)
        elif current_mode == "eco":
            draw_eco_panel(screen, data, theme, frame_count)
        elif current_mode == "care":
            draw_care_panel(screen, data, theme, frame_count)

        draw_radar_panel(screen, radar_data, theme, frame_count)

        pygame.display.flip()
        clock.tick(config.FPS)
        frame_count += 1


if __name__ == "__main__":
    main()
