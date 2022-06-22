"""
Helper:
https://github.com/NVIDIA/jetson-gpio
https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
Push button is set on Pin 11, GPIO 50

We want our program to read a low state when the button is not pushed
and a high state when the button is pushed.
"""

import Jetson.GPIO as GPIO


class Button:

    def __init__(self):
        self.pins = [11]
        GPIO.getmode()
        GPIO.setmode(mode)
        self.callback_fn = callback_fn
        # Set pin to be an input pin and set initial value to be pulled low (off)
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        event_detected()

    def callback_fn(self):
        # Read the value of a channel: (should be GPIO.LOW as set in the init)
        value = GPIO.input(self.pins)
        print("callback called from channel %s" % self.pins)
        print("value of button is %s" % value)

    def event_detected(self):
        GPIO.add_event_detect(self.pins, GPIO.RISING)
        if GPIO.event_detected(self.pins):
            print('button pressed !')
        # add rising edge detection
        GPIO.add_event_detect(self.pins, GPIO.RISING, callback=self.callback_fn)
        # Set the default state for pin
        GPIO.cleanup(self.pins)


# Initialization
channel = 11
mode = GPIO.getmode()
GPIO.setmode(mode)
# Set pin 11 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def callback_fn(channel):
    print("callback called from channel %s" % channel)


def event_detected():
    # Read the value of a channel: (should be GPIO.LOW as set in the init)
    GPIO.input(channel)
    GPIO.add_event_detect(channel, GPIO.RISING)
    if GPIO.event_detected(channel):
        print('button pressed !')
    # add rising edge detection
    GPIO.add_event_detect(channel, GPIO.RISING, callback=callback_fn)
    # Set the default state for pin
    GPIO.cleanup(channel)


# With this function, we continuously read the state of the button, it will output the print many times.
def read_state():
    while True:
        if GPIO.input(channel) == GPIO.HIGH:
            print("Button was pushed !")


if __name__ == '__main__':
    event_detected()
    b = Button()

