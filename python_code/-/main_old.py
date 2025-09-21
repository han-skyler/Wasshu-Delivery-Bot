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

#print('x_new:', x_new, ', y_new:', y_new)


################################### Line Tracking Start
while True:
    # jetson nano - YOLOv5
    ref_yolo = yolo_db.collection(u'WHATHU').document(u'YOLOv5').get()
    value_yolo = ref_yolo.to_dict()['class']
    x_new = ref_x_new.child('x_new').get()
    y_new = ref_y_new.child('y_new').get()
    #print("yolov5: ", value_yolo)
    
    if x == x_new and y == y_new:
        # Robot Stop and Come back (0, 0)
        print("Robot Stop and Come back...")
        robot.stop() # 로봇 stop
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
