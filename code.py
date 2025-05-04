import collections
import time

import alarm
import board
import digitalio
import displayio
import neopixel
import terminalio

# from adafruit_display_text import label

ThrowDescription = collections.namedtuple("ThrowDescription", ["pin", "value"])

test_switch_des = [
    ThrowDescription(board.D22, 0),
    ThrowDescription(board.D23, 1),
    ThrowDescription(board.D24, 2),
    ThrowDescription(board.D25, 3),
    ThrowDescription(board.D26, 4),
]


class MultiSwitch:

    def __init__(self, throw_descs):
        self.pins = []
        for desc in throw_descs:
            dig_pin = digitalio.DigitalInOut(desc.pin)
            dig_pin.switch_to_input()
            dig_pin.pull = digitalio.Pull.UP
            self.pins.append(ThrowDescription(dig_pin, desc.value))

    def get_value(self):
        for pin in self.pins:
            if not pin.pin.value:
                return pin.value


np = neopixel.NeoPixel(board.NEOPIXEL, 1)

np[0] = (50, 50, 50)
time.sleep(1)
np[0] = (0, 0, 0)

# ms = MultiSwitch(test_switch_des)


# time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 20)

pin = digitalio.DigitalInOut(board.A0)
pin.deinit()
print("BOOYA")
pin_alarm = alarm.pin.PinAlarm(pin=board.D22, value=False, pull=True)
alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
