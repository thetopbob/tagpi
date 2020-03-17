#!/usr/bin/python3

import paho.mqtt.client as mqtt
from sys import exit
import ast
from time import sleep
import game_statistics as game_stats
from subprocess import call
import gvars
import pregame
from datetime import datetime,timedelta

call(["sudo","service","mosquitto","start"])
sleep(.5) #make sure service has started prior to game start
CLIENT='ltserver'
LTSERVER='localhost'

players_ready=0
num_stats_received=0
#repeat=False

def onConnect(client,userdata,flags,rc):
    if(rc==0):print("Connected")

def onSubscribe(client,userdata,mid,granted_qos):
    pass

def onMessage(client,userdata,message):
    global player1_stats,player2_stats,player3_stats,players_ready,game_in_progress,gvars_dict,num_stats_received#,repeat

    if(len(message.payload.decode())==1): #someone was tagged
        for player in [player1_stats,player2_stats,player3_stats]:
            if(message.payload.decode()==str(player['player'])):
                player['health']=int(player['health'])
                player['health']-=1
                if(player['health']<=0):
                    gvars_dict['num_players_dead']+=1
                    if(int(gvars_dict['num_players_dead'])==int(gvars_dict['num_players'])-1):
                        server.publish('game/players','game over')
                        print("Ending Game...")
                        game_in_progress=False
                break

    elif(message.payload.decode()=='ready'):
        players_ready+=1 #make sure everyone is ready to start
        print(players_ready,"player(s) in game lobby")
#    elif(message.payload.decode()=='repeat'):
#        repeat=True
    else: #receive stats for end of game compilation
        num_stats_received+=1
        incoming_stats=ast.literal_eval(message.payload.decode())
        if(incoming_stats['player']=='1'):
            player1_stats=incoming_stats
        elif(incoming_stats['player']=='2'):
            player2_stats=incoming_stats
        elif(incoming_stats['player']=='3'):
            player3_stats=incoming_stats

def onDisconnect(client,userdata,message):
    print("Disconnected from broker")

"""
inserted the following to help debug MQTT events
"""
def onLog(client, userdata, level, buf):
    print("log: ",buf)

def create_player(num,starting_health):
    instance=dict(player=num,shots_fired=0,kills=0,deaths=0,health=starting_health,ammo=0,tags_given=dict(rshoulder=0,lshoulder=0,chest=0,back=0),tags_received=dict(rshoulder=0,lshoulder=0,chest=0,back=0))
    return(instance)

def print_everyone(message):
    print(message)
    server.publish('game/players',message)

def game_lobby():
    print("Waiting for other players...")
    while(players_ready<3):
        if(players_ready==2):
            sleep(1)
            wait_time=5
            print_everyone("Starting 2 player game in "+str(wait_time)+" seconds...")
            for n in range(wait_time-1):
                if(players_ready==3):
                    print_everyone("Starting 3 player player")
                    break
                sleep(1)
                if(n==wait_time-2):
                    print_everyone("Starting 2 player game")
            break

#----------------------------------------------------------
#                        MAIN
#----------------------------------------------------------

server=mqtt.Client(client_id=CLIENT,clean_session=True)
server.on_connect=onConnect
server.on_subscribe=onSubscribe
server.on_message=onMessage
server.on_disconnect=onDisconnect
server.on_log=onLog
server.connect(LTSERVER,keepalive=60,bind_address="")
server.loop_start()
server.subscribe('game/ltserver',0)

while True:
    try:
        game_in_progress=True

        gvars.init() #pull in all the global variables
#        if not repeat:
        if pregame.pregame_gui():
            raise KeyboardInterrupt
#        repeat=False

        player1_stats=create_player(1,gvars.end_value)
        player2_stats=create_player(2,gvars.end_value)
        player3_stats=create_player(3,gvars.end_value)

        gvars_dict=dict(num_players_dead=0,num_players=gvars.num_players,game_mode=gvars.game_mode,end_type=gvars.end_type,end_value=gvars.end_value,player1_char=gvars.player1_char,player2_char=gvars.player2_char,player3_char=gvars.player3_char,cancel=gvars.cancel)

        game_lobby()
        server.publish('game/players',str(gvars_dict))
        server.publish('game/players','start game')
        start_time=datetime.now()

        if(gvars.game_mode=='Showdown'):
            showdown_end=start_time+timedelta(0,67);
            while(game_in_progress):
                sleep(1)
                if(datetime.now()>=showdown_end):
                    server.publish('game/players','game over')
                    print("Ending Game...")
                    game_in_progress=False
                    break

        while(game_in_progress):
            pass

        end_time=datetime.now()
        duration=end_time-start_time
        duration="%02d:%02d"%(duration.seconds//60,duration.seconds%60)

        players_ready=0
#        sleep(10) #wait for possible repeat
        while(int(num_stats_received)<int(gvars.num_players)):
            pass #wait for all stats to come in
        num_stats_received=0

#        if not repeat:
        game_stats.compile_stats(player1_stats,player2_stats,player3_stats,duration)
        newgame=game_stats.postgame_gui()

        if not newgame:
            print("Exiting LTag...")
            raise KeyboardInterrupt

        server.publish('game/players','next')
        gvars.cancel=False

    except(KeyboardInterrupt):
        server.publish('game/players','exit')
        call(["sudo","service","mosquitto","stop"])
        exit(0)
