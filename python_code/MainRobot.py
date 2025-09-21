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

df['stop_sign'] = [0]
df['line_error'] = [0]
df.to_csv(csv_file_path, index = False)

def MainRobot():
    
    csv_file_path = '/home/pi/python_code/current.csv'
    df = pd.read_csv(csv_file_path)
    if (df['stop_sign'].astype(int) == 0).any():
        go()
    elif (df['stop_sign'].astype(int) == 1).any():
        stop()


def go():
    # 커브값을 배열로 저장
    global old_line
    global count
    #global count_turn
    #global previous_error
    #global integral

    line = Line.Line()
    
    rotate_big = 0.09
    rotate_small = 0.05
    time = 0.08

    if count == 0:
        count += 1
        line = [0, 1, 0]

    if line is [0, 1, 0]:  # 가운데 감지일 경우 직진
        motor.move(0.2, 0, time)
    elif line is [1, 0, 0] :  # 왼쪽 감지일 경우 왼쪽으로 회전
        motor.move(0.2, -(rotate_big), time)
    elif line is [1, 1, 0]:
        motor.move(0.2, -(rotate_small), time)
    elif line == [0, 0, 1]:  # 오른쪽 감지일 경우 오른쪽으로 회전
        motor.move(0.2, rotate_big, time)
    elif line == [0, 1, 1]:  # 오른쪽 감지일 경우 오른쪽으로 회전
        motor.move(0.2, rotate_small, time)
    else:
        motor.stop(0.1)
    print(line)
def stop():
    motor.stop(0.1)

# 시계방향 회전
def turn_cw():
    motor.turn(0.15,0,0.45)

# 반시계방향 회전
def trun_acw():
    motor.turn(0.15,1,0.45)

if __name__ == '__main__':
    while True:
        MainRobot()
    GPIO.cleanup()

#motor.stop(0.1)
GPIO.cleanup()







