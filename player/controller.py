from evdev import InputDevice, categorize, ecodes

gamepad = InputDevice('/dev/input/event3')

# these codes are for the 8bitdo lite controller
upBtn = 
downBtn = 
rightBtn = 
leftBtn = 
aBtn = 304
bBtn = 305
xBtn = 307
yBtn = 308
r1Btn = 311
l1Btn = 310
startBtn = 
selectBtn = 

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

            elif event.code == upBtn:
                print("up")
            elif event.code == downBtn:
                print("down")
            elif event.code == leftBtn:
                print("left")
            elif event.code == rightBtn:
                print("right")

            elif event.code == startBtn:
                print("start")
            elif event.code == selectBtn:
                print("select")

            elif event.code == l1Btn:
                print("left bumper")
            elif event.code == r1Btn:
                print("right bumper")
