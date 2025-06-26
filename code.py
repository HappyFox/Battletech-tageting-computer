import collections
import time

import board
import busio
import displayio
import framebufferio
import rotaryio
import sharpdisplay
import terminalio

import display

PICO_ENC_PINS = [
    (board.GP5, board.GP6),
    (board.GP8, board.GP9),
    (board.GP11, board.GP12),
    (board.GP27, board.GP26),
    (board.GP21, board.GP20),
    (board.GP18, board.GP17),
]


Labels = collections.namedtuple(
    "labels", ["gun", "atk", "tar", "other", "rng", "result"]
)


def setup_encoders():

    pins = PICO_ENC_PINS
    encoders = []

    for pin in pins:
        enc = EventEncoder(rotaryio.IncrementalEncoder(pin[0], pin[1]))
        encoders.append(enc)

    return encoders


class EventDispatcher:

    def __init__(self):
        self.callback_fns = set()

    def dispatch_event(self, *args, **kwargs):
        for fn in self.callback_fns:
            fn(*args, **kwargs)

    def register_fn(self, fn):
        self.callback_fns.add(fn)

    def remove_fn(self, fn):
        self.callback_fns.remove(fn)


class EventEncoder(EventDispatcher):

    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        self.current_pos = encoder.position

    def update(self):
        diff = self.encoder.position - self.current_pos
        self.current_pos = self.encoder.position
        if diff != 0:
            self.dispatch_event(diff)


class Entry(EventDispatcher):

    def __init__(self, label, encoder):
        super().__init__()
        self.value = 0
        self.label = label
        self.encoder = encoder
        self.encoder.register_fn(self.on_update)

    def on_update(self, diff):
        self.value = max(self.value + diff, 0)
        self.label.text = str(self.value)
        print(self.callback_fns)
        self.dispatch_event()


class ToHitHandler:

    def __init__(self, label, entrys):
        self.label = label
        self.entrys = entrys
        for entry in entrys:
            entry.register_fn(self.on_update)

    def on_update(self):
        to_hit = 0
        for entry in self.entrys:
            to_hit += entry.value
        print(f"updating to {to_hit}")
        self.label.text = str(to_hit)


def main():
    encs = setup_encoders()
    labels = Labels(*display.setup())

    entrys = [
        Entry(labels.gun, encs[0]),
        Entry(labels.atk, encs[1]),
        Entry(labels.tar, encs[2]),
        Entry(labels.other, encs[3]),
        Entry(labels.rng, encs[4]),
    ]

    to_hit = ToHitHandler(labels.result, entrys)

    print("Done!")
    while True:
        for enc in encs:
            enc.update()


main()
