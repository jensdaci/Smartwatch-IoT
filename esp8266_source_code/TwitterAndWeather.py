from machine import Pin, I2C
import time
import ssd1306
import network
import urequests as requests
import ujson

i2c = I2C(-1, Pin(5), Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

def connectToWIFI():
	sta_if = network.WLAN(network.STA_IF)

	if (sta_if.isconnected() == False):
		print("Connecting to network...")
		sta_if.active(True)
		sta_if.connect('MySpectrumWiFid6-2G', 'wittybike022')
		while (sta_if.isconnected() == False):
			pass
	
	print("Successfully connected to the local WiFi network.")
		
def getGeolocationData():
	post_data = ujson.dumps({'empty': 'empty'})
	request_url = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyB41p-2hkW2K-S_QtLzRvydNgdSTpd_v3g"
	res = requests.post(request_url, headers = {'content-type': 'application/json'}, data = post_data).json()
	
	lat_data = str(res['location']['lat'])
	lng_data = str(res['location']['lng'])
	
	print("Latitude: " + lat_data)
	print("Longitude: " + lng_data)
	
	return lat_data, lng_data
	
def getWeatherData(lat, lng):
	weather_post_data = ujson.dumps({'empty': 'empty'})
	weather_req_url = "https://api.openweathermap.org/data/2.5/find?lat=" + lat + "&lon=" + lng + "&cnt=1&appid=844e0897926ddb1779117e7ba823a8ff"
	weather_res = requests.post(weather_req_url, headers = {'content-type': 'application/json'}, data = weather_post_data).json()
	
	temp = str(weather_res['list'][0]['main']['temp'])
	desc = str(weather_res['list'][0]['weather'][0]['description'])
	
	print("Temperature: " + temp)
	print("Description: " + desc)
	
	return temp, desc
		
def sendTweet(status):							
	post_data = ujson.dumps({'api_key': 'JYSM2P6Z0RGYYV0X', 'status': status})
	req_url = 'https://api.thingspeak.com/apps/thingtweet/1/statuses/update'
	res = requests.post(req_url, headers = {'content-type': 'application/json'}, data = post_data).json()
	return str(res)
	
def displayLastWeather(temperature, description):
	oled.fill(0)
	oled.text("Last Wthr...", 0, 0)
	oled.text("Temp: " + temperature + "K", 0, 13)
	oled.text(description, 0, 23)		
	oled.show()
	
def displayLastTweet(tweet):
	oled.fill(0)
	oled.text("Last Tweet...", 0, 0)
	oled.text(tweet, 0, 15)	
	oled.show()
	
