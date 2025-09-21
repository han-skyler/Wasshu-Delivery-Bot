import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db

PROJECT_ID = "cd-fc010"
cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")

firebase_admin.initialize_app(cred, name='yolo_app')
yolo_app = firebase_admin.get_app('yolo_app')
yolo_db = firestore.client(app=yolo_app)
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'}, name='xy_app')
xy_app = firebase_admin.get_app('xy_app')
xy_db = firebase_admin.db.reference(app=xy_app)

# WiFi fingerprint - current
ref_x_new = xy_db.child('MAP').child('current')
ref_y_new = xy_db.child('MAP').child('current')
x_new = ref_x_new.child('x_new').get()
y_new = ref_y_new.child('y_new').get()

# jetson nano - YOLOv5
ref_yolo = yolo_db.collection(u'WHATHU').document(u'YOLOv5').get()
value_yolo = ref_yolo.to_dict()['class']

print("yolov5: ", value_yolo)


