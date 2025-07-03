import gc
import time

import board
import digitalio
import rotaryio

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
                return True
            self.pressed.dispatch_event(diff)
            return True
        return False


def main():
    encs = setup_encoders()
    display.auto_refresh(False)
    labels = display.setup()

    mech_widgets = [
        mechs.Mech(
            "Notos Prime",
            "Clan",
            ["Medium Pulse Laser"],
            encs,
            labels,
            target_comp=True,
            gunnery=3,
        ),
        mechs.Mech(
            "Ballius Prime",
            "Clan",
            ["ER Large Laser", "Medium Pulse Laser", "Flamer"],
            encs,
            labels,
            gunnery=3,
        ),
        mechs.Mech(
            "Athena",
            "Clan",
            ["HAG 30", "ER Medium Laser", "AP Gauss Rifle"],
            encs,
            labels,
            gunnery=3,
            target_comp=True,
        ),
    ]

    ms = mechs.MechSwitcher(encs[0], mech_widgets)

    display.refresh()
    last_update = time.monotonic()
    need_gc = False
    while True:
        updated = False
        for enc in encs:
            if enc.update():
                updated = True

        # if need_refresh[0]:
        if updated:
            display.refresh()
            last_update = time.monotonic()
            need_gc = True

        if need_gc:
            since_update = time.monotonic() - last_update
            if since_update > 1:
                print(gc.mem_free())
                gc.collect()
                print(gc.mem_free())
                last_update = time.monotonic()
                need_gc = False


main()
