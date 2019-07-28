import RPi.GPIO as GPIO
import schedule 
import time
import math
import requests 
import datetime	


def distance_measurement():

	try: 
		# Refer to pins by number
		GPIO.setmode(GPIO.BOARD)
		
		# Trigger is plugged into slot 7.
		TRIGGER = 7
		
		# Listener plugged into slot 11.
		ECHO = 11
		
		# Assign in and out to trigger and echo.
		GPIO.setup(TRIGGER, GPIO.OUT)
		GPIO.setup(ECHO, GPIO.IN) 
		
		GPIO.output(TRIGGER, GPIO.LOW)  
		
		time.sleep(2)
		
		# Stores total distances taken over 3 measurements
		total = 0
		
		# Take three readings
		distance_measurement_loop_counter = 0
		
		while distance_measurement_loop_counter < 3:			
			
			# Fire ultrasonic trigger for 1 nano second
			GPIO.output(TRIGGER, GPIO.HIGH)				
			time.sleep(0.00001) 			
			GPIO.output(TRIGGER, GPIO.LOW)
			
			# While the echo receives no sound, set start time
			while GPIO.input(ECHO) == 0:
				pulse_start_time = time.time() 
				
			# Once the echo receives sound, set end time
			while GPIO.input(ECHO) == 1:
				pulse_end_time = time.time() 
			
			# Calculate total duration of pulse
			pulse_duration = pulse_end_time - pulse_start_time
			
			# Pulse duration / half speed of sound in cm/s added to the
			# total of the three readings.  Calculates the distance to 
			# the oil level in cms
			total += round(pulse_duration * 17150, 2)
			
			# Allow sensor to settle
			time.sleep(2)
			
			# Increment loop counter
			distance_measurement_loop_counter += 1
		
		# Calculate average of the three readings for final distance 
		# readings
		distance = total / 3
		
		return distance

	finally:
		GPIO.cleanup() 

def volume_calcuation(distance):
	# Dimensions of tank
	length = 30
	diameter = 30
	radius = diameter / 2
	diameter_minus_distance = diameter - distance 
	tank_volume = (math.pi * (radius * radius) * length) / 1000
	
	# Calculate remaining oil using segement of a circle formula
	remaining_oil = length * ((radius * radius) * 
						math.acos((radius - diameter_minus_distance) / 
						radius) - (radius - diameter_minus_distance) * 
						math.sqrt((2 * radius * diameter_minus_distance) - (
						diameter_minus_distance * diameter_minus_distance))) / 1000
	
	print("Remaining oil:", remaining_oil, "litres")
	return remaining_oil

def upload_result(remaining_oil):
	# Assign variables for deviceID and curent datetime.
	deviceID = 1
	currentDT = datetime.datetime.now()
	currentDate = currentDT.strftime("%Y/%m/%d")
	currentTime = currentDT.strftime("%H:%M:%S")
	
	# Url, token, and data for the API>
	url = 'http://159.65.93.37/api/readings/new'
	headers = {"x-access-token" : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOjEsInVzZXJuYW1lIjoiUmlja3lLeWxlIiwiaWF0IjoxNTYzNzM0ODA1fQ.w_Ik97ldaX_9CmDR7kZouw8_s5acTxlyb0Fn4IsIwg8"}
	data = {
			"deviceID" : deviceID,
			"reading" : remaining_oil,
			"date" : currentDate,
			"time" : currentTime
			}
	
	# Pass headers, url, and data to requests package to upload.
	requests.post(url, headers=headers, data=data)

# Passes the result of the reading to the volume_calculation function,
# then passes the volume_caulcation to the upload_result function.
def read_upload(): 
	remaining_oil = volume_calcuation(distance_measurement())
	upload_result(remaining_oil) 


print("Application is running...") 

# Uses schedule package to upload a reading every 4 hours.
schedule.every(240).minutes.do(read_upload)

while True: 
	schedule.run_pending()
	time.sleep(1)
	

















	
