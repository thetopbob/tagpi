from evdev import InputDevice, categorize, ecodes

gamepad = InputDevice('/dev/input/event1')

# these codes are for the 8bitdo lite controller
# the d-pad codes are derived from a combination of code and value
# up and down are based on code 1, with up being value 0 and down being 65535
# left and right are code 0, with left being 0 and right being 65535
upBtn = 0
downBtn = 65535
rightBtn = 65535
leftBtn = 0
# the rest of the buttons are a simple numerical readout
aBtn = 305
bBtn = 304
xBtn = 307
yBtn = 306
r1Btn = 309
l1Btn = 308
startBtn = 311
selectBtn = 310
# r2 and l2 are on a different value, 1023, so they need to be nested as another if statement too
l2Btn = 2
r2Btn = 5

if __name__ == "__main__":
    print(f"Start pushing buttons on your {gamepad}")
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == yBtn:
                    print("Y")
                elif event.code == bBtn:
                    print("B")
                elif event.code == aBtn:
                    print("A")
                elif event.code == xBtn:
                    print("X")
                elif event.code == startBtn:
                    print("start")
                elif event.code == selectBtn:
                    print("select")
                elif event.code == l1Btn:
                    print("left bumper")
                elif event.code == r1Btn:
                    print("right bumper")
                elif event.code == l2Btn:
                    print("L2 button")
                elif event.code == r2Btn:
                    print("R2 Button")
        elif event.type == ecodes.EV_ABS:
            if event.code == 1:
                if event.value == upBtn:
                    print("up")
                elif event.value == downBtn:
                    print("down")
            elif event.code == 0:
                if event.value == leftBtn:
                    print("left")
                elif event.value == rightBtn:
                    print("right")
