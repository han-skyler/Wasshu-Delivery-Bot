import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db
import JiyunMain as robot
import threading
import pandas as pd

PROJECT_ID = "cd-fc010"
cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
ref_map = db.reference("")

# RTD라는 이름으로 Firebase 앱을 초기화
# databaseURL은 'https://cd-fc010-default-rtdb.firebaseio.com/'
firebase_admin.initialize_app(cred, {'databaseURL': 'https://cd-fc010-default-rtdb.firebaseio.com/'}, name='RTD')
RTD = firebase_admin.get_app('RTD')             # RTD 이름으로 초기화된 Firebase 앱 가져옴
db_RTD = firebase_admin.db.reference(app=RTD)   # RTD 앱을 사용하여 Firebase실시간 데인터베이스에 대한 참조를 만듬

global x_new       # 현재 x
global y_new       # 현재 y
global value_yolo  # 인식된 사람 수
global reach       # 도착 했는지 감지 reach = 1 : x도착 / reach = 2 : y 도착
reach = 0          # 초기화 값
global signal      # 도착지 방향에 대한 감지 1 : 시계방향 -1 : 반시계방향

# 안드로이드 어플에서 받아온 좌표로 목적지 설정
x = db_RTD.child('x').get()
y = db_RTD.child('y').get()
print('목적지')
print('x:', x, ', y:', y)

if y < 0:
    signal = -1  # 반시계방향
else:
    signal = 1   # 시계방향

# WiFi fingerprint - current
#ref_x_new = db_RTD.child('x_new')
#ref_y_new = db_RTD.child('y_new')

# jetson nano - YOLOv5
ref_yolo = db_RTD.child('yolo')
value_yolo = ref_yolo.get()

def load_firebase():
    # jetson nano - YOLOv5
    global x_new
    global y_new
    global value_yolo
    
    value_yolo = ref_yolo.get()
    #x_new = ref_x_new.get()
    #y_new = ref_y_new.get()
    df = pd.read_csv('/home/pi/python_code/current.csv')
    x_new = int(df['x'].values[0])
    y_new = int(df['y'].values[0])
    #print("yolov5: ", value_yolo)
    #print("{}, {}".format(x_new, y_new))

def schedule_execution():
    load_firebase()

    interval = 4  # 실행 간격 (초)
    threading.Timer(interval, schedule_execution).start()

def check():  # Checking destination
    global reach

    if (reach == 1) and (y_new - 10 <= y and y <= y_new + 10):
        reach = 2
    
    if reach == 0:
        print("교차로 이동 중... ", end=" ")

################################### Line Tracking Start

def main():
    global reach
    load_firebase()
    check()
    
    # Checking destination
    if (reach == 2):
        # Robot Stop and Come back (0, 0)
        print("목적지에 도착. ", end=" ")
        robot.stop() # 로봇 stop
        #break
    
    # Finding destination
    else:
        print("로봇이 움직임. ", end=" ")
        
        # Checking human
        if value_yolo == 0:
            print("사람 감지x. ", end=" ")
            robot.control(signal, reach)
            print(signal, reach)
            if robot.control(signal, reach) == 1:
                print("x_new = 170")
                ref_map.update({'x_new' : 170})
                reach = 1
            
        else:
            print("사람 감지o. ", end=" ")
            # Robot Stop
            robot.stop()

while True:
    #schedule_execution()  # Firebase
    main()
            