import serial
import cv2
import numpy as np
import time
from screeninfo import get_monitors

# Serial Configuration
SERIAL_PORT = '/dev/ttyACM0'  # Change to your port
BAUD_RATE = 115200

# Open Serial
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

# Open Camera
cap = cv2.VideoCapture(0)  # 0 is default webcam

# Get screen resolution
monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

# Set a dynamic window size based on screen resolution
window_width = int(screen_width * 0.8)  # 80% of screen width
window_height = int(screen_height * 0.7)  # 70% of screen height

# Resize window to fit
cv2.namedWindow("HUD Display", cv2.WINDOW_NORMAL)
cv2.resizeWindow("HUD Display", window_width, window_height)

def draw_hud(frame, pitch, roll):
    h, w, _ = frame.shape
    center_x, center_y = w // 2, h // 2

    # Draw fixed airplane at center
    cv2.line(frame, (center_x - 40, center_y), (center_x + 40, center_y), (0, 255, 0), 2)
    cv2.line(frame, (center_x, center_y - 30), (center_x, center_y + 30), (0, 255, 0), 2)
    cv2.line(frame, (center_x - 20, center_y + 20), (center_x + 20, center_y + 20), (0, 255, 0), 2)

    # Draw roll arc
    for angle in [-90, -60, -30, 0, 30, 60, 90]:
        rad = np.deg2rad(angle - roll)
        radius = 150
        x = int(center_x + radius * np.sin(rad))
        y = int(center_y - radius * np.cos(rad))
        cv2.line(frame, (x-5, y), (x+5, y), (255, 255, 255), 2)

    # Draw pitch ladder
    pitch_scale = 5  # pixels per degree
    for p in range(-90, 91, 10):
        offset = int(pitch_scale * (p - pitch))
        if abs(offset) < h // 2:
            y = center_y + offset
            cv2.line(frame, (center_x - 30, y), (center_x + 30, y), (255, 255, 255), 2)
            cv2.putText(frame, f"{p:+}", (center_x + 40, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Draw digital readouts
    cv2.putText(frame, f"Pitch: {pitch:+.1f} deg", (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Roll: {roll:+.1f} deg", (w - 250, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return frame

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame from camera")
            break

        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            try:
                parts = line.split(',')
                if len(parts) == 2:
                    pitch = float(parts[0])
                    roll = float(parts[1])

                    # Draw HUD
                    hud_frame = draw_hud(frame.copy(), pitch, roll)

                    # Show it
                    cv2.imshow('HUD Display', hud_frame)

            except ValueError:
                print(f"Invalid serial data: {line}")

        # Exit with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
    cap.release()
    cv2.destroyAllWindows()
