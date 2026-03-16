# simulator.py
# Pretends to be your car's sensors.
# Every function here will later be replaced by a real hardware call
# — but the UI will never know the difference.

import random
import time
import math

# We use this to make speed/RPM feel smooth rather than jumping randomly
_current_speed = 60.0
_current_rpm   = 3000.0

def get_speed() -> float:
    """Returns simulated speed in mph. Drifts up and down smoothly."""
    global _current_speed
    # Nudge speed slightly each call — feels like real driving
    _current_speed += random.uniform(-2.0, 2.0)
    # Clamp between 0 and 160 so it never goes out of range
    _current_speed = max(0.0, min(160.0, _current_speed))
    return round(_current_speed, 1)

def get_rpm() -> float:
    """Returns simulated RPM. Loosely tied to speed."""
    global _current_rpm
    _current_rpm += random.uniform(-150, 150)
    _current_rpm = max(800.0, min(8000.0, _current_rpm))
    return round(_current_rpm, 0)

def get_gps() -> dict:
    """Returns a fake GPS coordinate near Houston, TX.
    Drifts slightly to simulate movement."""
    return {
        "lat": 29.7604 + random.uniform(-0.001, 0.001),
        "lon": -95.3698 + random.uniform(-0.001, 0.001),
        "speed_gps": get_speed()   # GPS also tracks speed independently
    }

def get_engine_stats() -> dict:
    """Returns simulated engine stats we'll use later."""
    return {
        "coolant_temp": round(random.uniform(185.0, 210.0), 1),  # Fahrenheit
        "oil_temp":     round(random.uniform(200.0, 230.0), 1),
        "battery_v":    round(random.uniform(13.8, 14.4), 2),    # Volts
        "throttle":     round(random.uniform(0.0, 100.0), 1)     # Percent
    }

def get_radar_alert() -> dict:
    """Simulates a radar speed gun detection event.
    90% of the time there's nothing. 10% chance of a hit."""
    roll = random.random()  # random float between 0.0 and 1.0

    if roll > 0.90:
        band = random.choice(["X-BAND", "K-BAND", "Ka-BAND"])
        strength = random.randint(1, 5)  # signal strength bars (1–5)
        return {"alert": True, "band": band, "strength": strength}
    
    return {"alert": False, "band": None, "strength": 0}


# --- Quick test: run this file directly to see sample output ---
if __name__ == "__main__":
    print("Testing simulator output...\n")
    for i in range(100):
        print(f"Speed:  {get_speed()} mph")
        print(f"RPM:    {get_rpm()}")
        print(f"GPS:    {get_gps()}")
        print(f"Engine: {get_engine_stats()}")
        print(f"Radar:  {get_radar_alert()}")
        print("-" * 40)
        time.sleep(0.5)