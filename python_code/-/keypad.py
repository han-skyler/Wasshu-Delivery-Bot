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
ref2 = db.reference("open_pw")

    
encrypted_code = ref2.get()

def decrypt_code(encrypted_code):
    decrypted_result = ""
    
    for char in encrypted_code:
        decrypted_digit = chr(ord(char) - 5)
        txt = ord(decrypted_digit)
        txt -= 64
        decrypted_result += str(txt)
        
    return decrypted_result
    
decrypted_result = decrypt_code(encrypted_code)


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
  
##
keypad_rows = [10, 9, 11, 5]
keypad_cols = [6, 13, 19, 26]


keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
    ]

correct_password = decrypted_result

GPIO.setmode(GPIO.BCM)
for row_pin in keypad_rows:
    GPIO.setup(row_pin, GPIO.OUT)
    GPIO.output(row_pin, GPIO.HIGH)
    
for col_pin in keypad_cols:
    GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    

def get_key():
    for i, row_pin in enumerate(keypad_rows):
        GPIO.output(row_pin, GPIO.LOW)
        for j, col_pin in enumerate(keypad_cols):
            if GPIO.input(col_pin) == GPIO.LOW:
                return keys[i][j]
        GPIO.output(row_pin, GPIO.HIGH)
    return None
   
try:
    entered_password = ''
    while True:
        key = get_key()
        if key:
            entered_password += key
            print('Entered Password :{entered_password}')
            
            if len(entered_password)== len(correct_password):
                if entered_password == correct_password:
                    print('correct')
                    set_servo_position(0)
                else:
                    print('wrong')
                    set_servo_position(90)
                entered_password = ''
                
                GPIO.output(row_pin, GPIO.HIGH)
            time.sleep(0.5)
        
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

