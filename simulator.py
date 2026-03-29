# simulator.py
# Simulated car sensors. Every function here will later be replaced
# by real hardware calls — the UI will never know the difference.

import random
import math
import time

_speed   = 60.0
_rpm     = 3000.0
_coolant = 195.0
_oil     = 210.0
_battery = 14.1
_throttle = 35.0
_mpg_instant = 28.0
_eco_score   = 72.0
_boost       = 0.0

# ── Core sensors ───────────────────────────────────────────────

def get_speed() -> float:
    global _speed
    _speed += random.uniform(-2.5, 2.5)
    _speed = max(0.0, min(160.0, _speed))
    return round(_speed, 1)

def get_rpm() -> float:
    global _rpm
    _rpm += random.uniform(-180, 180)
    _rpm = max(700.0, min(8000.0, _rpm))
    return round(_rpm, 0)

def get_gear() -> int:
    """Derive gear from speed (approximate 6-speed gearbox)."""
    breakpoints = [0, 20, 42, 65, 92, 118]
    for gear, bp in reversed(list(enumerate(breakpoints, 1))):
        if _speed >= bp:
            return gear
    return 1

def get_gps() -> dict:
    return {
        "lat": 29.7604 + random.uniform(-0.0008, 0.0008),
        "lon": -95.3698 + random.uniform(-0.0008, 0.0008),
    }

# ── Engine stats ───────────────────────────────────────────────

def get_engine_stats() -> dict:
    global _coolant, _oil, _battery, _throttle, _boost
    _coolant  += random.uniform(-0.4, 0.4);  _coolant  = max(140, min(260, _coolant))
    _oil      += random.uniform(-0.4, 0.4);  _oil      = max(160, min(280, _oil))
    _battery  += random.uniform(-0.02, 0.02);_battery  = max(11.5, min(15.0, _battery))
    _throttle += random.uniform(-3.0, 3.0);  _throttle = max(0.0, min(100.0, _throttle))
    _boost    += random.uniform(-0.8, 0.8);  _boost    = max(0.0, min(18.0, _boost))
    return {
        "coolant_temp": round(_coolant,  1),
        "oil_temp":     round(_oil,      1),
        "battery_v":    round(_battery,  2),
        "throttle":     round(_throttle, 1),
        "boost_psi":    round(_boost,    1),
    }

# ── Economy ────────────────────────────────────────────────────

def get_fuel_economy() -> dict:
    global _mpg_instant, _eco_score
    _mpg_instant += random.uniform(-1.5, 1.5)
    _mpg_instant  = max(8.0, min(55.0, _mpg_instant))
    _eco_score   += random.uniform(-1.0, 1.0)
    _eco_score    = max(0.0, min(100.0, _eco_score))
    return {
        "mpg_instant": round(_mpg_instant, 1),
        "mpg_trip":    round(28.5 + random.uniform(-0.2, 0.2), 1),
        "eco_score":   round(_eco_score, 0),
        "range_mi":    round((_eco_score / 100) * 320 + random.uniform(-2, 2), 0),
    }

# ── Tire pressures ─────────────────────────────────────────────

def get_tire_pressures() -> dict:
    return {
        "fl": round(random.uniform(31.5, 33.5), 1),
        "fr": round(random.uniform(31.5, 33.5), 1),
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
        print(get_speed(), get_rpm(), get_gear(), get_engine_stats())
        time.sleep(0.3)
