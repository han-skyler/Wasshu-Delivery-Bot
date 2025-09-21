#from MotorDriver import Motor
import MotorModule as motor
import GetCurve as gc
import RPi.GPIO as GPIO
import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'})
ref_map = db.reference("")

global motor
#motor = Motor(2, 3, 4, 22, 17, 27)
global zero_count
# 초기값설정
global old_line, count
old_line = [0, 0, 0]
count = 0
zero_count = 0

def find_line(old_line):
    print("I am finding the line...")
    
    if old_line == [0, 0, 1]:
        while True:
            print("finding... [0, 0, 1]")
            val = gc.LineTracking()
            line = gc.LineWrite(val)
            motor.move(0.2, -0.062, 0.1)
            # 이탈 방향으로 이동한 후 다시 라인을 찾을 때까지 대기
            if line == [0, 1, 0]:
                print("Line Found!")
                break

    elif old_line == [1, 0, 0]:
        while True:
            print("finding... [1, 0, 0]")
            val = gc.LineTracking()
            line = gc.LineWrite(val)
            motor.move(0.2, 0.062, 0.1)
            # 이탈 방향으로 이동한 후 다시 라인을 찾을 때까지 대기
            if line == [0, 1, 0]:
                time.sleep(0.3)
                print("Line Found!")
                break

def control(signal, reach):
    # 커브값을 배열로 저장
    global old_line
    global count
    global zero_count
    #motor = Motor(2, 3, 4, 22, 17, 27)
 
    val = gc.LineTracking()
    line = gc.LineWrite(val)
    
    # first starting value have error, so first value setting
    if count == 0:
        count += 1
        line = [0, 1, 0]
        # print(line)
    if line != [0, 0, 0]:
        old_line = line  # 값이 비정상적일 때를 대비해서 이전값 저장
        print(old_line)
    # 라인의 값이 비정상적인 경우
    elif line == [0, 0, 0]:
        line = old_line  # 비정상적인 경우 이전값 불러옴
        zero_count = zero_count + 1
        
        if zero_count >= 5:
            find_line(old_line)
            zero_count = 0
            
        elif zero_count >= 50:
            print("경로 이탈")
            motor.stop(1)
    else:
        pass


    if line == [0, 1, 0]:  # 가운데 감지일 경우 직진
        motor.move(0.2, 0, 0.1)
    elif line == [1, 0, 0]:  # 왼쪽 감지일 경우 왼쪽으로 회전
        motor.move(0.2, 0.073, 0.1)
    elif line == [1, 1, 0]:
        motor.move(0.2, 0.027, 0.1)
    elif line == [0, 0, 1]:  # 오른쪽 감지일 경우 오른쪽으로 회전
        motor.move(0.2, -0.073, 0.1)
    elif line == [0, 1, 1]:
        motor.move(0.2, -0.27, 0.1)
    elif line == [1, 1, 1]: # 교차로에 감지되었을 때
        print("cross!!! signal: ", signal, ", reach: ", reach)
        if signal == 1 and reach == 0:  # x값이 교차로에 도착하지 않았을 때
            print("1, 0")
            turn(signal)    # 시계 방향으로 회전
            time.sleep(0.6)
            old_line = [1, 0, 0]
            find_line(old_line)
            value = 1
            return value
        elif signal == -1 and reach == 0:
            print("-1, 0")
            turn(signal)    # 반시계 방향으로 회전
            time.sleep(0.6)
            old_line = [0, 0, 1]
            find_line(old_line)
            value = 1
            return value
        elif reach == 1 or reach == 2:
            print("Error: Not cross")
            stop(1)  # 교차로 이 외에서 감지되면 오류
        #ref_map.update({'x_new' : 170})
    elif line == [0, 0, 0]:
        stop()
    else:
        motor.stop(0.1)
        
    print(line)

def stop():
    motor.stop(0.1)

def turn(rotation):
    motor.turn(0.3, rotation, 0.8)  # speed, wise, time

if __name__ == '__main__':
    while True:
        control(1, 0)  #  signal, reach

#motor.stop(0.1)
GPIO.cleanup()






