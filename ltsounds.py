#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

a0 = 28
as0 = 29
b0 = 31
c1 = 33
cs1 = 35
d1 = 37
ds1 = 39
e1 = 41
f1 = 44
fs1 = 46
g1 = 49
gs1 = 52
a1 = 55
as1 = 58.3
b1 = 61.7
c2 = 65.4
cs2 = 69.3
d2 = 73.4
ds2 = 77.8
e2 = 82.4
f2 = 87.3
fs2 = 92.5
g2 = 98
gs2 = 103.8
a2 = 110
as2 = 116.5
b2 = 123.5
c3 = 130
cs3 = 138.6
d3 = 146.8
ds3 = 155.6
e3 = 164.8
f3 = 174.6
fs3 = 185
g3 = 196
gs3 = 207.6
a3 = 220
as3 = 233.1
b3 = 246.9
c4 = 261.6
cs4 = 277.2
d4 = 293.7
ds4 = 311.1
e4 = 329.6
f4 = 349.2
fs4 = 370
g4 = 392
gs4 = 415.3
a4 = 440
as4 = 466.2
b4 = 493.9
c5 = 523.3
cs5 = 554.4
d5 = 587.3
ds5 = 622.3
e5 = 659.3
f5 = 698.5
fs5 = 740
g5 = 784
gs5 = 830.6
a5 = 880
as5 = 932.3
b5 = 987.8
c6 = 1046.5

class Buzzer(object):
  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    self.buzzer_pin = 5
    GPIO.setup(self.buzzer_pin, GPIO.IN)
    GPIO.setup(self.buzzer_pin, GPIO.OUT)
#    print ("buzzer ready")

  def __del__(self):
    class_name = self.__class__.__name__
#    print (class_name, "finished")

  def buzz(self, pitch, duration):
    if(pitch==0):
      time.sleep(duration)
      return
    period = 1.0 / pitch
    delay = period / 2
    cycles = int(duration * pitch)
    for i in range(cycles):
      GPIO.output(self.buzzer_pin, 1)
      time.sleep(delay)
      GPIO.output(self.buzzer_pin, 0)
      time.sleep(delay)

  def play(self, tune):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.buzzer_pin, GPIO.OUT)
    x = 0
#    print("Playing: ", tune)
    if(tune==1):
#      print("Laser Sound")
      pitches=[a0,b0,c1,d1,e1,f1,g1,a1,b1,c2,d2,e2,f2,g2,a2,b2,c3,d3,e3,f3,g3,a3,b3,c4,d4,e4,f4,g4,a4,b4,c5,d5,e5,f5,g5,a5,b5,c6]
      duration = 0.006
      for p in pitches:
        self.buzz(p, duration)
      duration = 0.009
      for p in reversed(pitches):
        self.buzz(p, duration)
        time.sleep(duration * 0.5)
    elif(tune==2):
#      print("Playing Yankee-doodle")
      pitches=[c4,c4,d4,e4,c4,e4,d4,c4,c4,d4,e4,c4,b3,c4,c4,d4,e4,f4,e4,d4,c4,b3,g3,a3,b3,c4,c4]
      duration=[0.16,0.16,0.16,0.16,0.16,0.16,0.32,0.16,0.16,0.16,0.16,0.32,0.32,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.32,0.32]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x] * 0.5)
        x+=1
    elif(tune==3):
#      print("Start Game Sound")
      pitches=[392,294,0,392,294,0,392,0,392,392,392,0,1047]
      duration=[0.2,0.2,0.2,0.2,0.2,0.2,0.1,0.1,0.1,0.1,0.1,0.1,0.8]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x] * 0.5)
        x+=1
    elif(tune==4):
#      print("Death Sound Final")
      pitches=[c4,cs4,d4,0,b3,f4,f4,f4,f4,e4,d4,c4,e3,e3,c3]
      duration=[0.04,0.04,0.04,0.24,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.16,0.08,0.16]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x] * 0.5)
        x+=1
    elif(tune==5):
#      print("Death Sound One")
      pitches=[gs5,b4,ds4]
      duration=[0.1,0.1,0.2]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x] * 0.5)
        x+=1
    elif(tune==6):
#      print("Ammo sound 1")
      pitches=[gs3]
      duration=[0.4]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x]*0.5)
        x+=1
    elif(tune==7):
#      print("You got hit!")
      pitches=[b4,e3]
      duration=[0.1,0.3]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x]*0.5)
        x+=1
    elif(tune==8):
#      print("You hit them!")
      pitches=[f5,f5,f5]
      duration=[0.1,0.1,0.1]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x]*0.5)
        x+=1
    elif(tune==9):
#      print("End Game")
      pitches=[a3,f3,a3]
      duration=[0.2,0.2,0.2]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x]*0.5)
        x+=1
    elif(tune==10):
#      print("Reload ammo")
      pitches=[d4,b4,d5]
      duration=[0.08,0.08,0.1]
      for p in pitches:
        self.buzz(p, duration[x])
        time.sleep(duration[x]*0.5)
        x+=1

#    GPIO.setup(self.buzzer_pin, GPIO.IN)

if __name__ == "__main__":
  a = input("Enter Tune number 1-10:")
  buzzer = Buzzer()
  buzzer.play(int(a))
