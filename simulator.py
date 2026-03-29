# simulator.py
# Simulated car sensors. Every function here will later be replaced
# by real hardware calls — the UI will never know the difference.

import random
import math
import time

_speed    = 58.0
_rpm      = 3200.0
_coolant  = 195.0
_oil      = 212.0
_battery  = 14.1
_throttle = 32.0
_brake    = 5.0
_boost    = 0.8
_lat_g    = 0.0
_lon_g    = 0.0
_mpg_inst = 28.0
_eco_sc   = 72.0
_trip_dist  = 0.0
_trip_mins  = 0.0
_smooth_sc  = 80.0    # smooth driving score (0-100)


# ── Core sensors ───────────────────────────────────────────────

def get_speed() -> float:
    global _speed
    _speed += random.uniform(-2.5, 2.5)
    _speed = max(0.0, min(160.0, _speed))
    return round(_speed, 1)

def get_rpm() -> float:
    global _rpm
    _rpm += random.uniform(-200, 200)
    _rpm = max(700.0, min(8000.0, _rpm))
    return round(_rpm, 0)

def get_gear() -> int:
    """Approximate 6-speed gearbox derived from speed."""
    breaks = [0, 18, 40, 62, 88, 115]
    for g, bp in reversed(list(enumerate(breaks, 1))):
        if _speed >= bp:
            return g
    return 1

def get_gps() -> dict:
    return {
        "lat": 29.7604 + random.uniform(-0.0008, 0.0008),
        "lon": -95.3698 + random.uniform(-0.0008, 0.0008),
    }


# ── Pedal inputs ───────────────────────────────────────────────

def get_throttle() -> float:
    global _throttle
    _throttle += random.uniform(-5, 5)
    _throttle = max(0.0, min(100.0, _throttle))
    return round(_throttle, 1)

def get_brake_pressure() -> float:
    global _brake
    _brake += random.uniform(-4, 4)
    _brake = max(0.0, min(100.0, _brake))
    return round(_brake, 1)

def get_boost_psi() -> float:
    global _boost
    _boost += random.uniform(-0.6, 0.6)
    _boost = max(0.0, min(18.0, _boost))
    return round(_boost, 1)


# ── G-force ────────────────────────────────────────────────────

def get_g_force() -> dict:
    global _lat_g, _lon_g
    _lat_g += random.uniform(-0.08, 0.08)
    _lat_g  = max(-1.8, min(1.8, _lat_g))
    _lon_g += random.uniform(-0.06, 0.06)
    _lon_g  = max(-1.4, min(0.9, _lon_g))
    return {"lat": round(_lat_g, 2), "lon": round(_lon_g, 2)}


# ── Engine stats ───────────────────────────────────────────────

def get_engine_stats() -> dict:
    global _coolant, _oil, _battery
    _coolant += random.uniform(-0.3, 0.3); _coolant = max(140, min(260, _coolant))
    _oil     += random.uniform(-0.3, 0.3); _oil     = max(160, min(280, _oil))
    _battery += random.uniform(-0.015, 0.015); _battery = max(11.5, min(15.0, _battery))
    return {
        "coolant_temp": round(_coolant, 1),
        "oil_temp":     round(_oil,     1),
        "battery_v":    round(_battery, 2),
    }


# ── Economy + driving style ────────────────────────────────────

def get_fuel_economy() -> dict:
    global _mpg_inst, _eco_sc
    _mpg_inst += random.uniform(-1.2, 1.2); _mpg_inst = max(8.0, min(55.0, _mpg_inst))
    _eco_sc   += random.uniform(-0.8, 0.8); _eco_sc   = max(0.0, min(100.0, _eco_sc))
    return {
        "mpg_instant": round(_mpg_inst, 1),
        "mpg_trip":    round(28.5 + random.uniform(-0.2, 0.2), 1),
        "eco_score":   round(_eco_sc, 0),
        "range_mi":    round((_eco_sc / 100) * 320 + random.uniform(-1, 1), 0),
    }

def get_trip_data() -> dict:
    global _trip_dist, _trip_mins, _smooth_sc
    _trip_dist  += _speed / 3600.0          # miles per 1/60s tick
    _trip_mins  += 1.0 / 60.0              # 1 second per call at 60 fps approx
    _smooth_sc  += random.uniform(-0.5, 0.5)
    _smooth_sc  -= max(0, (_throttle - 70) * 0.02)   # punish hard throttle
    _smooth_sc  -= max(0, (_brake    - 60) * 0.03)   # punish hard braking
    _smooth_sc   = max(0.0, min(100.0, _smooth_sc))
    return {
        "distance":   round(_trip_dist, 1),
        "time_min":   round(_trip_mins, 0),
        "avg_speed":  round(_speed * 0.9 + random.uniform(-1, 1), 1),
        "smooth_score": round(_smooth_sc, 0),
    }

def get_drive_style_score() -> float:
    """0 = very gentle, 100 = very aggressive."""
    return round((_throttle * 0.55 + _brake * 0.45), 1)


# ── Tyres ──────────────────────────────────────────────────────

def get_tire_pressures() -> dict:
    return {
        "fl": round(random.uniform(31.4, 33.6), 1),
        "fr": round(random.uniform(31.4, 33.6), 1),
        "rl": round(random.uniform(30.5, 32.5), 1),
        "rr": round(random.uniform(30.5, 32.5), 1),
    }


# ── Radar ──────────────────────────────────────────────────────

def get_radar_alert() -> dict:
    if random.random() > 0.90:
        return {
            "alert":    True,
            "band":     random.choice(["X-BAND", "K-BAND", "Ka-BAND"]),
            "strength": random.randint(1, 5),
        }
    return {"alert": False, "band": None, "strength": 0}


if __name__ == "__main__":
    for _ in range(5):
        print(get_speed(), get_rpm(), get_gear(), get_throttle(), get_brake_pressure())
        time.sleep(0.2)
