# 모터 제어 테스트 코드
import RPi.GPIO as GPIO
from time import sleep

# from IRSensorReadEx import LineTracking as lt

# setmode, 워닝 비활성화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# (2, 3, 4, 22, 17, 27)

EnaA = 2
In1A = 3
In2A = 4

EnaB = 22
In1B = 17
In2B = 27

GPIO.setup(EnaA, GPIO.OUT)
GPIO.setup(In1A, GPIO.OUT)
GPIO.setup(In2A, GPIO.OUT)

GPIO.setup(EnaB, GPIO.OUT)
GPIO.setup(In1B, GPIO.OUT)
GPIO.setup(In2B, GPIO.OUT)

pwmA = GPIO.PWM(EnaA, 100)
pwmA.start(0)

pwmB = GPIO.PWM(EnaB, 100)
pwmB.start(0)

global leftSpeed
global rightSpeed


def move(speed=0.2, turn=0, t=000.1):
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(EnaA, GPIO.OUT)
    GPIO.setup(In1A, GPIO.OUT)
    GPIO.setup(In2A, GPIO.OUT)

    GPIO.setup(EnaB, GPIO.OUT)
    GPIO.setup(In1B, GPIO.OUT)
    GPIO.setup(In2B, GPIO.OUT)

    # speed와 turn에 100을 곱해줌 (듀티사이클)
    speed *= 100
    turn *= 100

    temp = 0

    # turn 값을 넣어줌
    # speed 값을 -100 ~ 100 범위로 정의하여 방향을 지정하도록 하였음
    # 음수 값은 왼쪽으로 이동
    # 양수 값은 오른쪽으로 이동
    leftSpeed = speed - turn
    rightSpeed = speed + turn

    # 범위를 벗어나지 않도록 값 지정
    if leftSpeed > 100:
        leftSpeed = 100
    elif leftSpeed < -100:
        leftSpeed = -100

    if rightSpeed > 100:
        rightSpeed = 100
    elif rightSpeed < -100:
        rightSpeed = -100

    # pwm은 음수값을 읽을 수 없으므로 절대값을 넣어줌
    pwmA.ChangeDutyCycle(abs(leftSpeed))
    pwmB.ChangeDutyCycle(abs(rightSpeed))

    # 값이 마이너스인지 확인하고 극성을 뒤집을 것임
    # 레프트 값이 양수이면 왼쪽으로 이동이라는 뜻

    if leftSpeed > 0:
        GPIO.output(In1A, GPIO.HIGH)
        GPIO.output(In2A, GPIO.LOW)
    elif leftSpeed < 0:
        GPIO.output(In1A, GPIO.LOW)
        GPIO.output(In2A, GPIO.HIGH)

    if rightSpeed > 0:
        GPIO.output(In1B, GPIO.HIGH)
        GPIO.output(In2B, GPIO.LOW)
    elif rightSpeed < 0:
        GPIO.output(In1B, GPIO.LOW)
        GPIO.output(In2B, GPIO.HIGH)

    # sleep 시간 지정
    sleep(t)


def turn(speed=0.5, wise=0, time=0):  # 0 means clockwise, 1 means anticlock
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(EnaA, GPIO.OUT)
    GPIO.setup(In1A, GPIO.OUT)
    GPIO.setup(In2A, GPIO.OUT)

    GPIO.setup(EnaB, GPIO.OUT)
    GPIO.setup(In1B, GPIO.OUT)
    GPIO.setup(In2B, GPIO.OUT)

    speed *= 100
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)

    # anti clock wise
    if wise == -1:
        GPIO.output(In1A, GPIO.LOW)
        GPIO.output(In2A, GPIO.HIGH)
        GPIO.output(In1B, GPIO.HIGH)
        GPIO.output(In2B, GPIO.LOW)

    # clock wise
    elif wise == 1:
        GPIO.output(In1A, GPIO.HIGH)
        GPIO.output(In2A, GPIO.LOW)
        GPIO.output(In1B, GPIO.LOW)
        GPIO.output(In2B, GPIO.HIGH)

    sleep(time)


def stop(t=1):
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(EnaA, GPIO.OUT)
    GPIO.setup(In1A, GPIO.OUT)
    GPIO.setup(In2A, GPIO.OUT)

    GPIO.setup(EnaB, GPIO.OUT)
    GPIO.setup(In1B, GPIO.OUT)
    GPIO.setup(In2B, GPIO.OUT)

    # 정지
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

    GPIO.output(In1A, GPIO.LOW)
    GPIO.output(In2A, GPIO.LOW)
    GPIO.output(In1B, GPIO.LOW)
    GPIO.output(In2B, GPIO.LOW)

    sleep(t)


def main():
    # move_(speed, time)
    # turn(0.3,0,2)
    stop(1)


if __name__ == '__main__':
    main()
    GPIO.cleanup()










