import serial
import threading
import time

import pygame
import RPi.GPIO as gpio

# =====================================
# TF-Luna Configuration
# =====================================

PORT = "/dev/ttyUSB0" # Serial Port (sollte bei gleichem Aufbau gleich sein)

# NICHT VERÄNDERN!! liest den TF Luna aus

BAUD_RATE = 115200

CLIFF_THRESHOLD = 30      # cm
CLIFF_CONFIRMATIONS = 3   # consecutive readings
COOLDOWN = 0.5            # seconds

distance_cm = 9999
distance_timestamp = 0

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

# =====================================
# GPIO Setup (Verbindung zwischen Controller und PI)
# =====================================

IN1 = 17
IN2 = 22
IN3 = 23
IN4 = 24

ENA = 18
ENB = 19

gpio.setmode(gpio.BCM)

for pin in (IN1, IN2, IN3, IN4, ENA, ENB):
    gpio.setup(pin, gpio.OUT)

pwmA = gpio.PWM(ENA, 1000)
pwmB = gpio.PWM(ENB, 1000)

pwmA.start(0)
pwmB.start(0)

# =====================================
# TF-Luna Reader Thread (Liest den Luna immer wieder in einem eigenen Thread aus, um während der Steuerung lesen zu können)
# =====================================

def lidar_thread():
    global distance_cm
    global distance_timestamp

    while True:
        try:
            if ser.read() == b'\x59':
                if ser.read() == b'\x59':

                    frame = ser.read(7)

                    if len(frame) == 7:
                        distance_cm = frame[0] + frame[1] * 256
                        distance_timestamp = time.time()

        except Exception as e:
            print("LiDAR Error:", e)
            time.sleep(0.1)

# =====================================
# Motor Control
# =====================================

def set_motors(left_speed, right_speed):
    """
    Speed range:
    -100 to 100
    """

    # Left motor
    if left_speed > 0:
        gpio.output(IN1, True)
        gpio.output(IN2, False)

    elif left_speed < 0:
        gpio.output(IN1, False)
        gpio.output(IN2, True)
    else:
        gpio.output(IN1, False)
        gpio.output(IN2, False)

    # Right motor
    if right_speed > 0:
        gpio.output(IN3, False)
        gpio.output(IN4, True)
    elif right_speed < 0:
        gpio.output(IN3, True)
        gpio.output(IN4, False)
    else:
        gpio.output(IN3, False)
        gpio.output(IN4, False)

    pwmA.ChangeDutyCycle(min(abs(left_speed), 100))
    pwmB.ChangeDutyCycle(min(abs(right_speed), 100))


def stop():
    set_motors(0, 0)

# =====================================
# Controller Setup
# =====================================

pygame.init()
pygame.joystick.init()

# Jeder Bluetooth Controller sollte funktionieren, nicht getestet (sticks und bumper könnten untereinander vertauscht sein - Siehe "Controller Input" weiter unten)
# Getestet: Xbox Series S/X Controller mit bluetooth (standart ausstattung)

if pygame.joystick.get_count() == 0:
    raise Exception("No controller detected")

controller = pygame.joystick.Joystick(0)
controller.init()

print("Connected:", controller.get_name())

# =====================================
# Start LiDAR Thread
# =====================================

threading.Thread(
    target=lidar_thread,
    daemon=True
).start()

last_cliff_time = 0
cliff_count = 0

# =====================================
# Main Loop
# =====================================

try:

    while True:

        pygame.event.pump()

        now = time.time()

        # Ignore stale measurements
        reading_is_fresh = (
            now - distance_timestamp
        ) < 0.1

        # =================================
        # Cliff Detection
        # =================================

        if reading_is_fresh:

            if distance_cm > CLIFF_THRESHOLD:
                cliff_count += 1
            else:
                cliff_count = 0

        if (
            reading_is_fresh
            and cliff_count >= CLIFF_CONFIRMATIONS
            and (now - last_cliff_time) > COOLDOWN
        ):

            print(
                f"CLIFF DETECTED! Distance: {distance_cm} cm"
            )

            # Immediate reverse override
            set_motors(-55, -55)

            # Block controller
            time.sleep(0.5)

            stop()

            # Throw away buffered TF-Luna packets
            ser.reset_input_buffer()

            # Wait for fresh measurement
            old_timestamp = distance_timestamp

            timeout_start = time.time()

            while (
                distance_timestamp == old_timestamp
                and time.time() - timeout_start < 1
            ):
                time.sleep(0.005)

            cliff_count = 0
            last_cliff_time = time.time()

            continue

        # =================================
        # Controller Input
        # =================================

	# Setup der Achsen (sticks und bumper - hier kann die konfiguration geändert werden, für die gewünschten tasten)

        # Left stick horizontal
        steer = controller.get_axis(0)

        # Triggers
        left_trigger = (
            controller.get_axis(5) + 1
        ) / 2

        right_trigger = (
            controller.get_axis(4) + 1
        ) / 2

        # ---------------------------------
        # Rotate in place (tank steering)
        # ---------------------------------

        if abs(steer) > 0.20:

            turn_speed = abs(steer) * 65 # Faktor bestimmt geschwindigkeit (Limit 100)

            if steer > 0:
                # Rotate right
                set_motors(
                    -turn_speed,
                    turn_speed
                )

            else:
                # Rotate left
                set_motors(
                    turn_speed,
                    -turn_speed
                )

        # ---------------------------------
        # Forward
        # ---------------------------------

        elif right_trigger > 0.05:

            speed = right_trigger * 100 # Faktor bestimmt geschwindigkeit (Limit 100)
            print("FORWARD:", speed)
            set_motors(
                speed,
                speed
            )

        # ---------------------------------
        # Reverse
        # ---------------------------------

        elif left_trigger > 0.05:

            speed = left_trigger * 65 # Faktor bestimmt geschwindigkeit (Limit 100)
            print("REVERSE:", speed)

            set_motors(
                -speed,
                -speed
            )

        else:
            stop()

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nStopping...")

finally:

    stop()

    pwmA.stop()
    pwmB.stop()

    gpio.cleanup()

    pygame.quit()

    ser.close()