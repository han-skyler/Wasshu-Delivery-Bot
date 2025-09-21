"""
YOLOv5의 서버 값을 읽어오는 코드

사람이 있을 경우 정지한다.

사람이 있을 경우
stop_sign = 1 (True)

사람이 없을 경우
stop_sign = 0 (False)
"""
# 필요한 라이브러리 임포트
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import csv
import pandas as pd

# 파이어베이스 설정
cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")

firebase_admin.initialize_app(cred, {'databaseURL': 'https://cd-fc010-default-rtdb.firebaseio.com/'}, name='RTD')
RTD = firebase_admin.get_app('RTD')
db_RTD = firebase_admin.db.reference(app=RTD)

yolo = db_RTD.child('yolo').get()  # 1: 사람O, 0: 사람X

csv_file_path = '/home/pi/python_code/current.csv'

# CSV 파일 읽기
df = pd.read_csv(csv_file_path)

if (yolo == 1): # 사람이 있을 경우
    df['stop_sign'] = [1] # true
    df.to_csv(csv_file_path, index = False)
elif (yolo == 0): # 사람이 없을 경
    df['stop_sign'] = [0] # false
    df.to_csv(csv_file_path, index = False)

df.to_csv('current.csv', index=False)
