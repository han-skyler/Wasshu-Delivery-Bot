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
global save_line, count
save_line = [0, 0, 0]
start_count = 0
zero_count = 0

# def find_line(old_line):
#     print("I am finding the line...")
#     if old_line == [0, 0, 1]:
#         while True:
#             print("finding... [0, 0, 1]")
#             val = gc.LineTracking()
#             line = gc.LineWrite(val)
#             motor.move(0.2, -0.062, 0.1)
#             # 이탈 방향으로 이동한 후 다시 라인을 찾을 때까지 대기
#             if line == [0, 1, 0]:
#                 print("Line Found!")
#                 break

#     elif old_line == [1, 0, 0]:
#         while True:
#             print("finding... [1, 0, 0]")
#             val = gc.LineTracking()
#             line = gc.LineWrite(val)
#             motor.move(0.2, 0.062, 0.1)
#             # 이탈 방향으로 이동한 후 다시 라인을 찾을 때까지 대기
#             if line == [0, 1, 0]:
#                 time.sleep(0.3)
#                 print("Line Found!")
#                 break




def control(signal, reach):
    # 커브값을 배열로 저장
    global save_line
    global start_count
    global zero_count
    #motor = Motor(2, 3, 4, 22, 17, 27)

    val = gc.LineTracking()
    line = gc.LineWrite(val)
    
    # 처음 시작할때 값을 정상적으로 받아오기 위한 초기화
    if start_count == 0:
        start_count += 1
        line = [0, 1, 0]

    ####### 라인 값이 비 정상적일 때를 위한 코드 ########       
    # [ 비정상적인 값 ]
    # line = [0, 0, 0] [1, 1, 1] [1, 0, 1]

    if line == [0, 0, 0]:
        zero_count += 1
        line = save_line
    elif line != [1, 1, 1] or line != [1, 0, 1] or line != [0, 0, 0] :
        save_line = line # 정상적인 값이 들어왔을 때 save_line에 저장(백업)
        zero_count = 0

    ###################################################        [ zero_count 기준 ]
    #######  zero_count가 계속 될 경우를 위한 코드  #######        * zero_count <= 3 : 센서값 오류 일 수도 있음
    ###################################################        * 3 < zero_count <= 15 : 경로 재탐색 
    ###################################################        * 15 < zero_count : 오류, 정지함    

    if zero_count <= 3:
        # line에 저장(백업)해둔 라인코드를 불러온다
        line = save_line
    elif 3 < zero_count and zero_count <= 35:
        while line == [1, 1, 1] or line == [1, 0, 1] or line == [0, 0, 0]:
            print("----------------CHECK!!!----------------")
            print(zero_count,"\n")
            line [0] = save_line[2]
            line [1] = save_line[1]
            line [2] = save_line[0]
            val = gc.LineTracking()
            line = gc.LineWrite(val)
    elif 35 < zero_count:
        print("--------------------------------")
        print("------------경로 이탈------------")
        print("--------------------------------")
        motor.stop(1)
    

    #if line != [0, 0, 0]:
    #    save_line = line  # 값이 비정상적일 때를 대비해서 이전값 저장
    #    print(save_line)
    # 라인의 값이 비정상적인 경우
    #elif line == [0, 0, 0]:
    #    line = save_line  # 비정상적인 경우 이전값 불러옴
    #    zero_count = zero_count + 1
        
    #    if zero_count >= 5:
    #        find_line(save_line)
    #        zero_count = 0
            
    #    elif zero_count >= 50:
    #        print("경로 이탈")
    #        motor.stop(1)
    #else:
    #    pass


    if line == [0, 1, 0]:  # 가운데 감지일 경우 직진
        motor.move(0.2, 0, 0.1)
        zero_count = 0
    elif line == [1, 0, 0]:  # 왼쪽 감지일 경우 왼쪽으로 회전
        motor.move(0.2, 0.073, 0.1)
        zero_count = 0
    elif line == [1, 1, 0]:
        motor.move(0.2, 0.027, 0.1)
        zero_count = 0
    elif line == [0, 0, 1]:  # 오른쪽 감지일 경우 오른쪽으로 회전
        motor.move(0.2, -0.073, 0.1)
        zero_count = 0
    elif line == [0, 1, 1]:
        motor.move(0.2, -0.27, 0.1)
        zero_count = 0
    elif line == [1, 1, 1]: # 교차로에 감지되었을 때
        print("\n------------------------------------------------")
        print("교차로 signal: ", signal, ", reach: ", reach)
        print("------------------------------------------------\n")
        if reach == 1 or reach == 2:
            print("Error: 교차로가 아니에요")
            stop(1)  # 교차로 이 외에서 감지되면 오류
        elif signal == 1 and reach == 0:  # x값이 교차로에 도착하지 않았을 때
            motor.move(0.2,0.1,0.6)
            line = [1, 1, 0] # 일부러 반대 값 저장
            #print("1, 0")
            #turn(signal)    # 시계 방향으로 회전
            #time.sleep(0.6)
            #save_line = [1, 0, 0]
            #find_line(save_line)
            value = 1
            return value
        elif signal == -1 and reach == 0:
            motor.move(0.2,-0.1,0.6)
            line = [0 ,1, 1] # 일부러 반대 값 저장
            #print("-1, 0")
            #turn(signal)    # 반시계 방향으로 회전
            #time.sleep(0.6)
            #save_line = [0, 0, 1]
            #find_line(save_line)
            value = 1
            return value
        
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
    
import signal
import sys

def keyboard_interrupt_handler(signal, frame):
    print("키보드 인터럽트 발생")
    stop()
    sys.exit(0)

if __name__ == '__main__':
    while True:
        control(1, 0)  #  signal, reach

#motor.stop(0.1)
GPIO.cleanup()






