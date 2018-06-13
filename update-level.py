#!/usr/bin/python
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

# Domoticz settings
DOMOTICZ_HOST = "domoticz"
DOMOTICZ_DEVICE_IDX = 705  # Fill in your Domoticz device ID
DOMOTICZ_URL = "http://%s:8080" % DOMOTICZ_HOST

# Select which GPIOs you will use
GPIO_TRIGGER = 24
GPIO_ECHO = 23


def main():
    # Setup Raspberry's GPIO's
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
    GPIO.setup(GPIO_ECHO,GPIO.IN)

    # Set TRIGGER to LOW and pause
    GPIO.output(GPIO_TRIGGER, False)
    time.sleep(0.5)

    # Send 10 microsecond ultrasonic wave with TRIGGER
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    while GPIO.input(GPIO_ECHO) == 0:
        pass

    # Measure time it took for the wave to come back on ECHO
    start = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()
    measuredTime = stop - start

    # Calculate the travel distance by multiplying the measured time by speed of sound
    distanceBothWays = measuredTime * 33112 # cm/s in 20 degrees Celsius
    distance = distanceBothWays / 2

    GPIO.cleanup()

    # Update device in Domoticz
    url = "%s/json.htm?type=command&param=udevice&idx=%d&nvalue=0&svalue=%.1f" % \
          (DOMOTICZ_URL, DOMOTICZ_DEVICE_IDX, distance)
    resp = requests.get(url)
    print(resp.text)

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
