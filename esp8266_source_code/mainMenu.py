from machine import Pin, I2C, RTC, ADC, PWM
import time
import ssd1306

class OLEDScreen(object):
	def __init__(self):
		self.x = 0
		self.y = 0
		self.count = 0
		
		self.option = ""
		
		self.option1_flag = False
		self.option2_flag = False
		self.option3_flag = False
		self.option4_flag = False
		self.option5_flag = False
		self.option6_flag = False
		
		self.MainMenu_flag = False
		
		#Button initialization
		self.buttonA = Pin(14, Pin.IN, Pin.PULL_UP)
		self.buttonB = Pin(12, Pin.IN, Pin.PULL_UP)
		self.buttonC = Pin(13, Pin.IN, Pin.PULL_UP)
		self.buttonRST = Pin(0, Pin.IN, Pin.PULL_UP)

		#Buzzer initialization
		self.buzzer = Pin(15, Pin.OUT)	#Piezo Buzzer
		self.pwmBuzzer = PWM(Pin(15), freq=500, duty=0) #Create PWM for Piezo

		#ADC initialization
		self.adc = ADC(0)


		self.i2c = I2C(-1, Pin(5), Pin(4))
		self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
		
		self.enableInterrupts()
	
	def enableInterrupts(self):
		self.buttonA.irq(trigger = Pin.IRQ_FALLING, handler = self.moveUp)
		self.buttonB.irq(trigger = Pin.IRQ_FALLING, handler = self.clickThis)
		self.buttonC.irq(trigger = Pin.IRQ_FALLING, handler = self.moveDown)
		self.buttonRST.irq(trigger = Pin.IRQ_FALLING, handler = self.enableMainMenu)
		
	def disableInterrupts(self):
		self.buttonA.irq(trigger = 0, handler = self.moveUp)
		self.buttonB.irq(trigger = 0, handler = self.clickThis)
		self.buttonC.irq(trigger = 0, handler = self.moveDown)
	
	#Function to debounce button presses
	def debounce(self, btn): 
		stateNow = btn.value()
		time.sleep_ms(30)
		
		if(btn.value() != stateNow):
			return 0
		else: 
			return 1
	
	def moveUp(self, p):
		if self.debounce(self.buttonA):
			self.count = self.count - 1
			
			if self.count == 0:
				self.x = 1
				self.y = 0
			if self.count == 3:
				self.x = 70
				self.y = 0
			
			self.y = self.y - 12
			
	def moveDown(self, p):
		if self.debounce(self.buttonC):
			self.count = self.count + 1
			
			if self.count == 0:
				self.x = 1
				self.y = 0
			if self.count == 3:
				self.x = 70
				self.y = -12
			
			self.y = self.y + 12

	def clickThis(self, p):
		if self.debounce(self.buttonB):
			if ((self.x==1) & (self.y==0)):
				self.option1_flag = True
			if ((self.x==1) & (self.y==12)):
				self.option2_flag = True
			if ((self.x==1) & (self.y==24)):
				self.option3_flag = True
			if ((self.x==70) & (self.y==0)):
				self.option4_flag = True
			if ((self.x==70) & (self.y==12)):
				self.option5_flag = True
			if ((self.x==70) & (self.y==24)):
				self.option6_flag = True
	
	def enableMainMenu(self, p):
		if self.debounce(self.buttonRST):
			self.MainMenu_flag = ~self.MainMenu_flag
			print(str(self.MainMenu_flag))
	
	def showBlankScreen(self):
		self.oled.fill(0)
		self.oled.show()
	
	def MainMenu(self):
		
		self.option1_flag = False
		self.option2_flag = False
		self.option3_flag = False
		self.option4_flag = False
		self.option5_flag = False
		self.option6_flag = False
		
		self.x = 1
		self.y = 0
		self.count = 0
		
		while str(self.MainMenu_flag) == "0":
			self.oled.fill(0)
						
			self.oled.text(" Time     Wth", 0, 0)
			self.oled.text(" Comm     Gest", 0, 12)
			self.oled.text(" Tweet        ", 0, 24)
			self.oled.text(".", self.x, self.y)
				
			if (self.option1_flag):
				self.option = "Option 1"
			if (self.option2_flag):
				self.option = "Option 2"
			if (self.option3_flag):
				self.option = "Option 3"
			if (self.option4_flag):
				self.option = "Option 4"
			if (self.option5_flag):
				self.option = "Option 5"
			if (self.option6_flag):
				self.option = "Option 6"
				
			self.oled.show()
		
		return self.option