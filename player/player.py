#!/usr/bin/python3

# Future development: change the client parameter to prompt on join to the server
# so that players join and press a button to confirm their slot
# i.e. circle = player 1, cross = player 2, etc
CLIENT='1' #each player needs to have a different CLIENT number. 1,2,3,etc,
# Future development: change this so that it is stored in a variables file on the local device.
# For the the moment the IP address will be fixed, but this should be flexible
LTSERVER='192.168.1.225' #insert IP address of server computer

#---------------------
#BUZZER:     GPIO5
#TRIGGER:    GPIO23
#RELOAD:     GPIO12
#IR_TX:      GPIO22
#IR_RX       GPIO18         Notes for wiring
#RED:        GPIO20
#GREEN:      GPIO21
#BLUE:       GPIO26
#I2C_SDA:    GPIO2
#I2C_SCL:    GPIO3
#---------------------
import paho.mqtt.client as mqtt
from os import _exit
from sys import exit
from time import sleep
import RPi.GPIO as GPIO
from random import randint
import ast
# import lirc
import ltsounds
from subprocess import call
import threading
from datetime import datetime
from py_irsend import irsend
from approxend.input.selectbinder import ControllerResource

GPIO.setmode(GPIO.BCM)
""" Suggest removing trigger and reload when controller is working """
TRIGGER=23
RELOAD=12
RED=20
GREEN=21
BLUE=26
newgame='waiting'
game_wait=3
connected=False

""" Suggest reviewing trigger and reload for later removal when the controller is working """
GPIO.setup(TRIGGER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RELOAD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

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

def shoot(pin):
    global maxDeaths, stats
    if(stats['health']==0 or stats['deaths']>maxDeaths):
        sound('error')
    elif(stats['ammo']==0):
        LED(BLUE,1)
    elif(stats['ammo']>=1):
        irsend.send_once('ltag', [gvars_dict['game_mode']+CLIENT]) #New line that utilises the py_irsend module
        stats['shots_fired']+=1
        stats['ammo']-=1
        print("shot fired") #uncommented this line so that we can check logs when shooting 
        sound('shoot')
        LED(GREEN,0.3)

def tag_received(code):
	global stats
	player.publish('game/ltserver',CLIENT) #tell server I  was tagged
	from_player=code[-3:-2] #who was the tagger
	print("Received tag from player"+ str(from_player))
	return_topic='game/players/'+str(from_player) #who to reply to
	player.publish(return_topic,CLIENT) #reply to tagger
	tag_location=randint(0,len(stats['tags_received'])-1) #random 
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
    tag_location=randint(0,len(stats['tags_given'])-1) #random sensor
    tmp=list(stats['tags_given'])[tag_location]
    stats['tags_given'][tmp]+=1
    stats['kills']+=1
    sound('tag_given')
    LED(BLUE,1)

def player_reload(pin):
    global stats,game_in_progress
    if(stats['health']<=0):
        sound('error')
    else:
        sound('reloading')
        stats['ammo'] = maxAmmo
        LED(GREEN,0.5)

def dead(return_topic):
    global stats,game_in_progress
    game_in_progress=False
    stats['deaths']+=1
    if(int(gvars_dict['num_players_dead'])!=int(gvars_dict['num_players'])-1):
        sound('dead')
        LED(RED,3)
    sleep(1)
    player.publish(return_topic,'dead')

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
	player=mqtt.Client(client_id=CLIENT,clean_session=True)
	player.on_connect=onConnect
	player.on_message=onMessage
	player.on_disconnect=onDisconnect
	sound_class = ltsounds.Buzzer()
	game_in_progress=False
	GPIO.add_event_detect(TRIGGER,GPIO.RISING,shoot,bouncetime=400) #commented out this line as it will be redundant due to use of a controller
	GPIO.add_event_detect(RELOAD,GPIO.RISING,player_reload,bouncetime=400) #commented out this line as it will be redundant due to use of a controller

	while not connected:
		try:
			player.connect(LTSERVER,keepalive=60,bind_address="")
			connected=True
		except ConnectionRefusedError:
			print('LTServer must be started first...')
			LED_waiting(0.3)
			sleep(1)
	
	connected=False

	while True:
			stats=dict(player=CLIENT,shots_fired=0,kills=0,deaths=0,health=0,ammo=0,
					   tags_given=dict(rhull=0,lhull=0),
					   tags_received=dict(rhull=0,lhull=0))
			player.loop_start()
			player.publish('game/ltserver','ready')

		while not game_in_progress:
			pass #wait for start game message
			
		initialize(gvars_dict['game_mode'],gvars_dict['end_type'],int(gvars_dict['end_value']))

		while game_in_progress:
			Try:
				with ControllerResource() as joystick:
					while joystick.connected:
						joystick.check_presses()
						if joystick.presses.cross:
							player_reload()
						elif joystick.presses.l1:
							shoot()
			""" the following section needs to be threaded, along with the joystick section """
				code=lirc.nextcode()
				if code:
					tag_received(str(code))
			sleep(5) #wait for processes to end
		
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

	except IOError:
		# No joystick found, wait for a bit before trying again
		print('Unable to find any joysticks. Trying again in 3 seconds...')
		sleep(3.0)

finally:
	GPIO.cleanup()
	player.disconnect()
