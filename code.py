import time

from adafruit_circuitplayground import cp

PTCH_C = 261.63
PTCH_D = 293.67
PTCH_E = 329.63
PTCH_F = 349.23
PTCH_G = 392.0
PTCH_A = 440.0
PTCH_B = 493.88

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

octve_scalar = 2


def arp():
    cp.play_tone(PTCH_C*2**0, 0.06)
    cp.play_tone(PTCH_G*2**0, 0.06)
    cp.play_tone(PTCH_D*2**1, 0.06)
    cp.play_tone(PTCH_A*2**1, 0.06)
    cp.play_tone(PTCH_E*2**2, 0.06)
    cp.play_tone(PTCH_B*2**2, 0.06)

def keyboard():
    arp()


    buttons = Buttons()

    octve_scalar = 2

    time.sleep(1)
    while True:
        buttons.update()

        any_pressed = any((cp.touch_A1, cp.touch_A2, cp.touch_A3, cp.touch_A4,
            cp.touch_A5, cp.touch_A6, cp.touch_TX))

        if buttons.pressed["A1"]:
            cp.stop_tone()
            cp.start_tone(PTCH_C * octve_scalar)
            cp.pixels[6] = colors[0]
        elif buttons.released["A1"] and not any_pressed:
            cp.stop_tone()
            cp.pixels[6] = BLACK

        if buttons.pressed["A2"]:
            cp.stop_tone()
            cp.start_tone(PTCH_D * octve_scalar)
            cp.pixels[7] = colors[1]
        elif buttons.released["A2"] and not any_pressed:
            cp.stop_tone()
            cp.pixels[7] = BLACK

        if buttons.pressed["A3"]:
            cp.stop_tone()
            cp.start_tone(PTCH_E * octve_scalar)
            cp.pixels[8] = colors[2]
        elif buttons.released["A3"] and not any_pressed:
            cp.stop_tone()
            cp.pixels[8] = BLACK

        if buttons.pressed["A4"]:
            cp.stop_tone()
            cp.start_tone(PTCH_F * octve_scalar)
            cp.pixels[1] = colors[3]
        elif buttons.released["A4"] and not any_pressed:
            cp.stop_tone()
            cp.pixels[1] = BLACK

        if buttons.pressed["A5"]:
            cp.stop_tone()
            cp.start_tone(PTCH_G * octve_scalar)
            cp.pixels[2] = colors[4]
        elif buttons.released["A5"] and not any_pressed:
            cp.stop_tone()
            cp.pixels[2] = BLACK

        if buttons.pressed["A6"]:
            cp.stop_tone()
            cp.start_tone(PTCH_A * octve_scalar)
            cp.pixels[3] = colors[5]
        elif buttons.released["A6"] and not any_pressed:
            cp.stop_tone()
            cp.pixels[3] = BLACK

        if buttons.pressed["TX"]:
            cp.stop_tone()
            cp.start_tone(PTCH_B * octve_scalar)
            cp.pixels[4] = colors[6]
        elif buttons.released["TX"] and not any_pressed:
            cp.stop_tone()
            cp.pixels[4] = BLACK


class Buttons:
    def __init__(self):
        buttons = ["A1", "A2", "A3", "A4", "A5", "A6", "TX"]
        self.prev = {
            "A1": cp.touch_A1,
            "A2": cp.touch_A2,
            "A3": cp.touch_A3,
            "A4": cp.touch_A4,
            "A5": cp.touch_A5,
            "A6": cp.touch_A6,
            "TX": cp.touch_TX
            }
        self.pressed = {b:False for b in buttons}
        self.released = {b:False for b in buttons}

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

#chord()
