import socket
import network
import time
import urequests as requests
from machine import Pin,I2C,PWM,RTC,Timer
import ssd1306
import TwitterAndWeather as TaW

class AlarmClock(object):
    def __init__(self):
    
        self.i2c = I2C(-1, Pin(5), Pin(4))
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.update = 0
        self.display = False
        
        self.display_hour=0
        self.display_minute=0
        self.display_second=0
        
        self.timer = Timer(0)
        self.time = RTC()
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self._handleInterrupt)

    def _get_current_time(self):
        
        now = self.time.datetime()

        self.display_hour=now[4]
        self.display_minute=now[5]

        if self.display_second != now[6]:
            self.display_second=now[6]
            self.update = 1
   
    def _post_time(self):
        if self.display:
            hour = str(self.display_hour)
            minute = str(self.display_minute)
            second = str(self.display_second)

            if len(hour)==1:
                hour = '0' + hour
            if len(minute)==1:
                minute = '0' + minute
            if len(second)==1:
                second = '0' + second
                
            text = hour + ' : ' + minute + ' : ' + second
            self.oled.fill(0)
            
            self.oled.invert(0)
            self.oled.text(text,0,2)
            self.oled.show()
    def _handleInterrupt(self,timer):
            self._get_current_time()
            self._post_time()
        

def display_on():
    try:
        i2c = I2C(-1,Pin(5),Pin(4))
        oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        oled.fill(0)
        oled.text('Hello',0,0)
        oled.show()
        response = 'display on'
    except:
        response = 'error'
    return response


def display_off():
    try:
        i2c = I2C(-1,Pin(5),Pin(4))
        oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        oled.fill(0)
        oled.show()
        response = 'display off'
        return response
    except:
        response = 'error'
        return response

def display_time(alarmClock):
    try:

        response = 'display time'
        alarmClock.display=True
        alarmClock._get_current_time()
        alarmClock._post_time()
        return response
    except:
        response = 'error'
        return response

def display_weather():
    try:
        i2c = I2C(-1,Pin(5),Pin(4))
        oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        latitude, longitude = TaW.getGeolocationData()
        time.sleep_ms(100)
        temperature, description = TaW.getWeatherData(latitude, longitude)
        oled.fill(0)
        oled.text("Weather...", 0, 0)
        oled.text("Temp: " + temperature + "K", 0, 13)
        oled.text(description, 0, 23)		
        oled.show()
        response = "...Temp: " + temperature + "K" + "\n.........Desc: " + description
        return response, temperature, description
    except:
        response = 'error'
        return response

def send_tweet(tweet):
    try:
        i2c = I2C(-1,Pin(5),Pin(4))
        oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        TaW.sendTweet(tweet)
        oled.fill(0)
        oled.text("Tweet...", 0, 0)
        oled.text(tweet, 0, 15)	
        oled.show()
        response = '...tweet sent:  ' + tweet
        return response
    except:
        response = 'error'
        return response

def show(command):
    try:
        i2c = I2C(-1,Pin(5),Pin(4))
        oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        oled.fill(0)
        oled.text(command,0,0)
        oled.show()
        response = 'command displayed'
        return response
    except:
        response = 'error'
        return response
		


