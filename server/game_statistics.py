#!/usr/bin/python3

import matplotlib.pyplot as plt
from random import *
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import ttk, scrolledtext
import csv
import gvars
import time
import os
import shutil

rshoulder=[110,180]
lshoulder=[290,180]
chest=[200,300]
back=[200,650]
dictionary=['tags_given','tags_received']
subplotnum=[121,122]
image=['enemies.png','self.png']
size=25
color=['g','r']
spread=30
past_game=""
history_dir="history"
newgame=False
#import Game Stats CSV File
#Header: Game type, number of Players, Time
#Player: Player type, shots fired, tags given, tags taken

def rando():
    return randint(-spread,spread)

def compile_stats(player1,player2,player3,duration):
    global past_game
    if gvars.num_players==2:
        player_list=[player1,player2]
    else:
        player_list=[player1,player2,player3]
    for player in player_list:
        plt.figure(player['player'])
        plt.suptitle('Player '+str(player['player'])+' Accuracy Report',fontsize=24)
        for i in range(0,2):
            plt.subplot(subplotnum[i])
            im=plt.imread(image[i])
            implot=plt.imshow(im)
            plt.axis('off')
            for tags in player[dictionary[i]]:
                for x in range(0,player[dictionary[i]][tags]):
                    if(tags=='rshoulder'):
                        plt.scatter(x=rshoulder[0]+rando(),y=rshoulder[1]+rando(),c=color[i],s=size)
                    elif(tags=='lshoulder'):
                        plt.scatter(x=lshoulder[0]+rando(),y=lshoulder[1]+rando(),c=color[i],s=size)
                    elif(tags=='chest'):
                        plt.scatter(x=chest[0]+rando(),y=chest[1]+rando(),c=color[i],s=size)
                    elif(tags=='back'):
                        plt.scatter(x=back[0]+rando(),y=back[1]+rando(),c=color[i],s=size)

        plt.savefig(str(player['player'])+'player_stats.png',bbox_inches='tight')
        plt.subplots_adjust(wspace=0,hspace=0)
        plt.clf()
#    plt.show()

    #rankings
    player_rank=[]
    rankings=sorted(player_list,key=lambda d: d['kills'],reverse=True)
    for n in range(len(rankings)):
        player_rank.append(str(rankings[n]['player']))

    #create history file
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    past_game=(history_dir+"/"+time.strftime("%c").replace(" ","_")+".csv")
    fout=open(past_game,"w+")
    fout.write(gvars.game_mode+","+str(gvars.num_players)+","+duration+","+str(','.join(player_rank))+"\n")
    for player in player_list:
        fout.write(gvars.game_mode+","+str(player['shots_fired'])+","+str(player['kills'])+","+str(sum(player['tags_received'].values()))+"\n")
    fout.close()

def postgame_gui():
    global past_game
    fin = open(past_game,"r")
    reader = csv.reader(fin,delimiter=",")
    GType = 'na';numPlayers = 0;GTime = '00:00:00'
    PType = [];PFired=[];PGiven=[];PTaken=[]
    fr = 0
    for row in reader:
        if fr == 0:
            fc = 0
            for col in row:
                if fc == 0:
                    GType = row[fc]
                if fc == 1:
                    numPlayers = int(row[fc])
                if fc == 2:
                    GTime = row[fc]
                if fc == 3:
                    place1 = row[fc]
                if fc == 4:
                    place2 = row[fc]
                if fc == 5:
                    if numPlayers==3:
                        place3 = row[fc]
                fc+=1
            fr+=1
        else:
            fc = 0
            for col in row:
                if fc == 0:
                    PType.append(row[fc])
                if fc == 1:
                    PFired.append(int(row[fc]))
                if fc == 2:
                    PGiven.append(int(row[fc]))
                if fc == 3:
                    PTaken.append(int(row[fc]))	
                fc+=1

    fin.close()
    gtg=0;gtt=0;gtf=0
    for j in PGiven:
        gtg+=j
    for j in PTaken:
        gtt+=j
    for j in PFired:
        gtf+=j

    #initialize Window
    numTabs = int(numPlayers) + 1
    tab = [None]*numTabs
    lbl = [None]*numTabs
    img = [None]*numTabs
    imgc = [None]*numTabs
    window = Toplevel()
    window.title("Game Stats")
    window.geometry('705x575')
    tab_ctrl = ttk.Notebook(window)

    #Generate Game Stats Page
    tab[0]=ttk.Frame(tab_ctrl)
    tab_ctrl.add(tab[0], text='Game Stats')
    if numPlayers==3:
        stats = '\n\n   Game Type:   {}\n   Game Time:   {}\n   Number of Players: {}\n\n----------------Rankings---------------\n\n   1. Player{}\n   2. Player{}\n   3. Player{}\n\n'.format(GType,GTime,numPlayers,place1,place2,place3)
    else:
        stats = '\n\n   Game Type:   {}\n   Game Time:   {}\n   Number of Players: {}\n\n----------------Rankings---------------\n\n   1. Player{}\n   2. Player{}\n\n'.format(GType,GTime,numPlayers,place1,place2)

    imgc[0]=ImageTk.PhotoImage(Image.open("home.png"))
    img[0] = Label(tab[0], image=imgc[0])
    img[0].grid(column=0,row=0,columnspan=13)
    lbl[0] = Label(tab[0],text=stats,justify=LEFT)
    lbl[0].grid(column=7,row=0,columnspan=4)

    #Generate Player Stats Pages
    for i in range (1,numTabs):
        p = i-1
        tab[i]=ttk.Frame(tab_ctrl)
        tit = "Player " + str(i) + " Stats"
        tab_ctrl.add(tab[i],text=tit)
        PImage = str(i)+"player_stats.png"
        imgc[i] = ImageTk.PhotoImage(Image.open(PImage))
        img[i] = Label(tab[i], image = imgc[i])
        img[i].grid(column=0,row=0)
        acur=0 if PFired[p]==0 else PGiven[p]/PFired[p]*100
        pgtg=0 if gtg==0 else PGiven[p]/gtg*100  
        pgtt=0 if gtt==0 else PTaken[p]/gtt*100 
        pgtf=0 if gtf==0 else PFired[p]/gtf*100
        pstats = 'Player Type: {}\nShots Fired: {}\nTags Given:  {}\nTags Received:  {}\nAccuracy:    {:.0f}%\n\nGlobal Percentages\nTags Given: {:.0f}%\nTags Received: {:.0f}%\nTags Fired: {:.0f}%'.format(PType[p],PFired[p],PGiven[p],PTaken[p],acur,pgtg,pgtt,pgtf)	
        lbl[i] = Label(tab[i],text=pstats,justify=LEFT)
        lbl[i].grid(column=1,row=0)

    tab_ctrl.grid(column=0,row=0)
   
    def on_closing():
        global newgame
        if messagebox.askyesno("Quit","Quit LaserTag?"):
            newgame=False
            window.quit()
            window.destroy()

    def on_newgame():
        global newgame
        newgame=True
        window.quit()
        window.destroy()
    
    def on_clear():
        if messagebox.askyesno("Clear Game History","Are you sure you want to clear the game history? This action cannot be undone."):
            shutil.rmtree(history_dir)
            messagebox.showinfo("Cleared","Game history has been cleared")

    newgamebtn=Button(tab[0],text="New Game", command=on_newgame)
    newgamebtn.grid(sticky="S",column=11,row=0)
    quitbtn=Button(tab[0],text="Quit", command=on_closing)
    quitbtn.grid(sticky="S",column=12,row=0)
    clearbtn=Button(tab[0],text="Clear Game History", command=on_clear)
    clearbtn.grid(column=10,row=0,sticky="S")
    
    window.protocol("WM_DELETE_WINDOW",on_closing)
    window.mainloop()
    return newgame
