
from machine import SPI,Pin,I2C,RTC
import ubinascii
import network
import time
import ssd1306
import urequests
import ujson

class GestureRecognition():
	def __init__(self):
		# Init accelerometer pins and buttons
		self.spi = SPI(1, baudrate=5000000, polarity=1, phase=1)
		self.cs = Pin(15,Pin.OUT,value=1)

		# Init oled
		self.i2c = I2C(-1, scl=Pin(5), sda=Pin(4))
		self.oled_width = 128
		self.oled_height = 32
		self.oled = ssd1306.SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
		
		# Button A and B and C are OLED buttons
		self.button_A = Pin(0, Pin.IN, Pin.PULL_UP)
		self.button_B = Pin(16, Pin.IN)
		self.button_C = Pin(2, Pin.IN, Pin.PULL_UP)
		
		
		#write initial settings
		self.write_reg(b'\x31',b'\x00')
		time.sleep_ms(10)
		self.write_reg(b'\x2D',b'\x08')
		time.sleep_ms(10)
		
		
	def twos_complement(self, val):
		if val & 32768 != 0:
			return val - (1 << 16)
		else:
			return val

	def write_reg(self, address, value):
		self.cs.value(0)
		self.spi.write(address)
		self.spi.write(value)
		self.cs.value(1)
		return

	def read_sensor(self, address):
		self.cs.value(0)
		self.spi.write(address)
		x1 = self.spi.read(1)
		x2 = self.spi.read(1)
		y1 = self.spi.read(1)
		y2 = self.spi.read(1)
		self.cs.value(1)
		return int(ubinascii.hexlify(x1),16),int(ubinascii.hexlify(x2),16),int(ubinascii.hexlify(y1),16),int(ubinascii.hexlify(y2),16)

	def get_Prediction(self):
		x_arr = []
		y_arr = []
		run_flag = False

		while run_flag == False:
			
			while self.button_C.value() == 0:
				# Debounce
				time.sleep_ms(1)
				if self.button_C.value() != 0:
					break
				x1,x2,y1,y2 = self.read_sensor(b'\xF2')
				x_arr.append( str(self.twos_complement(x2 << 8 | x1)) )
				y_arr.append( str(self.twos_complement(y2 << 8 | y1)) )
				time.sleep_ms(25)
				print(x_arr[-1],y_arr[-1])


			if self.button_C.value() == 1 and len(x_arr) > 0:

				r = urequests.post("http://ec2-3-87-228-201.compute-1.amazonaws.com:5001", data = ujson.dumps({'x' : x_arr, 'y' : y_arr}) )          
				data = r.content
				encoding = 'utf-8'
				str_data = ujson.loads(data.decode(encoding).replace("'", '"'))
				results = (str(str_data["prediction"]))
				del x_arr, y_arr
				run_flag = True    

		return results

	def verify_prediction(self, results):
		self.oled.fill(0)
		while True:

			self.oled.text('Prediction: ' + results[-1], 0,0)
			self.oled.text('Keep(A)/Retry(B)?', 0,10)
			self.oled.show()

			if self.button_B.value() == 0:
				time.sleep_ms(1)
				if self.button_A.value() != 0:
					break
				# kept_flag = True
				break

			elif self.button_A.value() == 0:
				time.sleep_ms(1)
				if self.button_B.value() != 0:
					break
				# kept_flag = False
				results.pop(-1)
				break
    
		# return results, kept_flag
		return results

	def display_results(self, results):
		self.oled.fill(0)
		self.oled.text(''.join(results), 0, 0)
		self.oled.show()


