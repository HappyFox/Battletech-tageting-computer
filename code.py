import time

import board
import busio
import displayio
import framebufferio
import rotaryio
import sharpdisplay
import terminalio
from adafruit_display_shapes.line import Line
from adafruit_display_text.label import Label

displayio.release_displays()


spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)
# spi = busio.SPI(board.SCK, MOSI=board.MOSI)
framebuffer = sharpdisplay.SharpMemoryFramebuffer(spi, board.GP1, 400, 240)
display = framebufferio.FramebufferDisplay(framebuffer)

FONT = terminalio.FONT
BG_COLOR = 0xFFFFFF
FG_COLOR = 0


"""
GRAND_CENTERAL_ENC_PINS = [
    (board.D0, board.D1),
    (board.D3, board.D4),
    (board.D5, board.D6),
    (board.D7, board.D8),
    (board.D11, board.D12),
    (board.D15, board.D16),
    (board.D27, board.D28),
    (board.D37, board.D38),
]"""

PICO_ENC_PINS = [
    (board.GP5, board.GP6),
    (board.GP8, board.GP9),
    (board.GP11, board.GP12),
    (board.GP27, board.GP26),
    (board.GP21, board.GP20),
    (board.GP18, board.GP17),
]


def setup_encoders():

    pins = PICO_ENC_PINS
    encoders = []

    for pin in pins:
        enc = rotaryio.IncrementalEncoder(pin[0], pin[1])
        encoders.append(enc)

    return encoders


def setup_display():

    print("TESTING")

    display.rotation = 90

    bg_bitmap = displayio.Bitmap(display.width, display.height, 1)
    bg_bitmap.fill(0)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = BG_COLOR
    bg_tile_grid = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)

    group = displayio.Group()
    display.root_group = group
    display.root_group.append(bg_tile_grid)

    padding = 10
    col_names = ["G", "A", "T", "O", "R"]
    cell_width = display.width // len(col_names)
    scale = 3

    labels = []

    for idx, name in enumerate(col_names):

        title_label = Label(FONT, text=name, scale=scale)
        title_label.color = FG_COLOR
        title_label.background_color = BG_COLOR
        title_label.anchor_point = (0.5, 1.0)
        height = display.height - cell_width - padding
        title_label.anchored_position = (cell_width * (idx + 0.5), height)
        display.root_group.append(title_label)

        label = Label(FONT, text="0", scale=scale)
        label.color = FG_COLOR
        label.background_color = BG_COLOR
        label.anchor_point = (0.5, 1.0)
        label.anchored_position = (cell_width * (idx + 0.5), display.height - padding)
        display.root_group.append(label)
        labels.append(label)

    # Result label
    result_label = Label(FONT, text="0", scale=4)
    result_label.color = FG_COLOR
    result_label.background_color = BG_COLOR
    result_label.anchor_point = (0.5, 0.5)
    height = (display.height - (cell_width * 2)) // 2
    result_label.anchored_position = (display.width // 2, height)
    display.root_group.append(result_label)
    labels.append(result_label)

    display.root_group.append(
        Line(
            0,
            display.height - cell_width,
            display.width,
            display.height - cell_width,
            FG_COLOR,
        )
    )
    for idx in range(1, 5):
        line_x = cell_width * idx
        display.root_group.append(
            Line(
                line_x,
                display.height - cell_width,
                line_x,
                display.height,
                FG_COLOR,
            )
        )

    return labels


class Entry:

    def __init__(self, label, encoder):
        self.value = 0
        self.label = label
        self.encoder = encoder

    def update(self):
        self.label.text = str(self.encoder.position)
        self.value = self.encoder.position


def main():

    enc = setup_encoders()
    gun_label, atk_label, tar_label, other_label, rng_label, result_label = (
        setup_display()
    )

    entrys = [
        Entry(gun_label, enc[0]),
        Entry(atk_label, enc[1]),
        Entry(tar_label, enc[2]),
        Entry(other_label, enc[3]),
        Entry(rng_label, enc[4]),
    ]

    print("Done!")
    while True:
        to_hit = 0
        for entry in entrys:
            entry.update()
            to_hit = to_hit + entry.value
        result_label.text = str(to_hit)


main()
