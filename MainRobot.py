"""
메인 로봇 주행 코드

시그널이 1인 경우, 모터가 정지한다
stop_sign = 1 (True)

시그널이 0인 경우, 정상 주행한다
stop_sign = 0 (False)
"""

import GetMotor as motor
import GetLine as Line
import RPi.GPIO as GPIO
import csv
import pandas as pd
import time

########################################
#global motor
#motor = Motor(2, 3, 4, 22, 17, 27)
########################################

# 초기값설정
global old_line, count, count_turn, previous_error, integral
old_line = [0, 0, 0]
count = 0
#count_turn = 0
#previous_error = 0
#integral = 0

# CSV 파일 읽기
csv_file_path = '/home/pi/python_code/current.csv'
df = pd.read_csv(csv_file_path)

# 정지 신호를 의미 
# 0 = 주행 1 = 정지
df['stop_sign'] = 0

# 라인의 누적 에러값을 표시  
df['line_error'] = 0
df['rotate'] = df['rotate'].astype(float)
df['rotate'] = 0.053
df['clockwise'] = 0
df.to_csv(csv_file_path, index = False)

def MainRobot():
    csv_file_path = '/home/pi/python_code/current.csv'
    df = pd.read_csv(csv_file_path)
    if (df['stop_sign'].astype(int) == 0).any():
        go()
    elif (df['stop_sign'].astype(int) == 1).any():
        stop()
        if(df['clockwise'].astype(int) == 1).any():
            # 시계 방향으로 회전
            clockwise(1)
        elif(df['clockwise'].astype(int) == 2).any():
            # 반시계 방향으로 회전
            clockwise(2)


def go():
    # 커브값을 배열로 저장
    global old_line
    global count
    global rotate

    line = Line.Line()
    
    csv_file_path = '/home/pi/python_code/current.csv'
    df = pd.read_csv(csv_file_path)

    rotate = df.iloc[0,df.columns.get_loc('rotate')].astype(float) # 로봇의 회전 각도를 csv파일에서 받아옴
    rotate = float(rotate)
    time = 0.1   # 모터 작동 시간 0.08초
    speed = 0.2   # 로봇의 속도
    print()

    if count == 0:
        count += 1
        line = [0, 1, 0]
        
    if line == [0, 1, 0]:  # 가운데 감지일 경우 직진
        motor.move(speed, 0, time)
    elif line == [1, 0, 0] or line == [1, 1, 0]:  # 왼쪽 감지일 경우 왼쪽으로 회전
        motor.move(speed, -(rotate), time)
    elif line == [0, 0, 1] or line == [0, 1, 1]:  # 오른쪽 감지일 경우 오른쪽으로 회전
        motor.move(speed, rotate, time)
    else:
        motor.stop(time)
        
    print(line)
def stop():
    motor.stop(0.1)

# 시계방향 회전
def clockwise(direction):
    while True:
        line = Line.Line()
        if line == [0,0,0] or line == [1,1,1] or line == [1,0,1]:
            motor.turn(0.4,direction,0.5)
        else:
            print("----------------------방향을 바꿨습니다-----------------------")
            df = pd.read_csv(csv_file_path)
            df['line_error'] = 0 # error값 초기화
            df['stop_sign'] = 0 # 모터 움직임
            df.to_csv(csv_file_path, index = False)
            break
        time.sleep(1)
        

if __name__ == '__main__':
    while True:
        MainRobot()
    GPIO.cleanup()

#motor.stop(0.1)
GPIO.cleanup()







