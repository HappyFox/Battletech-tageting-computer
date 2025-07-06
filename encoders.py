import board
import digitalio
import rotaryio

from events import EventDispatcher

PICO_ENC_PINS = [
    (board.GP5, board.GP6, board.GP7),
    (board.GP8, board.GP9, board.GP10),
    (board.GP11, board.GP12, board.GP13),
    (board.GP27, board.GP26, board.GP22),
    (board.GP21, board.GP20, board.GP19),
    (board.GP18, board.GP17, board.GP16),
]


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
