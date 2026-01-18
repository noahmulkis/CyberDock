print("Starting")

import board
import time
import random


from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.oled import OLED
from kmk.extensions.oled import OLED, OLEDDisplay


keyboard = KMKKeyboard()

# Encoder
encoder = EncoderHandler()
keyboard.modules.append(encoder)

encoder.pins = (
    (board.D3, board.D6),  # Encoder 1
)

encoder.map = [
    (KC.VOLD, KC.VOLU),  # CCW, CW
]

# Keyboard Matrix
keyboard.col_pins = (board.D10, board.D11, board.D12, board.D13)
keyboard.row_pins = (board.D2, board.D1, board.D0)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# Keymap
keyboard.keymap = [
    [KC.A, KC.B, KC.C, KC.D,
     KC.E, KC.F, KC.G, KC.H,
     KC.I, KC.J, KC.K, KC.L]
]

# OLED
oled = OLED(
    width=128,
    height=32,
    flip=False,
)

# Matrix rain parameters
COLS = 21   # characters per line (128px)
ROWS = 4    # lines (32px)
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# One drop position per column
drops = [random.randint(0, ROWS - 1) for _ in range(COLS)]
last_update = 0
RAIN_SPEED_MS = 120  # lower = faster

def matrix_rain():
    global last_update

    now = time.ticks_ms()
    if time.ticks_diff(now, last_update) > RAIN_SPEED_MS:
        for i in range(COLS):
            if random.random() > 0.7:
                drops[i] = (drops[i] + 1) % ROWS
        last_update = now

    # Build screen buffer
    lines = [""] * ROWS
    for col in range(COLS):
        for row in range(ROWS):
            if row == drops[col]:
                lines[row] += random.choice(CHARS)
            else:
                lines[row] += " "

    return lines

oled.display = OLEDDisplay(
    oled,
    matrix_rain,
)



keyboard.extensions.append(oled)

#END
if __name__ == '__main__':
    keyboard.go()
