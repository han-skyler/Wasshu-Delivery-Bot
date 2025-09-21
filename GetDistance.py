"""
HC-SR04 초음파 센서를 이용하여 물체와 거리 구하는 코드

장애물 있을 경우 정지한다.

장애물이 있을 경우
stop_sign = 1 (True)

장애물이 없을 경우
stop_sign = 0 (False)
"""

import RPi.GPIO as GPIO
import time
import csv
import pandas as pd

#GPIO 핀 설정
echo1 = 14
trig1 = 15
echo2 = 23
trig2 = 24
echo3 = 25
trig3 = 8

#GPIO 핀 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#초음파 센서와 연결된 핀을 입력 또는 출력으로 설정
GPIO.setup(echo1, GPIO.IN)
GPIO.setup(trig1, GPIO.OUT)
GPIO.setup(echo2, GPIO.IN)
GPIO.setup(trig2, GPIO.OUT)
GPIO.setup(echo3, GPIO.IN)
GPIO.setup(trig3, GPIO.OUT)

# CSV 파일 읽기
csv_file_path = '/home/pi/python_code/current.csv'
df = pd.read_csv(csv_file_path)

distance = [0, 0, 0]

def Distance():
    distance[0] = get_distance(trig1, echo1)
    distance[1] = get_distance(trig2, echo2)
    distance[2] = get_distance(trig3, echo3)
    
    if distance[0] < 50 or distance[1] < 50 or distance[2] < 50:
         df['stop_sign'] = [1]
         print("[거리 센서] 정지 명령 실행")
    else:
        df['stop_sign'] = [0]
        print("[거리 센서] 모터 작동")

    print(f"거리 센서 1: {distance[0]} cm")
    print(f"거리 센서 2: {distance[1]} cm")
    print(f"거리 센서 3: {distance[2]} cm")
    print("------------------------")

#초음파 센서 거리 측정 함수
def get_distance(trig, echo):
    # 초음파 트리거 핀을 활성화
    GPIO.output(trig, True)
    time.sleep(0.000001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

    # 에코 핀이 상승할 때까지 대기
    while GPIO.input(echo) == 0:
        start_time = time.time()

    # 에코 핀이 하락할 때까지 대기
    while GPIO.input(echo) == 1:
        stop_time = time.time()

    # 초음파 파울스의 이동 시간 계산
    elapsed_time = stop_time - start_time

    # 소리의 속도(34300 cm/s)를 사용하여 거리 계산
    distance = (elapsed_time * 34300) / 2
    
    if distance > 300 :
        distance = 300
    elif distance < 0 :
        distance = 0

    return int(distance)

try:
    while True:
        Distance()
        time.sleep(1)
        
except KeyboardInterrupt:
    GPIO.cleanup()

