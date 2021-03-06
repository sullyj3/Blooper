import time

from adafruit_circuitplayground import cp

# 4th octave. C4, D4, etc
PITCH_C = 261.63
PITCH_D = 293.67
PITCH_E = 329.63
PITCH_F = 349.23
PITCH_G = 392.0
PITCH_A = 440.0
PITCH_B = 493.88

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
BLUE = (0,0,50)
GREEN = (0,20,0)

ALL_BUTTONS = ["A1", "A2", "A3", "A4", "A5", "A6", "TX", "BTN_A", "BTN_B"]
ALL_KEYS = ["A1", "A2", "A3", "A4", "A5", "A6", "TX"]

def arp():
    cp.play_tone(PITCH_C*2**0, 0.06)
    cp.play_tone(PITCH_G*2**0, 0.06)
    cp.play_tone(PITCH_D*2**1, 0.06)
    cp.play_tone(PITCH_A*2**1, 0.06)
    cp.play_tone(PITCH_E*2**2, 0.06)
    cp.play_tone(PITCH_B*2**2, 0.06)

key_note_map = {
        "A1": PITCH_C,
        "A2": PITCH_D,
        "A3": PITCH_E,
        "A4": PITCH_F,
        "A5": PITCH_G,
        "A6": PITCH_A,
        "TX": PITCH_B,
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

def degree_to_key_octave(degree: int) -> (str, int):
    key = ALL_KEYS[(degree - 1) % len(ALL_KEYS)]
    octave = (degree-1) // len(ALL_KEYS)
    return (key, octave)

# stops any currently playing tone, starts the one associated with the key, and
# lights up the appropriate LED the right color
def trigger_note(key, octave_offset):
    cp.start_tone(key_note_map[key] * 2**octave_offset)
    cp.pixels.fill(BLACK)
    (pixel_ix, color_ix) = key_pixel_color_map[key]
    cp.pixels.fill(BLACK)
    cp.pixels[pixel_ix] = colors[color_ix]

def trigger_degree(degree):
    (key,octave) = degree_to_key_octave(degree)
    cp.start_tone(key_note_map[key] * 2**octave)

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

        for k in ALL_BUTTONS:
            if buttons.pressed[k]:
                note_stack.append(k)
                cp.stop_tone()
                trigger_note(k, octave_offset)

        for k in ALL_BUTTONS:
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

# possibly we should remove the callback stuff and let users just check
# self.state? Fuck around and find out
class Pulse:
    def __init__(self, on_interval, off_interval=None):
        self.on_interval = on_interval
        self.off_interval = off_interval if off_interval is not None else on_interval

        self.subscribers = {}

        self.state = None
        self.next_toggle = None

    def start(self):
        now = time.monotonic()
        self.state = True
        self.next_toggle = now + self.on_interval

    def update(self):
        now = time.monotonic()
        if now >= self.next_toggle:
            self.state = not self.state
            self.next_toggle = now + (self.on_interval if self.state else self.off_interval)

        self.notify_subscribers()

    def notify_subscribers(self):
        for callback in self.subscribers.values():
            callback(self.state)

    def subscribe(self, key, f):
        if key in self.subscribers:
            print(f"warning, ovewriting subscriber {key}")

        self.subscribers[key] = f

    def unsubscribe(self, key):
        del self.subscribers[key]



class Sequencer:
    # todo think of a better name than epoch
    def __init__(self, epoch_length=1):
        self.playing = False
        self.note_on = False
        self.next_epoch = None
        self.epoch_length = epoch_length

        self.sequence = [8,8,12,8,10,8,9,8] + [8,8,8,8,8,8,8,8] + [8,8,12,8,10,8,9,9] + [9,9,9,10,9,8,6,5]
        self.playhead = 0

        #between 0 and 7 inclusive
        # used in editing mode
        self.editor_selected_step = 0

    def tick_playhead(self):
        now = time.monotonic()
        if now >= self.next_epoch:
            self.next_note()
            self.next_epoch += self.epoch_length

    def start_note(self, key="A1", octave=0):
        trigger_note(key, octave)
        self.note_on = True

    def stop_note(self):
        cp.stop_tone()
        self.note_on = False


    def toggle_note(self):
        if self.note_on:
            self.stop_note()
        else:
            self.start_note()

    # start the next note in the sequence and advance the playhead
    def next_note(self):
        self.stop_note()
        next_degree = self.sequence[self.playhead]
        (key,octave) = degree_to_key_octave(next_degree)
        self.start_note(key, octave)

        # todo: can probably use itertools.cycle to avoid index issues
        self.playhead = (self.playhead + 1) % len(self.sequence)

    def play(self):
        self.playing = True
        now = time.monotonic()
        self.playhead = 0
        self.next_epoch = now

    def stop(self):
        self.stop_note()
        cp.pixels.fill(BLACK)
        self.playing = False

    def update(self, buttons):
        if self.playing:
            self.tick_playhead()


class Editor:
    def __init__(self):
        self.selected_step = 0
        self.sequence = [8,8,12,8,10,8,9,8]

        self.bottom_blinker = Pulse(0.5)
        self.selected_blinker = Pulse(0.1)

        def blink_blue(b):
            color = BLUE if b else BLACK
            cp.pixels[0] = color
            cp.pixels[9] = color

        def blink_selected(b):
            color = GREEN if b else BLACK
            pixel_index = sequence_led_indices[self.selected_step]
            cp.pixels[pixel_index] = color

        self.bottom_blinker.subscribe("blink blue", blink_blue)
        self.selected_blinker.subscribe("blink selected", blink_selected)

    def start(self):
        self.bottom_blinker.start()
        self.selected_blinker.start()


    # called by main loop
    def update(self, buttons):

        
        #A3 and A4 are left and right
        if buttons.pressed["A3"]:
            pixel_index = sequence_led_indices[self.selected_step]
            cp.pixels[pixel_index] = BLACK
            self.selected_step = (self.selected_step - 1) % 8

            trigger_degree(self.sequence[self.selected_step])
            self.selected_blinker.start()
            # TODO schedule note off instead of sleeping
            time.sleep(0.1)
            cp.stop_tone()

        if buttons.pressed["A4"]:
            pixel_index = sequence_led_indices[self.selected_step]
            cp.pixels[pixel_index] = BLACK
            self.selected_step = (self.selected_step + 1) % 8

            trigger_degree(self.sequence[self.selected_step])
            self.selected_blinker.start()
            # TODO schedule note off instead of sleeping
            time.sleep(0.1)
            cp.stop_tone()

        self.bottom_blinker.update()
        self.selected_blinker.update()

# We have 8 steps in our sequence (for now?). Each of those steps is
# represented by the pixel at the given index blinking
sequence_led_indices = {
    # if step 0 is selected, pixel 5 blinks, etc
    0:5,
    1:6,
    2:7,
    3:8,
    4:1,
    5:2,
    6:3,
    7:4,
    }

def main():
    EDITOR = 0
    PLAYING = 1

    buttons = Buttons()
    sequencer = Sequencer(0.2)
    editor = Editor()

    state = EDITOR
    editor.start()

    while True:
        buttons.update()

        # handle state transitions
        if buttons.pressed["BTN_A"]:
            if state == EDITOR:
                sequencer.play()
                state = PLAYING
            elif state == PLAYING:
                sequencer.stop()
                editor.start()
                state = EDITOR
        
        # handle active state
        if state == EDITOR:
            editor.update(buttons)
        elif state == PLAYING:
            sequencer.update(buttons)



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
        # prev essentially tracks the down state of each button, lagging by one
        # update call.
        # So for example, if a button was `up` last update call, but is `down`
        # now, that means the button must have been pressed in the intervening time
        self.prev = {
            "A1": cp.touch_A1,
            "A2": cp.touch_A2,
            "A3": cp.touch_A3,
            "A4": cp.touch_A4,
            "A5": cp.touch_A5,
            "A6": cp.touch_A6,
            "TX": cp.touch_TX,
            "BTN_A" : cp.button_a,
            "BTN_B" : cp.button_b
            }

        self.pressed = {b:False for b in ALL_BUTTONS}
        self.released = {b:False for b in ALL_BUTTONS}

    # Determine which buttons were pressed or released in the time since the last update call
    # sets the state of self.pressed or self.released, which are then available for inspection
    def update(self):
        # Clear the events that happened last time
        for b in self.pressed:
            self.pressed[b] = False
        for b in self.released:
            self.released[b] = False

        # check whether each button was pressed or released since last time
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

        if not self.prev["BTN_A"] and cp.button_a:
            self.pressed["BTN_A"] = True
            self.prev["BTN_A"] = True
        elif self.prev["BTN_A"] and not cp.button_a:
            self.released["BTN_A"] = True
            self.prev["BTN_A"] = False

        if not self.prev["BTN_B"] and cp.button_b:
            self.pressed["BTN_B"] = True
            self.prev["BTN_B"] = True
        elif self.prev["BTN_B"] and not cp.button_b:
            self.released["BTN_B"] = True
            self.prev["BTN_B"] = False

if __name__ == '__main__':
    main()
