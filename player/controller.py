import sys
from approxeng.input.selectbinder import ControllerResource
from time import sleep
import RPi.GPIO as GPIO
import threading
import logging

logging.basicConfig(
        filename='controller.log',
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Define what pins are required for the motors
MOTORAFWD=10
MOTORABK=9
MOTORBFWD=8
MOTORBBK=7
# Set initial duty cycle to 40 and frequency to 20
Frequency = 20
DutyCycleA = 40 #left motor is A
DutyCycleB = 40 #right motor is B
Stop = 0
RED=20
GREEN=21
BLUE=26
IR=22

GPIO.setup(MOTORAFWD, GPIO.OUT)
GPIO.setup(MOTORABK, GPIO.OUT)
GPIO.setup(MOTORBFWD, GPIO.OUT)
GPIO.setup(MOTORBBK, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.setup(IR, GPIO.OUT)
logging.debug("GPIO Pins mapped")

forwardLeft = GPIO.PWM(MOTORAFWD, Frequency)
reverseLeft = GPIO.PWM(MOTORABK, Frequency)
forwardRight = GPIO.PWM(MOTORBFWD, Frequency)
reverseRight = GPIO.PWM(MOTORBBK, Frequency)

forwardLeft.start(Stop)
reverseLeft.start(Stop)
forwardRight.start(Stop)
reverseRight.start(Stop)

class RobotStopException(Exception):
        pass

def LED(color,delay):
        logging.debug("Player pressed {}".format(LED))
        LED_thread=threading.Thread(target=LED_func,args=[color,delay])
        LED_thread.daemon=True
        LED_thread.start()

def LED_func(color,delay):
        GPIO.output(color,GPIO.HIGH)
        sleep(delay)
        GPIO.output(color,GPIO.LOW)

def motor_stop():
	forwardLeft.ChangeDutyCycle(Stop)
	forwardRight.ChangeDutyCycle(Stop)
	reverseLeft.ChangeDutyCycle(Stop)
	reverseRight.ChangeDutyCycle(Stop)

def motor_forward(delay):
	forwardLeft.ChangeDutyCycle(DutyCycleA)
	forwardRight.ChangeDutyCycle(DutyCycleB)
	reverseLeft.ChangeDutyCycle(Stop)
	reverseRight.ChangeDutyCycle(Stop)
	sleep(delay)
	motor_stop()

def spin_right(delay):
	forwardLeft.ChangeDutyCycle(Stop)
	forwardRight.ChangeDutyCycle(DutyCycleB)
	reverseLeft.ChangeDutyCycle(DutyCycleA)
	reverseRight.ChangeDutyCycle(Stop)
	sleep(delay)
	motor_stop()

def spin_left(delay):
	forwardLeft.ChangeDutyCycle(DutyCycleA)
	forwardRight.ChangeDutyCycle(Stop)
	reverseLeft.ChangeDutyCycle(Stop)
	reverseRight.ChangeDutyCycle(DutyCycleB)
	sleep(delay)
	motor_stop()

def motor_reverse(delay):
	forwardLeft.ChangeDutyCycle(Stop)
	forwardRight.ChangeDutyCycle(Stop)
	reverseLeft.ChangeDutyCycle(DutyCycleA)
	reverseRight.ChangeDutyCycle(DutyCycleB)
	sleep(delay)
	motor_stop()

while True:
        try:
                with ControllerResource() as joystick:
                        print('Found a joystick and connected')
                        logging.debug("Found a joystick and connected")
                        while joystick.connected:
                                ddown_held, dup_held, dleft_held, dright_held = joystick['ddown','dup','dleft','dright']
                                if dup_held is not None:
                                        motor_forward(dup_held)
                                if ddown_held is not None:
                                        motor_reverse(ddown_held)
                                if dleft_held is not None:
                                        spin_left(dleft_held)
                                if dright_held is not None:
                                        spin_right(dright_held)
                                joystick.check_presses()
                                if joystick.presses.circle:
                                        LED(GREEN,0.5)
                                if joystick.presses.cross:
                                        LED(RED,0.5)
                                if joystick.presses.square:
                                        LED(BLUE,0.5)
                                if joystick.presses.r2:
                                        motor_stop()
                                if joystick.presses.r1:
                                        LED(IR,0.5)
                                if joystick.presses.start:
                                        raise RobotStopException()
        # Joystick disconnected..
                                #print('Connection to joystick lost')
        except IOError:
        # No joystick found, wait for a bit before trying again
                print('Unable to find any joysticks. Trying again in 5 seconds..')
                logging.error("Cannot find a joystick")
                sleep(5.0)

        except RobotStopException:
                motor_stop()
                logging.debug("Player exited the app")
                print("Exiting...")
                GPIO.cleanup()
                sys.exit()
