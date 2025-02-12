import RPi.GPIO as GPIO
import time

# Define GPIO pin numbers for limit switches
LIMIT_SWITCH_LEFT_PIN = 21
LIMIT_SWITCH_RIGHT_PIN = 23
# Setup GPIO mode
GPIO.setmode(GPIO.BOARD)
# Setup GPIO pins for limit switches
GPIO.setup(LIMIT_SWITCH_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Left limit switch
GPIO.setup(LIMIT_SWITCH_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Right limit switch

for i in range(120):
    print(f"state: {GPIO.input(LIMIT_SWITCH_RIGHT_PIN)}")
    time.sleep(0.16)
GPIO.cleanup()



