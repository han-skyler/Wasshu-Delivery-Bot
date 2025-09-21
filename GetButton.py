# 필요한 라이브러리 임포트
import RPi.GPIO as GPIO 
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import csv
import pandas as pd

# 파이어베이스 설정
PROJECT_ID = "cd-fc010"

cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://cd-fc010-default-rtdb.firebaseio.com/'})
ref_map = db.reference("")

delivery_state = db.reference("")
state = 4

# button_callback 함수를 정의
def button_callback(channel):
    delivery_state.update({'delivery_state': state})

# 사용할 GPIO핀의 번호를 설정
button_pin = 12

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

# Event 방식으로 핀의 Rising 신호를 감지하면 button_callback 함수를 실행
GPIO.add_event_detect(button_pin,GPIO.RISING,callback=button_callback)

while 1:
     time.sleep(0.1) # 0.1초 딜레이
