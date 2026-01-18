"""
KMK Firmware for Open Source Macro Pad
Hardware: XIAO RP2040
Features: 11-key matrix + 1 Encoder Switch, Rotary Encoder, SSD1306 OLED
"""

import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.encoder import EncoderHandler
from kmk.modules.layers import Layers
from kmk.extensions.display import Display, TextEntry
from kmk.extensions.display.ssd1306 import SSD1306
from kmk.handlers.sequences import send_string

# Initialize the keyboard
keyboard = KMKKeyboard()

# --- 1. MODULES & EXTENSIONS ---
# Layers allow for multiple functions per key
layers = Layers()
keyboard.modules.append(layers)

# Encoder handler for the rotary knob
encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)

# --- 2. MATRIX CONFIGURATION ---
# Based on the schematic provided:
# Rows (Outputs): Row 0 (GP28), Row 1 (GP27), Row 2 (GP26)
# Columns (Inputs): Col 0 (GP29), Col 1 (GP6), Col 2 (GP7), Col 3 (GP1)
# Diode Orientation: COL2ROW (Diodes point from Column to Row)
keyboard.row_pins = (board.GP28, board.GP27, board.GP26)
keyboard.col_pins = (board.GP29, board.GP6, board.GP7, board.GP1)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# --- 3. ROTARY ENCODER CONFIGURATION ---
# Encoder Pins: A (GP0), B (GP7)
# Note: GP7 is shared with Column 2 in the schematic. 
# In a real build, this might cause interference unless handled in hardware.
encoder_handler.pins = (
    (board.GP0, board.GP7, None, False), # (Pin A, Pin B, Button Pin, Reverse)
)

# --- 4. OLED DISPLAY CONFIGURATION ---
# OLED Pins: SDA (GP6), SCL (GP7)
# Note: GP6 is shared with Col 1, GP7 is shared with Col 2 and Encoder B.
# This setup suggests the matrix might be scanned while I2C is inactive, 
# or the schematic implies a specific multi-purpose pin usage.
i2c = board.I2C() # Uses default SDA (GP6) and SCL (GP7) on XIAO RP2040
display_driver = SSD1306(
    i2c=i2c,
    device_address=0x3C,
)

display_extension = Display(
    display_driver=display_driver,
    width=128,
    height=32, # Standard 0.91" OLED height
    entries=[
        TextEntry(text='Manus Macro', x=0, y=0),
        TextEntry(text='Layer: 0', x=0, y=12),
    ],
)
keyboard.extensions.append(display_extension)

# --- 5. KEYMAPS & MACROS ---
# The matrix is 3x4. SW4 is the encoder's push button.
# Layer 0: Media & Navigation
# Layer 1: Productivity Macros
keyboard.keymap = [
    # Layer 0: Default
    [
        KC.MPRV, KC.MPLY, KC.MNXT, KC.MUTE,   # Row 0: Prev, Play/Pause, Next, [Encoder Click: Mute]
        KC.LCTL(KC.C), KC.LCTL(KC.V), KC.LCTL(KC.Z), KC.MO(1), # Row 1: Copy, Paste, Undo, [Layer 1 Switch]
        KC.LEFT, KC.DOWN, KC.UP, KC.RGHT,     # Row 2: Arrow Keys
    ],
    # Layer 1: Macros
    [
        KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS,   # Row 0
        send_string("https://manus.im"), KC.TRNS, KC.TRNS, KC.TRNS, # Row 1: Macro to type URL
        KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS,   # Row 2
    ]
]

# --- 6. ENCODER BEHAVIOR ---
# Define what the knob does on each layer
encoder_handler.map = [
    ((KC.VOLU, KC.VOLD),), # Layer 0: Volume Up / Volume Down
    ((KC.WH_U, KC.WH_D),), # Layer 1: Mouse Wheel Up / Down
]

# --- 7. START KEYBOARD ---
if __name__ == '__main__':
    keyboard.go()
