import collections

import display
from events import EventDispatcher

Entrys = collections.namedtuple("Entrys", ["gun", "atk", "tar", "other", "rng"])


class Entry(EventDispatcher):

    def __init__(self, label, encoder, on_pressed=False):
        super().__init__()
        self.value = 0
        self.label = label
        self.encoder = encoder
        self.on_pressed = on_pressed

    def activate(self):
        if self.on_pressed:
            self.encoder.pressed.register_fn(self.on_update)
        else:
            self.encoder.register_fn(self.on_update)
        self.label.text = str(self.value)

    def deactivate(self):
        if self.on_pressed:
            self.encoder.pressed.deregister_fn(self.on_update)
            return
        self.encoder.deregister_fn(self.on_update)

    def on_update(self, diff):
        self.value = max(self.value + diff, 0)
        self.label.text = str(self.value)
        print(self.callback_fns)
        self.dispatch_event()


class Mech:

    def __init__(self, name, weapons, encoders, labels):
        self.name = name
        self.encoders = encoders
        self.labels = labels

        self.entrys = Entrys(
            Entry(labels.gun, encoders[0], on_pressed=True),
            Entry(labels.atk, encoders[1]),
            Entry(labels.tar, encoders[2]),
            Entry(labels.other, encoders[3]),
            Entry(labels.rng, encoders[4]),
        )
        self.weapons = display.WeaponsList(weapons)

    def activate(self):
        self.labels.name.text = self.name
        for entry in self.entrys:
            entry.activate()
        self.weapons.activate()

    def deactivate(self):
        for entry in self.entrys:
            entry.deactivate()
        self.weapons.deactivate()


class MechSwitcher:

    def __init__(self, enc, mechs=None):
        self.enc = enc
        self.enc.register_fn(self.on_update)

        self.mechs = mechs
        self.active_idx = 0
        self.mechs[0].activate()

    def on_update(self, diff):
        self.mechs[self.active_idx].deactivate()
        self.active_idx = (self.active_idx + diff) % len(self.mechs)
        self.mechs[self.active_idx].activate()
