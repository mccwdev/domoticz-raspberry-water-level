#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Monitor tank water level with a Rapsberry Pi, Domoticz and a JSN-SR04T ultra-sonic distance sensor
#    © 2017 - David Bambušek
#    © 2018 - Lennart Jongeneel
#

# Import required Python libraries
import time               # library for time reading time
import RPi.GPIO as GPIO   # library to control Rpi GPIOs
import requests
import statistics


# Domoticz settings
DOMOTICZ_HOST = "domoticz"
DOMOTICZ_DEVICE_IDX = 705  # Fill in your Domoticz device ID
DOMOTICZ_URL = "http://%s:8080" % DOMOTICZ_HOST

# Select which GPIOs you will use
GPIO_TRIGGER = 24
GPIO_ECHO = 23

NUMBER_OF_MEASUREMENTS = 5
MIN_VALUE = 0
MAX_VALUE = 110


def distance_measure():
    # Setup Raspberry's GPIO's
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    try:
        # Set TRIGGER to LOW and pause
        GPIO.output(GPIO_TRIGGER, False)
        time.sleep(0.5)

        # Send 10 microsecond ultrasonic wave with TRIGGER
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)
        start = time.time()
        while GPIO.input(GPIO_ECHO) == 0:
            if time.time() - start > 20:
                raise IOError("Timeout. No trigger send / received")
            pass

        # Measure time it took for the wave to come back on ECHO
        start = time.time()
        measuredTime = 0
        while GPIO.input(GPIO_ECHO) == 1:
            stop = time.time()
            measuredTime = stop - start
            if measuredTime > 10:
                raise IOError("Timeout. No response from device")
        if not measuredTime or  measuredTime < 0:
            raise ValueError("Invalid measured time: %d" % measuredTime)

        # Calculate the travel distance by multiplying the measured time by speed of sound
        distanceBothWays = measuredTime * 33112  # cm/s in 20 degrees Celsius
        distance = distanceBothWays / 2
    finally:
        GPIO.cleanup()
    return distance


def main():
    # Do three measurements and take the median result
    measurements = []
    for _ in range(NUMBER_OF_MEASUREMENTS):
        d = distance_measure()
        if MIN_VALUE < d < MAX_VALUE:
            measurements.append(d)
    distance = statistics.median(measurements)

    # Update device in Domoticz
    url = "%s/json.htm?type=command&param=udevice&idx=%d&nvalue=0&svalue=%.1f" % \
          (DOMOTICZ_URL, DOMOTICZ_DEVICE_IDX, distance)
    resp = requests.get(url)
    print(resp.text)


# Run the main function when the script is executed
if __name__ == "__main__":
    main()
