from machine import ADC,Pin,PWM,RTC,I2C
import time
import math
import ssd1306

class AlarmClock(object):
    def __init__(self):
    
        self.i2c = I2C(-1, Pin(5), Pin(4))
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.alarm_set = 0
        self.alarm = 0
        self.adc = ADC(0)
        self.update = 0
        self.menu = 0
        self.display_hour=0
        self.display_minute=0
        self.display_second=0
        self.time = RTC()
        #self.time.datetime((2020,10,5,0,10,10,10,0))
        self.alarm_time = [0,0,0]
        self.value = 1
        self.debounce_value = 1
        self.button_A = Pin(14,Pin.IN,Pin.PULL_UP)
        self.button_B = Pin(12,Pin.IN,Pin.PULL_UP)
        self.button_C = Pin(13,Pin.IN,Pin.PULL_UP)
        self.button_A.irq(handler=self._callback_A, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.button_B.irq(handler=self._callback_B, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.button_C.irq(handler=self._callback_C, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
	
    def _disable_interrupts(self):
        self.button_A.irq(handler=self._callback_A, trigger=0)
        self.button_B.irq(handler=self._callback_B, trigger=0)
        self.button_C.irq(handler=self._callback_C, trigger=0)
	
    def _get_current_time(self):
        
        now = self.time.datetime()
        if (self.alarm_set == 2) and ([now[4],now[5],now[6]]==self.alarm_time):
            self.alarm = 1
            self._ring_alarm()
        
        self.display_hour=now[4]
        self.display_minute=now[5]

        if self.display_second != now[6]:
            self.display_second=now[6]
            self.update = 1
   
    def _post_time(self):
        
        if self.alarm_set==1:
            hour = str(self.alarm_time[0])
            minute = str(self.alarm_time[1])
            second = str(self.alarm_time[2])
        else:
            hour = str(self.display_hour)
            minute = str(self.display_minute)
            second = str(self.display_second)
        
        text = '{} : {} : {}'.format((2-len(hour))*'0' + hour,(2-len(minute))*'0' + minute,(2-len(second))*'0' + second)
        
        self.oled.fill(0)
        if self.alarm_set==1:
            self.oled.invert(1)
        elif self.alarm_set==2:
            self.oled.invert(0)
            text+='a'
        else:
            self.oled.invert(0)
        
        self.oled.text(text,0,2)
        self.oled.show()

    def _callback_A(self,button):
        self.value = button.value()
        button.irq(trigger=0)
        time.sleep_ms(20)

        self.debounce_value = button.value()

        if self.value == self.debounce_value == 0:
            if self.alarm_set==1:
                if self.menu==0:
                    self.alarm_time[0] = (self.alarm_time[0]+1)%24
                elif self.menu==1:
                    self.alarm_time[1] = (self.alarm_time[1]+1)%60
                elif self.menu==2:
                    self.alarm_time[2] = (self.alarm_time[2]+1)%60
            elif self.alarm_set==0:
                if self.menu==0:
                    self.display_hour = self.time.datetime()[4]
                    self.display_hour = (self.display_hour+1)%24
                
                elif self.menu==1:
                    self.display_minute = self.time.datetime()[5]
                    self.display_minute = (self.display_minute+1)%60
                elif self.menu==2:
                    self.display_second = self.time.datetime()[6]
                    self.display_second = (self.display_second+1)%60
                self.time.datetime((2020,10,5,0,int(self.display_hour),int(self.display_minute),int(self.display_second),0))          
            self._post_time()
            
        button.irq(handler=self._callback_A,trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

    def _callback_B(self,button):
        self.value = button.value()
        button.irq(trigger=0)
        time.sleep_ms(20)
        self.debounce_value = button.value()
        
        if self.value == self.debounce_value == 0:
            self.alarm=0
            if self.alarm_set ==1:
                self.alarm_set +=1
            elif self.alarm_set == 2:
                self.alarm_set = 0
            else:
                self.alarm_set += 1
        button.irq(handler=self._callback_B,trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
            
    def _callback_C(self,button):
        self.value = button.value()
        button.irq(trigger=0)
        time.sleep_ms(20)
        self.debounce_value = button.value()
        if self.value == self.debounce_value == 0:
            self.menu= (self.menu + 1)%3

        button.irq(handler=self._callback_C,trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        
    def _ring_alarm(self):
        buzzer = Pin(15,Pin.OUT)
        while self.alarm:
            self.oled.fill(0)
            self.oled.text('ALARM!',0,2)
            self.oled.show()
            buzzer.value(1)
        buzzer.value(0)
      
    def _adjust_brightness(self):
        value = int(round((self.adc.read()/1024) * 255,0))
        self.oled.contrast(value)