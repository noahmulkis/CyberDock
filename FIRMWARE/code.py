print("Starting")
import board
import busio
import digitalio
import time
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.layers import Layers
import adafruit_ssd1306

# --- OLED Setup ---
i2c = busio.I2C(board.D5, board.D4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# --- Layer Names ---
LAYER_NAMES = ["Main", "Onshape", "Reaper"]
current_layer = 0

# --- Key Labels per layer ---
LAYER_LABELS = [
    [
        ["PREV", "NEXT", "PLAY", "LYR"],
        ["SNIP", "SHOW", "LOCK", "EMOJI"],
        ["RUN",  "TABS", "MUTE", "DESK"],
    ],
    [
        ["SKTCH", "EXVW", "FIT",  "LYR"],
        ["FRONT", "RGHT", "TOP",  "MATE"],
        ["ZOOM+", "ZOOM-","ROT",  "LYR"],
    ],
    [
        ["PLAY", "STOP", "REC",  "LYR"],
        ["MUTE", "SOLO", "LOOP", "QTSE"],
        ["ZM+",  "ZM-",  "TAP",  "LYR"],
    ],
]

# --- Key Actions per layer ---
LAYER_ACTIONS = [
    [
        "Prev Track", "Next Track", "Play/Pause", "Next Layer",
        "Snip", "Show Desktop", "Lock", "Emoji",
        "Run", "Task View", "Mute", "New Desktop",
    ],
    [
        "Sketch", "Exit View", "Fit All", "Next Layer",
        "Front View", "Right View", "Top View", "Mate",
        "Zoom In", "Zoom Out", "Rotate", "Next Layer",
    ],
    [
        "Play", "Stop", "Record", "Next Layer",
        "Mute Track", "Solo Track", "Toggle Loop", "Quantise",
        "Zoom In", "Zoom Out", "Tap Tempo", "Next Layer",
    ],
]

TIMEOUT = 1
DISPLAY_INTERVAL = 0.5

last_action_time = None
last_display_update = 0
pending_action = None
pending_is_volume = False
volume_direction = None

def draw_static():
    oled.fill(0)
    layer_label = LAYER_NAMES[current_layer]
    oled.text(layer_label, 0, 0, 1)
    oled.fill_rect(0, 9, 128, 1, 1)
    labels = LAYER_LABELS[current_layer]
    for row in range(3):
        for col in range(4):
            x = col * 32
            y = 11 + row * 7
            oled.text(labels[row][col], x, y, 1)
    oled.show()

def show_action(label):
    global last_action_time
    oled.fill(0)
    char_width = 12
    text_width = len(label) * char_width
    x = max(0, (128 - text_width) // 2)
    y = 8
    oled.text(label, x, y, 1, size=2)
    oled.show()
    last_action_time = time.monotonic()

def show_volume(direction):
    oled.fill(0)
    label = "Vol Up" if direction == "up" else "Vol Down"
    char_width = 12
    text_width = len(label) * char_width
    x = max(0, (128 - text_width) // 2)
    y = 8
    oled.text(label, x, y, 1, size=2)
    oled.show()

def show_layer_name(name):
    oled.fill(0)
    char_w = 12
    text_w = len(name) * char_w
    x = max(0, (128 - text_w) // 2)
    oled.text(name, x, 8, 1, size=2)
    oled.show()

draw_static()

# --- Keyboard Setup ---
keyboard = KMKKeyboard()
keyboard.col_pins = (board.D10, board.D9, board.D8, board.D7)
keyboard.row_pins = (board.D2, board.D1, board.D0)
keyboard.diode_orientation = DiodeOrientation.COL2ROW
keyboard.extensions.append(MediaKeys())

layers_mod = Layers()
keyboard.modules.append(layers_mod)

LYR_MAIN    = KC.TO(0)
LYR_ONSHAPE = KC.TO(1)
LYR_REAPER  = KC.TO(2)

keyboard.keymap = [
    # Layer 0 - Main
    [
        KC.MPRV,                    KC.MNXT,           KC.MPLY,                 LYR_ONSHAPE,
        KC.LGUI(KC.LSFT(KC.S)),     KC.LGUI(KC.D),     KC.LGUI(KC.L),           KC.LGUI(KC.DOT),
        KC.LGUI(KC.R),              KC.LGUI(KC.TAB),   KC.MUTE,                 KC.LCTL(KC.LGUI(KC.D)),
    ],
    # Layer 1 - Onshape
    [
        KC.S,                       KC.E,              KC.F,                    LYR_REAPER,
        KC.LCTL(KC.NUM_1),          KC.LCTL(KC.NUM_2), KC.LCTL(KC.NUM_3),       KC.M,
        KC.LCTL(KC.EQUAL),          KC.LCTL(KC.MINUS), KC.LCTL(KC.R),           LYR_REAPER,
    ],
    # Layer 2 - Reaper
    [
        KC.SPACE,                   KC.LCTL(KC.SPACE), KC.LCTL(KC.LSFT(KC.R)), LYR_MAIN,
        KC.F6,                      KC.F8,             KC.LCTL(KC.L),           KC.LCTL(KC.LSFT(KC.Q)),
        KC.LCTL(KC.EQUAL),          KC.LCTL(KC.MINUS), KC.LALT(KC.LSFT(KC.T)), LYR_MAIN,
    ],
]

# --- Encoder Setup ---
clk = digitalio.DigitalInOut(board.D3)
clk.direction = digitalio.Direction.INPUT
clk.pull = digitalio.Pull.UP

dt = digitalio.DigitalInOut(board.D6)
dt.direction = digitalio.Direction.INPUT
dt.pull = digitalio.Pull.UP

ENCODER_TABLE = {
    (1, 1, 0, 1): -1,
    (0, 1, 0, 0): -1,
    (0, 0, 1, 0): -1,
    (1, 0, 1, 1): -1,
    (1, 1, 1, 0): +1,
    (1, 0, 0, 0): +1,
    (0, 0, 0, 1): +1,
    (0, 1, 1, 1): +1,
}

last_clk = int(clk.value)
last_dt = int(dt.value)
accumulated = 0

_original_main_loop = keyboard._main_loop

def patched_main_loop():
    global last_clk, last_dt, accumulated
    global last_display_update, pending_action, last_action_time
    global pending_is_volume, volume_direction, current_layer

    now = time.monotonic()

    # --- Sync current_layer from KMK ---
    new_layer = keyboard.active_layers[0]
    if new_layer != current_layer:
        current_layer = new_layer
        show_layer_name(LAYER_NAMES[current_layer])
        last_action_time = now

    # --- Encoder ---
    cur_clk = int(clk.value)
    cur_dt = int(dt.value)
    state = (last_clk, last_dt, cur_clk, cur_dt)
    direction = ENCODER_TABLE.get(state, 0)
    if direction != 0:
        accumulated += direction
    last_clk = cur_clk
    last_dt = cur_dt

    if accumulated >= 2:
        if current_layer == 1:  # Onshape zoom in
            keyboard.tap_key(KC.LSFT(KC.Z))
            pending_action = "Zoom In"
            pending_is_volume = False
        else:
            keyboard.tap_key(KC.VOLU)
            pending_action = "Vol Up"
            pending_is_volume = True
            volume_direction = "up"
        accumulated = 0
    elif accumulated <= -2:
        if current_layer == 1:  # Onshape zoom out
            keyboard.tap_key(KC.Z)
            pending_action = "Zoom Out"
            pending_is_volume = False
        else:
            keyboard.tap_key(KC.VOLD)
            pending_action = "Vol Down"
            pending_is_volume = True
            volume_direction = "down"
        accumulated = 0

    # --- Key presses ---
    for key in keyboard.keys_pressed:
        try:
            idx = list(keyboard.keymap[current_layer]).index(key)
            action = LAYER_ACTIONS[current_layer][idx]
            if action != "Next Layer":
                pending_action = action
                pending_is_volume = False
        except (ValueError, IndexError):
            pass

    # --- Display update ---
    if now - last_display_update >= DISPLAY_INTERVAL:
        if pending_action is not None:
            if pending_is_volume:
                show_volume(volume_direction)
            else:
                show_action(pending_action)
            pending_action = None
            last_action_time = now
        elif last_action_time is not None and (now - last_action_time) > TIMEOUT:
            last_action_time = None
            draw_static()
        last_display_update = now

    return _original_main_loop()

keyboard._main_loop = patched_main_loop
keyboard.go()