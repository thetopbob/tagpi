#!/usr/bin/python3

# Future development: change the client parameter to prompt on join to the server
# so that players join and press a button to confirm their slot
# i.e. circle = player 1, cross = player 2, etc. For now this has been built out as args.
#CLIENT='1' #each player needs to have a different CLIENT number. 1,2,3,etc,
# Future development: change this so that it is stored in a variables file on the local device.
# For the the moment the IP address will be fixed, but this should be flexible. For now this has been built out as args.
#LTSERVER='192.168.1.161' #insert IP address of server computer

#---------------------
#BUZZER:    	GPIO5
#IR_TX:     	GPIO22
#IR_RX      	GPIO18         Notes for wiring
#RED:       	GPIO20
#GREEN:     	GPIO21
#BLUE:      	GPIO26
#I2C_SDA:   	GPIO2
#I2C_SCL:   	GPIO3
#MOTOR_A_FWD:	GPIO10
#MOTOR_A_BK:	GPIO9
#MOTOR_B_FWD:	GPIO8
#MOTOR_B_BK:	GPIO7
#---------------------
import paho.mqtt.client as mqtt
from os import _exit
from sys import exit
from time import sleep
from random import randint
import threading
import ast
import lirc
from py_irsend import irsend
from subprocess import call
from datetime import datetime
from approxeng.input.selectbinder import ControllerResource
import RPi.GPIO as GPIO
import ltsounds
import argparse

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
RED=20
GREEN=21
BLUE=26
# Define what pins are required for the motors
MOTORAFWD=10
MOTORABK=9
MOTORBFWD=8
MOTORBBK=7
# Initialise objects for H-Bridge PWM pins
# Set initial duty cycle to 0 and frequency to 1000
Frequency = 20
DutyCycleA = 30
DutyCycleB = 30
Stop = 0

# Variables required for the game start
newgame='waiting'
game_wait=3
connected=False

GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.setup(MOTORAFWD, GPIO.OUT)
GPIO.setup(MOTORABK, GPIO.OUT)
GPIO.setup(MOTORBFWD, GPIO.OUT)
GPIO.setup(MOTORBBK, GPIO.OUT)

forwardLeft = GPIO.PWM(MOTORAFWD, Frequency)
reverseLeft = GPIO.PWM(MOTORABK, Frequency)
forwardRight = GPIO.PWM(MOTORBFWD, Frequency)
reverseRight = GPIO.PWM(MOTORBBK, Frequency)

forwardLeft.start(Stop)
reverseLeft.start(Stop)
forwardRight.start(Stop)
reverseRight.start(Stop)

def onConnect(client,userdata,flags,rc):
	if(rc==0): print("Connected")
	client.subscribe([('game/players',0),('game/players/'+CLIENT,0)])
	print("Waiting for other players...")
	LED_waiting(10)

def onMessage(client,userdata,message):
	global game_in_progress,gvars_dict,newgame
	if(len(message.payload)==1):
		tag_given()
	elif(message.payload.decode()=='start game'):
		print("Server has started the game")
		game_in_progress=True
	elif(message.payload.decode()=='game over'):
		player.publish('game/ltserver',str(stats))
		print("Server has ended the game")
		game_in_progress=False
		sleep(5)
		sound('endgame')
		sleep(2)
	elif(message.payload.decode()=='dead'):
		print("You got a kill!")
	elif(message.payload.decode()=='message from server'):
		print("message!")
	elif(message.payload.decode()=='you hit them'):
		tag_given()
	elif(message.payload.decode()=='next'):
		newgame='next'
	elif(message.payload.decode()=='exit'):
		newgame='exit'
	elif(message.payload.decode()[0:8]=="Starting"):
		print(message.payload.decode())
	else:
		gvars_dict=ast.literal_eval(message.payload.decode())

def onDisconnect(client,userdata,message):
	player.unsubscribe('game/players')
	player.unsubscribe('game/ltserver')
	player.unsubscribe('game/players/'+CLIENT)
	player.loop_stop()
	LED_func(RED,0.5)
	sleep(0.5)
	LED_func(RED,0.5)
	sleep(0.5)
	GPIO.cleanup()
	print("Disconnected from broker")
	_exit(0)

"""
-------------------------------------------------------------
inserted the following to help debug MQTT events
-------------------------------------------------------------
"""
def onLog(client, userdata, level, buf):
    print("log: ",buf)
"""
-------------------------------------------------------------
"""

def sound(event):
	sound_thread=threading.Thread(target=sound_func,args=[event])
	sound_thread.daemon=True
	sound_thread.start()

def sound_func(event):
	#1 = LaserSound,2 = Not used,3 = Start Game
	#4 = Dead Tune,5 = Not used,6 = Error,7 = You got hit
	#8 = You hit them,9 = End Game,10 = Reloading
	if(event=='shoot'):
		sound_class.play(1)
	elif(event=='tag_received'):
		sound_class.play(7)
	elif(event=='tag_given'):
		sound_class.play(8)
	elif(event=='error'):
		sound_class.play(6)
	elif(event=='dead'):
		sound_class.play(4)
	elif(event=='begingame'):
		sound_class.play(3)
	elif(event=='endgame'):
		sound_class.play(9)
	elif(event=='reloading'):
		sound_class.play(10)
	else:
		pass

def LED(color,delay):
	LED_thread=threading.Thread(target=LED_func,args=[color,delay])
	LED_thread.daemon=True
	LED_thread.start()

def LED_func(color,delay):
	GPIO.output(color,GPIO.HIGH) 
	sleep(delay)
	GPIO.output(color,GPIO.LOW) 

def LED_waiting(delay):
	for color in [GREEN,BLUE,RED]:
		GPIO.output(color,GPIO.HIGH)
		sleep(delay)
		GPIO.output(color,GPIO.LOW)

def shoot():
    global maxDeaths, stats
    if(stats['health']==0 or stats['deaths']>maxDeaths):
        sound('error')
    elif(stats['ammo']==0):
        LED(BLUE,1)
    elif(stats['ammo']>=1):
        irsend.send_once('ltag', [gvars_dict['game_mode']+CLIENT]) #Use the py_irsend module to send a specific IR code based on the client value and the game mode
        stats['shots_fired']+=1
        stats['ammo']-=1
        print("shot fired") #uncommented this line so that we can check logs when shooting 
        sound('shoot')
        LED(GREEN,0.3)

def tag_received(code):
	global stats
	player.publish('game/ltserver',CLIENT) # tell server I  was tagged
	from_player=code[-3:-2] # who was the tagger
	print("Received tag from player"+ str(from_player))
	return_topic='game/players/'+str(from_player) # who to reply to
	player.publish(return_topic,CLIENT) # reply to tagger
	tag_location=randint(0,len(stats['tags_received'])-1) # show where i was tagged for the post-game. currently random 
	tmp=list(stats['tags_received'])[tag_location]
	stats['tags_received'][tmp]+=1
	stats['health']-=1
	if(stats['health']<=0):
		dead(return_topic)
	else:
		sound('tag_received')
		LED(RED,1)

def tag_given():
    global stats
    print("You tagged another player")
    tag_location=randint(0,len(stats['tags_given'])-1) #random sensor - this needs to be updated to pick up if sensor 1 or 2
    tmp=list(stats['tags_given'])[tag_location]
    stats['tags_given'][tmp]+=1
    stats['kills']+=1
    sound('tag_given')
    LED(BLUE,1)

def player_reload():
	global stats,game_in_progress
	if(stats['health']<=0):
		sound('error')
	else:
		sound('reloading')
		stats['ammo'] = maxAmmo
		LED(GREEN,0.5)
		print("Reload complete") # added for logging purposes

def dead(return_topic):
    global stats,game_in_progress
    game_in_progress=False
    stats['deaths']+=1
    if(int(gvars_dict['num_players_dead'])!=int(gvars_dict['num_players'])-1):
        sound('dead')
        LED(RED,3)
    sleep(1)
    player.publish(return_topic,'dead')

def motor_stop():
	forwardLeft.ChangeDutyCycle(Stop)
	forwardRight.ChangeDutyCycle(Stop)
	reverseLeft.ChangeDutyCycle(Stop)
	reverseRight.ChangeDutyCycle(Stop)

def motor_forward():
	forwardLeft.ChangeDutyCycle(DutyCycleA)
	forwardRight.ChangeDutyCycle(DutyCycleB)
	reverseLeft.ChangeDutyCycle(Stop)
	reverseRight.ChangeDutyCycle(Stop)

def spin_right():
	forwardLeft.ChangeDutyCycle(DutyCycleA)
	forwardRight.ChangeDutyCycle(Stop)
	reverseLeft.ChangeDutyCycle(Stop)
	reverseRight.ChangeDutyCycle(DutyCycleA)

def spin_left():
	forwardLeft.ChangeDutyCycle(Stop)
	forwardRight.ChangeDutyCycle(DutyCycleB)
	reverseLeft.ChangeDutyCycle(DutyCycleA)
	reverseRight.ChangeDutyCycle(Stop)

def motor_reverse():
	forwardLeft.ChangeDutyCycle(Stop)
	forwardRight.ChangeDutyCycle(Stop)
	reverseLeft.ChangeDutyCycle(DutyCycleA)
	reverseRight.ChangeDutyCycle(DutyCycleB)

def initialize(game_mode,end_type,end_value): #the game modes,Classic,Soldier,Tank,Sniper,GunGame,LaserMaster are init with
	global maxAmmo             #maxHealth,maxAmmo,maxDeaths,and waitTime(time to shoot the next shot)
	global maxHealth           #and either timed or life count number.
	global maxDeaths
	global waitTime
	global stats
	global game_wait

	if(game_mode=='Classic'):
		maxAmmo = 10
		if(end_type!='Time'):
			maxHealth = end_value
		else:
			maxHealth = 10000
		maxDeaths = 1
		stats['health'] = maxHealth
		stats['ammo'] = maxAmmo
		waitTime = 0.3
		message = "    Classic     "

	if(game_mode=='Showdown'):
		maxAmmo = 10
		if(end_type!='Time'):
			maxHealth = end_value
		else:
			maxHealth = 10000
		maxDeaths = 1
		stats['health'] = maxHealth
		stats['ammo'] = maxAmmo
		waitTime = 0.3
		message = "    Showdown    "

	elif(game_mode=='Soldier'):
		maxHealth = 12
		maxAmmo = 10
		if(end_type!='Time'):
			maxDeaths = end_value
		else:
			maxDeaths = 100000
		stats['health'] = maxHealth
		stats['ammo'] = maxAmmo
		waitTime = 0.1
		message = "   Overwatch    "

	elif(game_mode=='Tank'):
		maxHealth = 20
		maxAmmo = 25
		if(end_type!='Time'):
			maxDeaths = end_value
		else:
			maxDeaths = 100000
		stats['health'] = maxHealth
		stats['ammo'] = maxAmmo
		waitTime = 0.01
		message = "   Overwatch    "

	elif(game_mode=='Sniper'):
		maxHealth = 10
		maxAmmo = 1
		if(end_type!='Time'):
			maxDeaths = end_value
		else:
			maxDeaths = 100000
		stats['health'] = maxHealth
		stats['ammo'] = maxAmmo
		waitTime = 1.0
		message = "   Overwatch    "

	elif(game_mode=='GunGame'):
		maxHealth = 1
		maxAmmo = 1
		if(end_type!='Time'):
			maxDeaths = end_value
		else:
			maxDeaths = 100000
		stats['health'] = maxHealth
		stats['ammo'] = maxAmmo
		waitTime = 3.0
		message = "    Gun Game    "

	elif(game_mode=='LaserMaster'):
		maxHealth = 7
		maxAmmo = 7
		if(end_type!='Time'):
			maxDeaths = end_value
		else:
			maxDeaths = 100000
		stats['health'] = maxHealth
		stats['ammo'] = maxAmmo
		waitTime = 2.0
		message = "  Laser Master  "

	sleep(2)

	for i in range(game_wait,-1,-1):
		if(i==2):
			sound('begingame')
		sleep(1)

		
#----------------------------------------------------------
#                        MAIN
#----------------------------------------------------------
try:
	parser = argparse.ArgumentParser()
	parser.add_argument('--playerid', help='player number',	default='1', choices=['1','2','3'])
	parser.add_argument('--server', help='IP address of the game server', default='192.168.1.161')

	args = parser.parse_args()

	CLIENT=args.playerid
	LTSERVER=args.server

	player=mqtt.Client(client_id=CLIENT,clean_session=True)
	player.on_connect=onConnect
	player.on_message=onMessage
	player.on_disconnect=onDisconnect
	player.on_log=onLog
	sound_class = ltsounds.Buzzer()
	sockid=lirc.init("ltag",blocking=False)
	game_in_progress=False

	while not connected:
		try:
			player.connect(LTSERVER,keepalive=60,bind_address="")
			connected=True
		except ConnectionRefusedError:
			print('LTServer must be started first...')
			LED_waiting(0.3)
			#sleep(1)
	connected=False

	while True:
		stats=dict(player=CLIENT,shots_fired=0,kills=0,deaths=0,health=0,ammo=0,tags_given=dict(rhull=0,lhull=0),tags_received=dict(rhull=0,lhull=0))
		player.loop_start()
		player.publish('game/ltserver','ready')

		while not game_in_progress:
			pass #wait for start game message

		initialize(gvars_dict['game_mode'],gvars_dict['end_type'],int(gvars_dict['end_value']))

		while game_in_progress:
			sleep(0.1)
			print('Game Starting!')
			try:
				code=lirc.nextcode()
				if code:
					tag_received(str(code))		
				with ControllerResource() as joystick:
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
							player_reload()
						if joystick.presses.cross:
							shoot()
						if joystick.presses.square:
							shoot()
						if joystick.presses.r2:
							shoot()
						if joystick.presses.r1:
							shoot()
			
			except IOError:
			# No joystick found, wait for a bit before trying again
				print('Unable to find any joysticks. Trying again in 3 seconds...')
				sleep(3)
		
		sleep(3) #wait for processes to end
		
		while newgame=='waiting':
			LED_waiting(0.3)
			sleep(1)

			if newgame=='next':
				newgame=='waiting'
				print("Starting next game")
				break
			elif newgame=='exit':
				print("Exiting...")
				raise Exception

finally:
	lirc.deinit()
	GPIO.cleanup()
	player.disconnect()