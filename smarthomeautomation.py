```python
#!/usr/bin/env python3
import time
import threading
from bluetooth import discover_devices
from datetime import datetime
from gpiozero import LED, DistanceSensor

# === CONFIGURATION ===
OWNER_MAC          = 'AA:BB:CC:DD:EE:FF'  # replace with your phone’s BT MAC
BT_SCAN_INTERVAL   = 30                   # seconds between scans
OWNER_TIMEOUT      = 600                  # seconds to consider owner away
ENTRANCE_DIST      = 0.5                  # meters threshold for entrance sensor
ROOM_DIST          = 1.0                  # meters threshold for room sensor
INTRUDER_DIST      = 0.5                  # meters => intruder distance
PRESENCE_TIMEOUT   = 60                   # seconds before lights auto-off
NIGHT_START, NIGHT_END = 22, 6            # hours for night mode
MOOD_DAY_COLORS    = ['Y','G']            # sequence in daytime
MOOD_NIGHT_COLORS  = ['B','G']            # sequence at night
ALERT_BLINKS       = 6
ALERT_INTERVAL     = 0.3                  # sec

# === GPIOZERO SETUP ===
# LEDs mapping: R=9, G=10, B=11, Y=22
leds = {
    'R': LED(9),
    'G': LED(10),
    'B': LED(11),
    'Y': LED(22)
}
# Ultrasonic sensors wiring:
# Entrance sensor: trigger=2, echo=3 (GPIO2/3 have fixed pull-ups)
# Room sensor:     trigger=4, echo=17
entrance_sensor = DistanceSensor(trigger=2, echo=3, max_distance=2,
                                 echo_pull_up=False)
room_sensor     = DistanceSensor(trigger=4, echo=17, max_distance=2,
                                 echo_pull_up=False)

# === STATE ===
last_bt_seen       = 0
home_mode          = False
last_room_presence = time.time()

# === UTILITY FUNCTIONS ===
def set_led(color=None):
    """Turn on specified LED, turn off others. color None => all off"""
    for c, led in leds.items():
        if color and c == color:
            led.on()
        else:
            led.off()


def blink_led(color, times, interval):
    for _ in range(times):
        leds[color].on()
        time.sleep(interval)
        leds[color].off()
        time.sleep(interval)


def led_sequence(seq, delay=0.5):
    for c in seq:
        set_led(c)
        time.sleep(delay)
    set_led(None)

# === THREADS ===

def bt_scanner():
    """Scan built‑in Bluetooth for owner presence."""
    global last_bt_seen, home_mode
    while True:
        nearby = discover_devices(duration=8)
        now = time.time()
        if OWNER_MAC in nearby:
            last_bt_seen = now
            if not home_mode:
                home_mode = True
                print("[BT] Owner arrived → Home Mode")
        else:
            if home_mode and now - last_bt_seen > OWNER_TIMEOUT:
                home_mode = False
                print("[BT] Owner left → Away Mode")
        time.sleep(BT_SCAN_INTERVAL)


def entrance_monitor():
    """Welcome owner or alert intruder at the door."""
    while True:
        d = entrance_sensor.distance  # in meters
        if d and d < ENTRANCE_DIST:
            if home_mode:
                print("[ENTRY] Welcome home!")
                led_sequence(['G','B','Y','G'], delay=0.3)
            else:
                print("[ALERT] Intruder at entrance!")
                blink_led('R', ALERT_BLINKS, ALERT_INTERVAL)
        time.sleep(1)


def room_monitor():
    """Adaptive mood lighting and night‑time intrusion alert."""
    global last_room_presence
    while True:
        d = room_sensor.distance
        now = time.time()
        hour = datetime.now().hour

        # Night intrusion
        if (hour >= NIGHT_START or hour < NIGHT_END) and d and d < INTRUDER_DIST:
            print("[ALERT] Night intrusion detected!")
            blink_led('R', ALERT_BLINKS, ALERT_INTERVAL)

        # Presence-based mood lighting
        if home_mode and d and d < ROOM_DIST:
            last_room_presence = now
            if NIGHT_END <= hour < NIGHT_START:
                led_sequence(MOOD_DAY_COLORS, delay=0.7)
            else:
                led_sequence(MOOD_NIGHT_COLORS, delay=0.7)
        else:
            if now - last_room_presence > PRESENCE_TIMEOUT:
                set_led(None)

        time.sleep(1)

# === MAIN ===
if __name__ == '__main__':
    try:
        for fn in (bt_scanner, entrance_monitor, room_monitor):
            t = threading.Thread(target=fn, daemon=True)
            t.start()
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        pass
    finally:
        set_led(None)
        print("\n[SHUTDOWN] System off")
```