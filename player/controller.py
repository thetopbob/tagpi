from approxeng.input.selectbinder import ControllerResource
from time import sleep
import RPi.GPIO as GPIO

def circlepress():
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
	print "ALL LEDs on"
	GPIO.output(20,GPIO.HIGH)
	GPIO.output(21,GPIO.HIGH)
	GPIO.output(26,GPIO.HIGH)
	GPIO.output(22,GPIO.HIGH)

def squarepress():
	print "ALL LEDs off"
	GPIO.output(20,GPIO.LOW)
	GPIO.output(21,GPIO.LOW)
	GPIO.output(26,GPIO.LOW)
	GPIO.output(22,GPIO.LOW)

while True:
        try:
                with ControllerResource() as joystick:
                        print('Found a joystick and connected')
                        #print(joystick.controls)
                        while joystick.connected:
                                joystick.check_presses()
                                if joystick.has_presses:
                                        print(joystick.presses)
                                if joystick.presses.circle:
                                        circlepress()
                                if joystick.presses_square:
																				squarepress()
        # Joystick disconnected..
                                #print('Connection to joystick lost')
        except IOError:
        # No joystick found, wait for a bit before trying again
                print('Unable to find any joysticks')
                sleep(1.0)
