import collections
import time

import board
import busio
import digitalio
import displayio
import framebufferio
import rotaryio
import sharpdisplay
import terminalio

import display
import mechs
from events import EventDispatcher

PICO_ENC_PINS = [
    (board.GP5, board.GP6, board.GP7),
    (board.GP8, board.GP9, board.GP10),
    (board.GP11, board.GP12, board.GP13),
    (board.GP27, board.GP26, board.GP22),
    (board.GP21, board.GP20, board.GP19),
    (board.GP18, board.GP17, board.GP16),
]


def setup_encoders():

    pins = PICO_ENC_PINS
    encoders = []

    for a_pin, b_pin, button_pin in pins:
        button = digitalio.DigitalInOut(button_pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP
        enc = EventEncoder(rotaryio.IncrementalEncoder(a_pin, b_pin), button)
        encoders.append(enc)

    return encoders


class EventEncoder(EventDispatcher):

    def __init__(self, encoder, push_button):
        super().__init__()
        self.encoder = encoder
        self.current_pos = encoder.position
        self.push_button = push_button

        self.pressed = EventDispatcher()

    def update(self):
        diff = self.encoder.position - self.current_pos
        self.current_pos = self.encoder.position
        if diff != 0:
            if self.push_button.value:
                self.dispatch_event(diff)
                return
            self.pressed.dispatch_event(diff)


def main():
    encs = setup_encoders()
    display.auto_refresh(False)
    labels = display.setup()

    mech_widgets = [
        mechs.Mech("Urban Mech", ["LRM 55", "LB-X 10", "M Laser"], encs, labels),
        mechs.Mech("Locust", ["ER PPC", "AC-20", "Large Laser"], encs, labels),
    ]

    ms = mechs.MechSwitcher(encs[0], mech_widgets)

    need_refresh = [False]

    def do_refresh():
        need_refresh[0] = True

    for enc in encs:
        enc.register_fn(lambda x: do_refresh())
        enc.pressed.register_fn(lambda x: do_refresh())

    display.refresh()
    while True:
        for enc in encs:
            enc.update()

        if need_refresh[0]:
            print("refresh")
            display.refresh()
            need_refresh[0] = False


main()
