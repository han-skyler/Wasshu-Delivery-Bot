import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import RPi.GPIO as GPIO
import time


PROJECT_ID = "cd-fc010"
#cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'})

ref = db.reference("sub_key")

##
last = 0
sub_motor_pin = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sub_motor_pin, GPIO.OUT)

#pwm = GPIO.PWM(sub_motor_pin, 50)

def set_servo_position(angle):
    duty_cycle = angle / 18 + 2
    pwm = GPIO.PWM(sub_motor_pin, 50)
    pwm.start(duty_cycle)
    time.sleep(1)
    
    
    pwm.stop()
    
try:
    while True:
        motor_status = ref.get()
        
        if motor_status != last:
            if motor_status == 0:
                print(f'motor 0 :{motor_status}')
                set_servo_position(0)
                
            elif motor_status == 1:
                print(f'motor 1 :{motor_status}')
                set_servo_position(90)
                
        last = motor_status
        time.sleep(1)
        
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
    
    


            