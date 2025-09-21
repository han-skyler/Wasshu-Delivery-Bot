import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db
import RobotMain2 as robot

PROJECT_ID = "cd-fc010"
cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")

firebase_admin.initialize_app(cred, name='yolo_app')
yolo_app = firebase_admin.get_app('yolo_app')
yolo_db = firestore.client(app=yolo_app)
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'}, name='xy_app')
xy_app = firebase_admin.get_app('xy_app')
xy_db = firebase_admin.db.reference(app=xy_app)

# Android APP - destination
x = xy_db.child('MAP').child('destination').child('x').get()
y = xy_db.child('MAP').child('destination').child('y').get()
print('Destination')
print('x:', x, ', y:', y)

# WiFi fingerprint - current
ref_x_new = xy_db.child('MAP').child('current')
ref_y_new = xy_db.child('MAP').child('current')
global x_new
global y_new

# jetson nano - YOLOv5
col_yolo = yolo_db.collection(u'WHATHU')
global value_yolo
#print('x_new:', x_new, ', y_new:', y_new)

import threading

def periodic_function():
    # jetson nano - YOLOv5
    global x_new
    global y_new
    global value_yolo
    ref_yolo = col_yolo.document(u'YOLOv5').get()
    value_yolo = ref_yolo.to_dict()['class']
    x_new = ref_x_new.child('x_new').get()
    y_new = ref_y_new.child('y_new').get()
    #print("yolov5: ", value_yolo)
    print("{}, {}".format(x_new, y_new))

def schedule_execution():
    periodic_function()  # 최초 실행

    interval = 4  # 실행 간격 (초)
    threading.Timer(interval, schedule_execution).start()

################################### Line Tracking Start
while True:
    schedule_execution()  # 주기적 실행 시작
    
    if (x_new - 5 <= x and x <= x_new + 5) and (y_new - 5 <= y and y <= y_new + 5):
        # Robot Stop and Come back (0, 0)
        print("Robot Stop and Come back...")
        robot.stop() # 로봇 stop
        #break
    else:
        print("Robot Moving...")
        if value_yolo == 0:
            print("I think I didn't detected human.")
            if x > 0 and x < 700:
                robot.control() # 로봇 직진 # 복도까지
            elif x == 700:
                if y_new < 0:
                    if y_old > y_new:
                        # 반시계방향 90도 회전
                        robot.turn_acw()
                elif y_new > 0:
                    if y_old < y_new:
                        # 시계방향 90도 회전
                        robot.turn_cw()
                y_old = y_new
        else:
            print("I detected human.")
            # Robot Stop
            robot.stop()
