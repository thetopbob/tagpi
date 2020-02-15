#!/usr/bin/python3

import tkinter as tk
from tkinter import * 
from tkinter import messagebox
from PIL import ImageTk, Image
import pygubu
from time import sleep
import gvars

class Application:
    def __init__(self,master):
        self.builder=builder=pygubu.Builder()
        builder.add_from_file('pygubu_limited.ui')
        self.mainwindow=builder.get_object('pregame',master)
        builder.connect_callbacks(self)
        pregame.protocol("WM_DELETE_WINDOW", self.on_closing)

#  attempt to add background image      
#        cover=ImageTk.PhotoImage(Image.open("home.png")) 
#        lb_cover=Label(self.mainwindow,image=cover)
#        lb_cover.image=cover
#        lb_cover.grid(column=0,row=0)

    def click_start_game(self):
        global pregame
        if(gvars.game_mode=='Showdown'):
            gvars.end_value=99
        pregame.quit()
        pregame.destroy()

    def click_end_type(self):
        output=self.builder.get_variable('end_type').get()
        if(output=="minutes"):
            gvars.end_type="time"
        else:
#            gvars.end_type="tags"
            gvars.end_type="lives"

    def click_end_limit(self):
        gvars.end_value=self.builder.get_object('end_value').get()

    def click_game_mode(self,event=None):
        gvars.game_mode=self.builder.get_object('dd_game_mode').get()
        if(gvars.game_mode=='Classic'):
            self.builder.get_object('description').config(text="Classic: Points are awarded for each tag. The victor is the player with the most points at the end of the game.")
        elif(gvars.game_mode=='Overwatch'):
            self.builder.get_object('description').config(text="Overwatch: Each player chooses a character with a set of skills and abilities to use throughout the game.")
        elif(gvars.game_mode=='GunGame'):
            self.builder.get_object('description').config(text="GunGame: Each tag improves the player's weapon by cycling to a new gun. The first player to cycle through each weapon is the victor.")
        elif(gvars.game_mode=='LaserMaster'):
            self.builder.get_object('description').config(text="LaserMaster: Each player has only one laser at the start of the game. Another is earned by tagging an oppenent.")
        elif(gvars.game_mode=='Showdown'):
            self.builder.get_object('description').config(text="Showdown: Get as many tags as possible in this one-minute battle.")

    def click_num_players(self, event=None):
        gvars.num_players=self.builder.get_object('dd_num_players').get()

    def on_closing(self):
        if messagebox.askyesno("Quit", "Quit LaserTag?"):
            gvars.cancel=True
            pregame.quit()
            pregame.destroy()

def pregame_gui():
    global pregame
    pregame=tk.Tk()
    pregame.title("Laser Tag")

    app=Application(pregame)
    pregame.mainloop()
    return gvars.cancel

