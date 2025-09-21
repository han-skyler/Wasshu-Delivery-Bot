# QR 코드를 촬영하여 위치 보정

import cv2
from pyzbar.pyzbar import decode

# Firebase (pip install firebase-admin)
####################################################################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

PROJECT_ID = "cd-fc010"

cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://cd-fc010-default-rtdb.firebaseio.com/'})
ref_map = db.reference("")
####################################################################################

print("실행 중...")

def read_qr():
    old_x = 0
    old_y = 2

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray)

        for obj in decoded_objects:
            points = obj.polygon
            if len(points) > 4:
                hull = cv2.convexHull(points, clockwise=True)
                cv2.polylines(frame, [hull], True, (0, 255, 0), 2)

            qr_text = obj.data.decode("utf-8")
            x, y = qr_text.split(",")
            x_qr = int(x) * 105
            y_qr = int(y) * 100

            if old_x != x:
                ref_map.update({'x_new': x_qr})
                old_x = x
            if old_y != y:
                ref_map.update({'y_new': y_qr})
                old_y = y

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, qr_text, (points[0][0], points[0][1]), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('QR Code Reader', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("종료")
            break

    cap.release()
    cv2.destroyAllWindows()

read_qr()
