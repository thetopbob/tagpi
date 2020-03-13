from approxeng.input.selectbinder import ControllerResource
from time import sleep

class controller():
	def circlepress():
		currentbutton = "Circle"
		# Do something!

	def squarepress():
		currentbutton = "Square"
		# Do something!
	
	def main():
		while True:
			try:
				with ControllerResource() as joystick:
					while joystick.connected:
						print('Found a joystick and connected')
						joystick.check_presses()
						#if joystick.has_presses:
							#print(joystick.presses)
						if joystick.presses.circle:
							circlepress()
						elif joystick.presses.square:
							squarepress()
							# Joystick disconnected..
              #print('Connection to joystick lost')
				
if __name__ == "__main__":
	#print(joystick.controls)
	main()
	
	except IOError:
        # No joystick found, wait for a bit before trying again
		print('Unable to find any joysticks')
		sleep(1.0)
