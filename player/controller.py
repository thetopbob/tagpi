from evdev import InputDevice, categorize, ecodes, AbsInfo
from time import sleep
from threading import Thread
import time
import queue

gamepad = InputDevice('/dev/input/event1')

# these codes are for the 8bitdo lite controller
# the d-pad codes are derived from a combination of code and value:
# up and down are based on code 1, when up pressed the value starts at 0 (pressed) and on release is 32768
# down starts as 65535 and reverts to 32768 on release. Lets assume that 32768 becomes the "neutral" value for
# the Y-axis and build on that.
# Simlarly for the x-axis, left and right are code 0, with left being 0 
# and right being 65535

# Dictionary of buttons
controller_input = {305:'BTN_A', 306:'BTC_C', 307:'BTN_X', 304:'BTN_B', 309:'BTN_Z', 'ABS_X':0, 'ABS_Y':0}

upBtn = 0
downBtn = 65535
yaxisNeutral = 32768
rightBtn = 65535
leftBtn = 0
xaxisNeutral = 32768
# the rest of the buttons are a simple numerical readout
aBtn = 305
bBtn = 304
xBtn = 307
yBtn = 306
r1Btn = 309
l1Btn = 308
startBtn = 311
selectBtn = 310
# r2 and l2 are recorded as EV_ABS and on a different value, 1023
l2Btn = 2
r2Btn = 5

currentBtn = 0

def gamepad_update():
    events = gamepad.read_loop()
    return_code = 'No Match'
    for event in events:
        codename = event.value
        print(f"Codename is {codename}")
        event_test = controller_input.get(codename, 'No Match')
        print(f"Event_test is {event_test}")
        if event_test != 'No Match':
            controller_input[codename] = event.value
            return_code = codename
        else:
            return_code = 'No Match'
    
    return return_code

def drive_control():
    print("I am driving")

def fire_weapon():
    print("I am firing")

def reload_weapon():
    print("I am reloading")

def main():
    print(f"Start pushing buttons on your {gamepad}")
    while 1:
        control_code = gamepad_update()
        print(f"Control_code is {control_code}")
        if control_code == 'ABS_X' or control_code =='ABS_Y':
            drive_control()
        elif control_code == '304':
            fire_weapon()
        elif control_code == '306':
            reload_weapon()


def old_code():
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
        
        elif event.type == ecodes.EV_ABS:
            if event.code == 1:
                if event.value == 0:
                    currentBtn = "up"
                    while True:
                        for event in gamepad.read_loop():
                            if event.type == ecodes.EV_ABS:
                                if event.code == 32768:
                                    print(f"{currentBtn} released")
                                else:
                                    print(f"{currentBtn} pushed")
                elif event.value == 65535:
                    currentBtn = "down"
                    while True:
                        print(f"{currentBtn}")
                elif event.value == 32768:
                    print(f"{currentBtn} released")
                    currentBtn = 0
                    
            elif event.code == 0:
                if event.value == 0:
                    while event.value != 32768:
                        print("left")
                        if event.value == 32768:
                            print("left released")
                elif event.value == 65535:
                    while event.value !=32768:
                        print("right")
                        if event.value == 32768:
                            print("left released")
            
            elif event.value == 1023:
                if event.code == l2Btn:
                    print("L2 button")
                elif event.code == r2Btn:
                    print("R2 button")


if __name__ == "__main__":
    main()
