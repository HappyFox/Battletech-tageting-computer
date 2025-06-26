import board
import busio
import displayio
import framebufferio
import rotaryio
import sharpdisplay
import terminalio

displayio.release_displays()

from adafruit_display_shapes.line import Line
from adafruit_display_text.label import Label

spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)
# spi = busio.SPI(board.SCK, MOSI=board.MOSI)
framebuffer = sharpdisplay.SharpMemoryFramebuffer(spi, board.GP1, 400, 240)
display = framebufferio.FramebufferDisplay(framebuffer)

FONT = terminalio.FONT
BG_COLOR = 0xFFFFFF
FG_COLOR = 0


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
    result_label = Label(FONT, text="0", scale=3)
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
