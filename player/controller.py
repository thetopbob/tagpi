import sys
from approxeng.input.selectbinder import ControllerResource
from time import sleep
import RPi.GPIO as GPIO
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Define what pins are required for the motors
MOTORAFWD=23
MOTORABK=24
MOTORAPWM=12
MOTORBFWD=19
MOTORBBK=16
MOTORBPWM=13
# Initialise objects for H-Bridge PWM pins
# Set initial duty cycle to 0 and frequency to 1000
Frequency = 20
DutyCycleA = 40
DutyCycleB = 40
Stop = 0
RED=20
GREEN=21
BLUE=26

GPIO.setup(MOTORAFWD, GPIO.OUT)
GPIO.setup(MOTORABK, GPIO.OUT)
GPIO.setup(MOTORAPWM, GPIO.OUT)
GPIO.setup(MOTORBFWD, GPIO.OUT)
GPIO.setup(MOTORBBK, GPIO.OUT)
GPIO.setup(MOTORBPWM, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)


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
        GPIO.output(MOTORAPWM,GPIO.LOW)
        GPIO.output(MOTORBPWM,GPIO.LOW)
        print('I stopped')

def motor_forward():
        GPIO.output(MOTORAPWM,GPIO.HIGH)
        GPIO.output(MOTORBPWM,GPIO.HIGH)
        forwardLeft.ChangeDutyCycle(Stop)
        forwardRight.ChangeDutyCycle(DutyCycleA)
        reverseLeft.ChangeDutyCycle(Stop)
        reverseRight.ChangeDutyCycle(DutyCycleA)
        print('I went forward')
        GPIO.output(MOTORAPWM,GPIO.LOW)
        GPIO.output(MOTORBPWM,GPIO.LOW)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

def spin_right():
        forwardLeft.ChangeDutyCycle(Stop)
        forwardRight.ChangeDutyCycle(Stop)
        reverseLeft.ChangeDutyCycle(DutyCycleB)
        reverseRight.ChangeDutyCycle(DutyCycleA)

def spin_left():
        forwardLeft.ChangeDutyCycle(Stop)
        forwardRight.ChangeDutyCycle(DutyCycleA)
        reverseLeft.ChangeDutyCycle(DutyCycleB)
        reverseRight.ChangeDutyCycle(Stop)

def reverseDrive():
        forwardLeft.ChangeDutyCycle(Stop)
        forwardRight.ChangeDutyCycle(Stop)
        reverseLeft.ChangeDutyCycle(DutyCycleB)
        reverseRight.ChangeDutyCycle(DutyCycleA)
        print('I went back')

while True:
        try:
                with ControllerResource() as joystick:
                        print('Found a joystick and connected')
                        print(joystick.controls)
                        while joystick.connected:
                                ddown_held, dup_held, dleft_held, dright_held, circle_held, cross_held = joystick['ddown','dup','dleft','dright','circle','cross']
                                if dup_held is not None:
                                        #print(f'Up button held for {dup_held:.2f} seconds')
                                        motor_forward()
                                if ddown_held is not None:
                                        #print(f'Down button held for {ddown_held:.2f} seconds')
                                        reverseDrive()
                                if dleft_held is not None:
                                        spin_left()
                                if dright_held is not None:
                                        spin_left()
                                if circle_held is not None:
                                        LED(RED, circle_held)
                                if cross_held is not None:
                                        LED(GREEN, cross_held)
                                joystick.check_presses()
                                if joystick.has_presses:
                                        print(joystick.presses)
                                if 'start' in joystick.presses:
                                        raise RobotStopException()
                                if 'square' in joystick.presses:
                                        motor_stop()
        # Joystick disconnected..
                                #print('Connection to joystick lost')
        except IOError:
        # No joystick found, wait for a bit before trying again
                print('Unable to find any joysticks. Trying again in 5 seconds..')
                sleep(5.0)

        except RobotStopException:
                motor_stop()
                print("Exiting...")
                GPIO.cleanup()
                sys.exit()