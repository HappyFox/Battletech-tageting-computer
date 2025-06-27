import collections

import board
import busio
import displayio
import framebufferio
import rotaryio
import sharpdisplay
import terminalio

displayio.release_displays()

import adafruit_display_text
import adafruit_display_text.bitmap_label
from adafruit_display_shapes.line import Line
from adafruit_display_text.label import Label

spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)
# spi = busio.SPI(board.SCK, MOSI=board.MOSI)
framebuffer = sharpdisplay.SharpMemoryFramebuffer(spi, board.GP1, 400, 240)
display = framebufferio.FramebufferDisplay(framebuffer)

FONT = terminalio.FONT
BG_COLOR = 0xFFFFFF
FG_COLOR = 0

LEFT_PADDING = 5

COL_NAMES = ["G", "A", "T", "O", "R"]

Labels = collections.namedtuple("labels", ["gun", "atk", "tar", "other", "rng", "name"])


def cell_width():
    return display.width // len(COL_NAMES)


def setup():

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

    scale = 3

    labels = []

    for idx, name in enumerate(COL_NAMES):

        title_label = adafruit_display_text.bitmap_label.Label(
            FONT, text=name, scale=scale
        )
        title_label.color = FG_COLOR
        title_label.background_color = BG_COLOR
        title_label.anchor_point = (0.5, 1.0)
        height = display.height - cell_width() - padding
        title_label.anchored_position = (cell_width() * (idx + 0.5), height)
        display.root_group.append(title_label)

        label = adafruit_display_text.bitmap_label.Label(FONT, text="0", scale=scale)
        label.color = FG_COLOR
        label.background_color = BG_COLOR
        label.anchor_point = (0.5, 1.0)
        label.anchored_position = (cell_width() * (idx + 0.5), display.height - padding)
        display.root_group.append(label)
        labels.append(label)

    # Name
    name_label = adafruit_display_text.bitmap_label.Label(FONT, text="", scale=3)
    name_label.color = FG_COLOR
    name_label.background_color = BG_COLOR
    name_label.anchor_point = (0, 0)
    name_label.anchored_position = (LEFT_PADDING, 0)
    display.root_group.append(name_label)
    labels.append(name_label)

    display.root_group.append(
        Line(
            0,
            display.height - cell_width(),
            display.width,
            display.height - cell_width(),
            FG_COLOR,
        )
    )
    for idx in range(1, 5):
        line_x = cell_width() * idx
        display.root_group.append(
            Line(
                line_x,
                display.height - cell_width(),
                line_x,
                display.height,
                FG_COLOR,
            )
        )

    return Labels(*labels)


class WeaponsList:

    def __init__(self, weapons):
        self.weapons = weapons
        self.group = displayio.Group(x=LEFT_PADDING, y=cell_width())

        for weapon in weapons:
            self._add_weapon(weapon)

        self.group.hidden = True
        display.root_group.append(self.group)

    def _add_weapon(self, weapon):
        y_pos = 0
        for widget in self.group:
            _, _, _, height = widget.bounding_box
            _, y = widget.anchored_position
            wid_y = y + height
            print(f"wid_y: {wid_y}, height: {height}")
            if wid_y > y_pos:
                y_pos = wid_y + height
        print(f"Y_pos: {y_pos}")

        print(f"y_pos: {y_pos}")
        test_label = adafruit_display_text.bitmap_label.Label(
            FONT, text=weapon, scale=2
        )
        test_label.color = FG_COLOR
        test_label.background_color = BG_COLOR
        test_label.anchor_point = (0.0, 0.0)
        test_label.anchored_position = (LEFT_PADDING, y_pos)
        self.group.append(test_label)

    def activate(self):
        self.group.hidden = False

    def deactivate(self):
        self.group.hidden = True


def auto_refresh(enable):
    display.auto_refresh = enable


def refresh():
    display.refresh()
