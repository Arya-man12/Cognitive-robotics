import serial
import math

import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Serial port for Arduino (adjust if needed)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5)

xs, ys = [], []
import numpy as np

def update(frame):
    global xs, ys
    
    while ser.in_waiting > 0:
        try:
            line = ser.readline().decode().strip()
            if "," in line:
                angle_str, dist_str = line.split(",")
                angle = float(angle_str)
                dist = float(dist_str)

                theta = math.radians(angle)
                x = dist * math.cos(theta)
                y = dist * math.sin(theta)

                xs.append(x)
                ys.append(y)
        except:
            continue

    # Safely convert to (N,2) array
    if len(xs) > 0 and len(ys) > 0:
        coords = np.column_stack((xs, ys))
        scat.set_offsets(coords)
    else:
        scat.set_offsets(np.empty((0, 2)))

    return scat,

fig, ax = plt.subplots()
scat = ax.scatter([], [], c="red", s=10)
ax.set_xlim(-200, 200)
ax.set_ylim(0, 200)
ax.set_aspect('equal')
ax.set_title("Ultrasonic Mapping (Arduino → RPi)")

ani = animation.FuncAnimation(fig, update, interval=200, blit=True)
plt.show()


