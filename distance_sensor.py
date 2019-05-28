import RPi.GPIO as GPIO
import time
import math
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

def distance_measurement():

	try: 
		GPIO.setmode(GPIO.BOARD)
		
		PIN_TRIGGER = 7
		PIN_ECHO = 11
		
		GPIO.setup(PIN_TRIGGER, GPIO.OUT)
		GPIO.setup(PIN_ECHO, GPIO.IN) 
		
		GPIO.output(PIN_TRIGGER, GPIO.LOW)  
		
		time.sleep(2)
		
		total = 0
		distance_measurement_loop_counter = 0
		while distance_measurement_loop_counter < 3:			
			
			GPIO.output(PIN_TRIGGER, GPIO.HIGH)
			
			time.sleep(0.00001) 
			
			GPIO.output(PIN_TRIGGER, GPIO.LOW)
			
			while GPIO.input(PIN_ECHO) == 0:
				pulse_start_time = time.time() 
			while GPIO.input(PIN_ECHO) == 1:
				pulse_end_time = time.time() 
			
			pulse_duration = pulse_end_time - pulse_start_time
			total += round(pulse_duration * 17150, 2)
			time.sleep(2)
			distance_measurement_loop_counter += 1
		
		distance = total / 3
		return distance

	finally:
		GPIO.cleanup() 

def volume_calcuation(distance):
	length = 30
	diameter = 30
	radius = 15
	diameter_minus_distance = diameter - distance 
	tank_volume = (math.pi * (radius * radius) * length) / 1000
	
	print("Total tank capacity:", tank_volume, "litres")
	print("Distance to oil:", distance, "cm")
	
	remaining_oil = length * ((radius * radius) * 
						math.acos((radius - diameter_minus_distance) / 
						radius) - (radius - diameter_minus_distance) * 
						math.sqrt((2 * radius * diameter_minus_distance) - (
						diameter_minus_distance * diameter_minus_distance))) / 1000
	
	print("Remaining oil:", remaining_oil, "litres")
	return remaining_oil

def upload_result(remaining_oil):
	
	deviceID = 1
	
	try: 
		connection = mysql.connector.connect(host = 'oilmatedbinstance.cjhej1nzkkql.eu-west-1.rds.amazonaws.com', 
		port='3306',
		database='oilmate_database', 
		user='OilmateAdmin', 
		password='VKSWKICV13') 		
		
		cursor = connection.cursor()
		
		sql_insert_query = ("INSERT INTO `readings` (deviceID, reading, date, time) VALUES (%s, %s, CURDATE(), NOW())")
		insert_tuple = (deviceID, remaining_oil) 
		
		 
		result = cursor.execute(sql_insert_query, insert_tuple) 
		
		connection.commit()
		print ("Inserted") 
		
	except mysql.connector.Error as error : 
		connection.rollback() 
		print("Failed - rolling back {}".format(error)) 

	finally:
		if (connection.is_connected()):
				cursor.close()
				connection.close()
				print("SQL connection closed") 
	
## Main ## 

remaining_oil = volume_calcuation(distance_measurement())
upload_result(remaining_oil) 


	
