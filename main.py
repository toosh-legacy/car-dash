# main.py
# Controls:  1 = RACE  |  2 = ECO  |  3 = NORMAL  |  ESC/Q = quit

import pygame
import sys

import config
import simulator
from ui.map_view    import draw_map_panel
from ui.radar_alert import draw_radar_panel
from ui.modes       import (draw_mode_tabs, draw_mini_gauge_strip,
                             draw_race_panel, draw_eco_panel, draw_normal_panel)

pygame.init()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Car Dash")
clock  = pygame.time.Clock()

# ── Smooth interpolation state ────────────────────────────────
_sm = {
    "speed": 60.0, "rpm": 3200.0,
    "throttle": 32.0, "brake": 5.0, "boost": 0.8,
    "lat_g": 0.0, "lon_g": 0.0,
    "coolant": 195.0, "oil": 212.0, "battery": 14.1,
    "mpg_inst": 28.0, "eco_score": 72.0,
    "drive_style": 30.0, "smooth": 80.0,
}

def _lerp(key, target, rate=0.07):
    _sm[key] += (target - _sm[key]) * rate
    return _sm[key]


# ── Background ────────────────────────────────────────────────

def draw_background(theme):
    screen.fill(config.DARK_GRAY)

    # Right panel warm tint
    tint = pygame.Surface((config.GAUGE_PANEL_WIDTH, config.SCREEN_HEIGHT),
                          pygame.SRCALPHA)
    tint.fill((*theme["bg_tint"], 90))
    screen.blit(tint, (config.MAP_PANEL_WIDTH, 0))

    # Vertical divider (map | instruments)
    dvx = config.MAP_PANEL_WIDTH
    pygame.draw.line(screen, (24, 22, 8),  (dvx + 1, 0), (dvx + 1, config.SCREEN_HEIGHT), 1)
    pygame.draw.line(screen, theme["divider"], (dvx, 0), (dvx, config.SCREEN_HEIGHT), 1)

    # Horizontal divider (main gauges | mini strip)
    pygame.draw.line(screen, (24, 22, 8),
                     (config.MAP_PANEL_WIDTH, config.MAIN_GAUGE_HEIGHT + 1),
                     (config.SCREEN_WIDTH,    config.MAIN_GAUGE_HEIGHT + 1), 1)

    # Horizontal divider (mini strip | radar)
    rdy = config.GAUGE_AREA_HEIGHT
    pygame.draw.line(screen, (24, 22, 8),  (config.MAP_PANEL_WIDTH, rdy + 1), (config.SCREEN_WIDTH, rdy + 1), 1)
    pygame.draw.line(screen, theme["divider"], (config.MAP_PANEL_WIDTH, rdy), (config.SCREEN_WIDTH, rdy), 1)


# ── Main loop ─────────────────────────────────────────────────

def main():
    current_mode = "race"
    frame_count  = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_1: current_mode = "race"
                if event.key == pygame.K_2: current_mode = "eco"
                if event.key == pygame.K_3: current_mode = "normal"

        # Single shared theme — all modes use amber/white/black
        theme = config.DASH_THEME

        # Raw sensor reads
        raw_speed    = simulator.get_speed()
        raw_rpm      = simulator.get_rpm()
        raw_throttle = simulator.get_throttle()
        raw_brake    = simulator.get_brake_pressure()
        raw_boost    = simulator.get_boost_psi()
        raw_g        = simulator.get_g_force()
        raw_engine   = simulator.get_engine_stats()
        raw_econ     = simulator.get_fuel_economy()
        raw_trip     = simulator.get_trip_data()
        raw_style    = simulator.get_drive_style_score()
        gps_data     = simulator.get_gps()
        radar_data   = simulator.get_radar_alert()
        gear         = simulator.get_gear()

        # Smoothed values
        speed       = _lerp("speed",       raw_speed,                  0.08)
        rpm         = _lerp("rpm",         raw_rpm,                    0.07)
        throttle    = _lerp("throttle",    raw_throttle,               0.13)
        brake       = _lerp("brake",       raw_brake,                  0.15)
        boost       = _lerp("boost",       raw_boost,                  0.09)
        lat_g       = _lerp("lat_g",       raw_g["lat"],               0.10)
        lon_g       = _lerp("lon_g",       raw_g["lon"],               0.10)
        coolant     = _lerp("coolant",     raw_engine["coolant_temp"], 0.04)
        oil         = _lerp("oil",         raw_engine["oil_temp"],     0.04)
        battery     = _lerp("battery",     raw_engine["battery_v"],    0.05)
        mpg_inst    = _lerp("mpg_inst",    raw_econ["mpg_instant"],    0.06)
        eco_sc      = _lerp("eco_score",   raw_econ["eco_score"],      0.04)
        drive_style = _lerp("drive_style", raw_style,                  0.08)
        smooth      = _lerp("smooth",      raw_trip["smooth_score"],   0.04)

        engine_data = {
            "coolant_temp": coolant,
            "oil_temp":     oil,
            "battery_v":    battery,
        }

        data = {
            "speed":       speed,
            "rpm":         rpm,
            "gear":        gear,
            "throttle":    throttle,
            "brake":       brake,
            "boost":       boost,
            "g_force":     {"lat": lat_g, "lon": lon_g},
            "drive_style": drive_style,
            "engine":      engine_data,
            "economy": {
                "mpg_instant": mpg_inst,
                "mpg_trip":    raw_econ["mpg_trip"],
                "eco_score":   eco_sc,
                "range_mi":    raw_econ["range_mi"],
            },
            "trip": {
                "distance":     raw_trip["distance"],
                "time_min":     raw_trip["time_min"],
                "avg_speed":    raw_trip["avg_speed"],
                "smooth_score": smooth,
            },
            "gps":   gps_data,
            "radar": radar_data,
        }

        # Draw
        draw_background(theme)
        draw_map_panel(screen, gps_data, current_mode, theme)
        draw_mode_tabs(screen, current_mode, frame_count)

        if current_mode == "race":
            draw_race_panel(screen, data, theme, frame_count)
        elif current_mode == "eco":
            draw_eco_panel(screen, data, theme, frame_count)
        elif current_mode == "normal":
            draw_normal_panel(screen, data, theme, frame_count)

        # Mini gauge strip — always visible in all modes
        draw_mini_gauge_strip(screen, engine_data, theme)

        draw_radar_panel(screen, radar_data, theme, frame_count)

        pygame.display.flip()
        clock.tick(config.FPS)
        frame_count += 1


if __name__ == "__main__":
    main()
