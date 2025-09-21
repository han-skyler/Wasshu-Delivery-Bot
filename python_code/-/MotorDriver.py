# 모터 제어 테스트 코드
import RPi.GPIO as GPIO
from time import sleep

# from IRSensorReadEx import LineTracking as lt

# setmode, 워닝 비활성화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

global leftSpeed
global rightSpeed

# 모터제어 클래스 생성
class Motor():
    def __init__(self, EnaA, In1A, In2A, EnaB, In1B, In2B):
        # 활성화 핀 설정
        self.EnaA = EnaA
        self.In1A = In1A
        self.In2A = In2A

        self.EnaB = EnaB
        self.In1B = In1B
        self.In2B = In2B

        GPIO.setup(self.EnaA, GPIO.OUT)
        GPIO.setup(self.In1A, GPIO.OUT)
        GPIO.setup(self.In2A, GPIO.OUT)

        GPIO.setup(self.EnaB, GPIO.OUT)
        GPIO.setup(self.In1B, GPIO.OUT)
        GPIO.setup(self.In2B, GPIO.OUT)

        # pwm 지정
        self.pwmA = GPIO.PWM(self.EnaA, 100)
        self.pwmA.start(0)

        self.pwmB = GPIO.PWM(self.EnaB, 100)
        self.pwmB.start(0)

    def move(self, speed=0.2, turn=0, t=0):
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
            leftSpeed = -100

        # pwm은 음수값을 읽을 수 없으므로 절대값을 넣어줌
        self.pwmA.ChangeDutyCycle(abs(leftSpeed))
        self.pwmB.ChangeDutyCycle(abs(rightSpeed))

        # 값이 마이너스인지 확인하고 극성을 뒤집을 것임
        # 레프트 값이 양수이면 왼쪽으로 이동이라는 뜻
        if leftSpeed > 0:
            GPIO.output(self.In1A, GPIO.HIGH)
            GPIO.output(self.In2A, GPIO.LOW)
            # print("LO ")
        else:
            GPIO.output(self.In1A, GPIO.LOW)
            GPIO.output(self.In2A, GPIO.HIGH)
            # print("LX ")

        if rightSpeed > 0:
            GPIO.output(self.In1B, GPIO.HIGH)
            GPIO.output(self.In2B, GPIO.LOW)
            # print("RO ")
        else:
            GPIO.output(self.In1B, GPIO.LOW)
            GPIO.output(self.In2B, GPIO.HIGH)
            # print("RX ")

        # sleep 시간 지정
        sleep(t)

    def move_pid(self, leftSpeed=0.2, rightSpeed=0.2, t=0.1):
        GPIO.setmode(GPIO.BCM)
        # speed와 turn에 100을 곱해줌 (듀티사이클)
        #global leftSpeed
        #global rightSpeed
        leftSpeed *= 100
        rightSpeed *= 100
        
        #turn *= 100

        #temp = 0
        max_speed = 150
        
        if leftSpeed > 100:
            leftSpeed = 100
        elif leftSpeed < -100:
            leftSpeed = -100
        if rightSpeed > 100:
            rightSpeed = 100
        elif rightSpeed < -100:
            leftSpeed = -100
        
        # pwm은 음수값을 읽을 수 없으므로 절대값을 넣어줌
        self.pwmA.ChangeDutyCycle(abs(leftSpeed))
        self.pwmB.ChangeDutyCycle(abs(rightSpeed))

        GPIO.output(self.In1A, GPIO.HIGH)
        GPIO.output(self.In2A, GPIO.LOW)

        GPIO.output(self.In1B, GPIO.HIGH)
        GPIO.output(self.In2B, GPIO.LOW)

        # turn 값을 넣어줌
        # speed 값을 -100 ~ 100 범위로 정의하여 방향을 지정하도록 하였음
        # 음수 값은 왼쪽으로 이동
        # 양수 값은 오른쪽으로 이동
        # leftSpeed = speed - turn
        # rightSpeed = speed + turn
        #
        # # 범위를 벗어나지 않도록 값 지정
        # if leftSpeed > 100:
        #     leftSpeed = 100
        # elif leftSpeed < -100:
        #     leftSpeed = -100
        # if rightSpeed > 100:
        #     rightSpeed = 100
        # elif rightSpeed < -100:
        #     leftSpeed = -100


        # 값이 마이너스인지 확인하고 극성을 뒤집을 것임
        # 레프트 값이 양수이면 왼쪽으로 이동이라는 뜻
        # if leftSpeed > 0:
        #     GPIO.output(self.In1A, GPIO.HIGH)
        #     GPIO.output(self.In2A, GPIO.LOW)
        #     # print("LO ")
        # else:
        #     GPIO.output(self.In1A, GPIO.LOW)
        #     GPIO.output(self.In2A, GPIO.HIGH)
        #     # print("LX ")
        #
        # if rightSpeed > 0:
        #     GPIO.output(self.In1B, GPIO.HIGH)
        #     GPIO.output(self.In2B, GPIO.LOW)
        #     # print("RO ")
        # else:
        #     GPIO.output(self.In1B, GPIO.LOW)
        #     GPIO.output(self.In2B, GPIO.HIGH)
        #     # print("RX ")

        # sleep 시간 지정
        sleep(t)

    def turn(self, speed=0.5, wise=0, time=0):  # 0 means clockwise, 1 means anticlock
        speed *= 100
        self.pwmA.ChangeDutyCycle(speed)
        self.pwmB.ChangeDutyCycle(speed)

        # 시계 방향일때
        if wise == 0:
            GPIO.output(self.In1A, GPIO.LOW)
            GPIO.output(self.In2A, GPIO.HIGH)
            GPIO.output(self.In1B, GPIO.HIGH)
            GPIO.output(self.In2B, GPIO.LOW)

        # 반시계 방향일때
        elif wise == 1:
            GPIO.output(self.In1A, GPIO.HIGH)
            GPIO.output(self.In2A, GPIO.LOW)
            GPIO.output(self.In1B, GPIO.LOW)
            GPIO.output(self.In2B, GPIO.HIGH)

        sleep(time)

    def stop(self, t):
        # 정지
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB.ChangeDutyCycle(0)

        sleep(t)


def main():
    # move_(speed, time)
    motor1.move(0.2, -0.1, 2)
    motor1.stop(1)

    motor1.move(0.2, 0.1, 2)
    motor1.stop(1)


if __name__ == '__main__':
    # Motor(EnaA, In1A, In2A, EnaB, In1B, In2B)
    motor1 = Motor(2, 3, 4, 22, 17, 27)
    # motor1 = Motor(17, 27, 6, 13, 19, 26)
    main()
    GPIO.cleanup()








