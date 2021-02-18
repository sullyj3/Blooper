import time

from adafruit_circuitplayground import cp

# 4th octave. C4, D4, etc
PTCH_C = 261.63
PTCH_D = 293.67
PTCH_E = 329.63
PTCH_F = 349.23
PTCH_G = 392.0
PTCH_A = 440.0
PTCH_B = 493.88

# blue to pink gradient
colors = [
        (0,0,50),
        (0,55,67),
        (0,67,36),
        (18,67,0),
        (64,69,0),
        (50,0,0),
        (69,0,55)
        ]

BLACK = (0,0,0)

ALL_KEYS = ["A1", "A2", "A3", "A4", "A5", "A6", "TX"]

def arp():
    cp.play_tone(PTCH_C*2**0, 0.06)
    cp.play_tone(PTCH_G*2**0, 0.06)
    cp.play_tone(PTCH_D*2**1, 0.06)
    cp.play_tone(PTCH_A*2**1, 0.06)
    cp.play_tone(PTCH_E*2**2, 0.06)
    cp.play_tone(PTCH_B*2**2, 0.06)

key_note_map = {
        "A1": PTCH_C,
        "A2": PTCH_D,
        "A3": PTCH_E,
        "A4": PTCH_F,
        "A5": PTCH_G,
        "A6": PTCH_A,
        "TX": PTCH_B,
        }

# associate each key with (the index of its corresponding pixel, the index of the color in the colors array)
key_pixel_color_map = {
        "A1": (6,0),
        "A2": (7,1),
        "A3": (8,2),
        "A4": (1,3),
        "A5": (2,4),
        "A6": (3,5),
        "TX": (4,6),
        }

# stops any currently playing tone, starts the one associated with the key, and
# lights up the appropriate LED the right color
def trigger_note(key, octave_offset):
    cp.start_tone(key_note_map[key] * 2**octave_offset)
    cp.pixels.fill(BLACK)
    (pixel_ix, color_ix) = key_pixel_color_map[key]
    cp.pixels.fill(BLACK)
    cp.pixels[pixel_ix] = colors[color_ix]

def keyboard():
    arp()

    buttons = Buttons()
    octave_offset = 1

    # track which keys are currently pressed, and in what order they were
    # pressed (most recent is last in the list). This allows us to revert to
    # keys that are still being held when
    # a key is released.
    note_stack = []

    while True:
        buttons.update()

        for k in ALL_KEYS:
            if buttons.pressed[k]:
                note_stack.append(k)
                cp.stop_tone()
                trigger_note(k, octave_offset)

        for k in ALL_KEYS:
            if buttons.released[k]:
                # if we release the most recently pressed key, ie, the note currently playing,
                # we stop the tone and start the next most recently pressed note, if any
                if note_stack[-1] == k:
                    # switch off the LED
                    (pixel_ix,_) = key_pixel_color_map[k]
                    cp.pixels[pixel_ix] = BLACK

                    note_stack.pop()
                    cp.stop_tone()
                    if note_stack:
                        curr_key = note_stack[-1]
                        trigger_note(curr_key, octave_offset)
                else:
                    note_stack.remove(k)


'''Track when buttons are pressed and released

This is a substitute for an event system. Keeps track of when buttons are pressed or released.
You don't need this to know if the buttons are currently down, that's what cp.touch_A1 etc are for.

usage:

    buttons = Buttons()
    while True:
        buttons.update()
        if buttons.pressed["A1"]:
            # handle a1 pressed

        if buttons.released["A1"]:
            # handle a1 released
'''
class Buttons:
    def __init__(self):
        self.prev = {
            "A1": cp.touch_A1,
            "A2": cp.touch_A2,
            "A3": cp.touch_A3,
            "A4": cp.touch_A4,
            "A5": cp.touch_A5,
            "A6": cp.touch_A6,
            "TX": cp.touch_TX
            }

        self.pressed = {b:False for b in ALL_KEYS}
        self.released = {b:False for b in ALL_KEYS}

    def update(self):
        for b in self.pressed:
            self.pressed[b] = False
        for b in self.released:
            self.released[b] = False

        if not self.prev["A1"] and cp.touch_A1:
            self.pressed["A1"] = True
            self.prev["A1"] = True
        elif self.prev["A1"] and not cp.touch_A1:
            self.released["A1"] = True
            self.prev["A1"] = False

        if not self.prev["A2"] and cp.touch_A2:
            self.pressed["A2"] = True
            self.prev["A2"] = True
        elif self.prev["A2"] and not cp.touch_A2:
            self.released["A2"] = True
            self.prev["A2"] = False

        if not self.prev["A3"] and cp.touch_A3:
            self.pressed["A3"] = True
            self.prev["A3"] = True
        elif self.prev["A3"] and not cp.touch_A3:
            self.released["A3"] = True
            self.prev["A3"] = False

        if not self.prev["A4"] and cp.touch_A4:
            self.pressed["A4"] = True
            self.prev["A4"] = True
        elif self.prev["A4"] and not cp.touch_A4:
            self.released["A4"] = True
            self.prev["A4"] = False

        if not self.prev["A5"] and cp.touch_A5:
            self.pressed["A5"] = True
            self.prev["A5"] = True
        elif self.prev["A5"] and not cp.touch_A5:
            self.released["A5"] = True
            self.prev["A5"] = False

        if not self.prev["A6"] and cp.touch_A6:
            self.pressed["A6"] = True
            self.prev["A6"] = True
        elif self.prev["A6"] and not cp.touch_A6:
            self.released["A6"] = True
            self.prev["A6"] = False

        if not self.prev["TX"] and cp.touch_TX:
            self.pressed["TX"] = True
            self.prev["TX"] = True
        elif self.prev["TX"] and not cp.touch_TX:
            self.released["TX"] = True
            self.prev["TX"] = False


keyboard()
