```python
from gpiozero import LED
from time import sleep
import threading

# === CONFIGURABLE PARAMETERS ===
MIN_GREEN_DURATION        = 10     # Base green time in seconds
GREEN_PRIORITY_INCREMENT  = 2      # Additional seconds per priority level
EMERGENCY_GREEN_DURATION  = 15     # Green duration for emergencies
YELLOW_DURATION           = 6      # Fixed yellow light duration
YELLOW_BLINK_INTERVAL     = 1      # Interval for yellow blinking (seconds)
IDLE_BLINK_INTERVAL       = 1      # Interval between idle blinks

# Define LED pins for each direction (A, B, C)
led_pins = {
    'A': {'R': LED(2),  'Y': LED(3),  'G': LED(4)},
    'B': {'R': LED(17), 'Y': LED(27), 'G': LED(22)},
    'C': {'R': LED(10), 'Y': LED(9),  'G': LED(11)},
}

# Queue to hold traffic inputs
traffic_queue = { 'A': [], 'B': [], 'C': [] }

# Lock for thread safety
lock = threading.Lock()

# Priority map
priority_map = {
    'car': 1,
    'pedestrian': 2,
    'vip': 5,
    'police': 8,
    'fire': 9,
    'ambulance': 10,
    'accident': 20
}

emergency_state = False

# --- Utility Functions ---
def set_phase(active_dir, color):
    """Set active_dir to color, others to red."""
    for d, leds in led_pins.items():
        for c, led in leds.items():
            if d == active_dir:
                led.on() if c == color else led.off()
            else:
                led.on() if c == 'R' else led.off()


def blink_yellow_all(cycles):
    """Blink yellow for all directions, keeping red on during off-phase."""
    for _ in range(cycles):
        # Yellow on, red off for all
        for d in led_pins:
            led_pins[d]['Y'].on()
            led_pins[d]['R'].off()
            led_pins[d]['G'].off()
        sleep(YELLOW_BLINK_INTERVAL)
        # Revert to red on for all, yellow off
        for d in led_pins:
            led_pins[d]['R'].on()
            led_pins[d]['Y'].off()
            led_pins[d]['G'].off()
        sleep(YELLOW_BLINK_INTERVAL)

# --- Main Controller Thread ---
def smart_traffic_controller():
    global emergency_state
    # Initialize: all red
    for d in led_pins:
        set_phase(d, 'R')
    while True:
        sleep(1)
        with lock:
            # 1. Emergency handling
            for d in traffic_queue:
                for vehicle in traffic_queue[d]:
                    if vehicle in ('ambulance', 'fire', 'police', 'accident'):
                        emergency_state = True
                        print(f"[EMERGENCY] {vehicle.upper()} in direction {d}")
                        set_phase(d, 'G')
                        sleep(EMERGENCY_GREEN_DURATION)
                        set_phase(d, 'R')
                        traffic_queue[d].remove(vehicle)
                        emergency_state = False
                        break
                if emergency_state:
                    break

            if emergency_state:
                continue

            # 2. Select highest-priority queued direction
            max_prio = 0
            selected_dir = None
            for d, q in traffic_queue.items():
                if q:
                    pr = priority_map[q[0]]
                    if pr > max_prio:
                        max_prio = pr
                        selected_dir = d

            # 3. If someone waiting, grant green
            if selected_dir:
                vehicle = traffic_queue[selected_dir].pop(0)
                print(f"[INFO] Granting GREEN for {vehicle.upper()} at {selected_dir}")
                # GREEN phase
                green_time = MIN_GREEN_DURATION + (priority_map[vehicle] * GREEN_PRIORITY_INCREMENT)
                set_phase(selected_dir, 'G')
                sleep(green_time)
                # YELLOW transition
                print(f"[TRANSITION] YELLOW at {selected_dir}")
                # During yellow, others stay red
                set_phase(selected_dir, 'Y')
                sleep(YELLOW_DURATION)
                # RED phase before next: all directions red
                for d in led_pins:
                    set_phase(d, 'R')
                sleep(2)
            else:
                # 4. Idle: blink yellow all with red fallback
                blink_yellow_all(cycles=2)

# Start controller thread
def main():
    threading.Thread(target=smart_traffic_controller, daemon=True).start()
    # --- Input Loop ---
    try:
        while True:
            entry = input("Enter input (A,car): ").strip().lower()
            if entry == 'quit':
                break
            try:
                d, v = entry.split(',')
                d = d.upper()
                if d in traffic_queue and v in priority_map:
                    with lock:
                        traffic_queue[d].append(v)
                else:
                    print("[ERROR] Valid input: A,car or B,ambulance etc.")
            except ValueError:
                print("[ERROR] Invalid format. Use: A,car")
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure all red on shutdown
        for d in led_pins:
            set_phase(d, 'R')
        print("\n[SHUTDOWN] Traffic system turned off.")

if __name__ == '__main__':
    main()
```