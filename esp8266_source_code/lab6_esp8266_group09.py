"""
Group 9:     Jens Daci 
			 Endric Daues
			 Daniel Klass

Class Code:  EECS E4764
Class Title: IoT - Intelligent and Connected Systems

Assignment:  Lab 6 - Smartwatch
"""
from machine import Pin, I2C, RTC, ADC, PWM, Timer
import time
import socket
import network
import ssd1306
import alarmclock
import mainMenu
import commandFunc
import TwitterAndWeather as TaW
import gestureRecognition as grec


screen = mainMenu.OLEDScreen()
temperature = "___"
description = "___"
tweet = "___"

		
while True:
	
	screen.enableInterrupts()
	option = screen.MainMenu()
	
	if option == "Option 1":
		screen.disableInterrupts()
		
		alarmClock = alarmclock.AlarmClock()
		while str(screen.MainMenu_flag) == "-1":
			alarmClock._get_current_time()
			alarmClock._adjust_brightness()
			if alarmClock.update:
				alarmClock._post_time()
			time.sleep_ms(50)
			
		alarmClock._disable_interrupts()
	
	if option == "Option 2":
		screen.disableInterrupts()
		
		sta_if = network.WLAN(network.STA_IF)
		sta_if.active(True)
		sta_if.connect('MySpectrumWiFid6-2G', 'wittybike022')

		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.bind(('', 80))
		s.listen(1)

		print('listening on', sta_if.ifconfig()[0])
		show_time = False
		clock = commandFunc.AlarmClock()
			
		while str(screen.MainMenu_flag) == "-1":
			response = ''
			cl, addr = s.accept()
			print('client connected from', addr)
			cl_file = cl.makefile('rwb', 0)
			
			while str(screen.MainMenu_flag) == "-1":
				line = cl_file.readline()
				line = line.decode('ASCII')
				print(line)
				
				if 'Command' in line:
					start = line.index(':')
					end = line.index('\r\n')
					command = str(line[start+1:end])
					
					if ('display' in command) and ('on' in command):
						response = commandFunc.display_on()
						clock.display=False
						
					elif ('display' in command) and ('off' in command):
						response = commandFunc.display_off()
						clock.display=False
						
					elif ('time' in command) and (('on' in command) or ('display' in command)):
						response = commandFunc.display_time(clock)
						
					elif ('tweet' in command) and ('this' in command):
						x = command.split(" this")
						tweet = str(x[1])
						response = commandFunc.send_tweet(tweet)
						
					elif ('get' in command) and ('weather' in command):
						response, temperature, description = commandFunc.display_weather()
						
					else:
						response = commandFunc.show(command)
						clock.display=False
				
				if not line or line == '\r\n':
					break
					
			print("after small loop")
			cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\nContent-Length: {}\r\n\r\n'.format(len('esp: ' + response)))
			cl.send('esp: ' +response)#.encode("utf-8"))
			cl.close()
		
		print("after big loop")
			
			
	if option == "Option 3":
		screen.disableInterrupts()
		
		while str(screen.MainMenu_flag) == "-1":
			TaW.displayLastTweet(tweet)
	
	if option == "Option 4":
		screen.disableInterrupts()
		
		while str(screen.MainMenu_flag) == "-1":
			TaW.displayLastWeather(temperature, description)
			
	if option == "Option 5":
		screen.disableInterrupts()
		screen.showBlankScreen()
		gesturerec = grec.GestureRecognition()
		
		while str(screen.MainMenu_flag) == "-1":		
			
			# Initialize vector
			results = []
			
			# Get prediction
			results.append(gesturerec.get_Prediction())
			
			# Check if we want to keep letter
			results = gesturerec.verify_prediction(results)
			
			# Push results to OLED
			gesturerec.display_results(results)
	 
	screen.showBlankScreen()

	
	
	


