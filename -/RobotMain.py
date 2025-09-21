import MotorModule as motor
import GetCurve as gc
import RPi.GPIO as GPIO

########################################
#global motor
#motor = Motor(2, 3, 4, 22, 17, 27)
########################################

# 초기값설정
global old_line, count, count_turn, previous_error, integral
old_line = [0, 0, 0]
count = 0
count_turn = 0
previous_error = 0
integral = 0


def control():
    # 커브값을 배열로 저장
    global old_line
    global count
    global count_turn
    global previous_error
    global integral

    val = gc.LineTracking()
    line = gc.LineWrite(val)

    if count == 0:
        count += 1
        line = [0, 1, 0]

        # print(line)
    if line != [0, 0, 0]:
        old_line = line  # 값이 비정상적일때를 대비해서 이전의 값을 저장해줌
        print(old_line)
    # 라인의 값이 비정상적인 경우
    elif line == [0, 0, 0]:
        line = old_line  # 비정상적인경우 이전의 값을 불러옴
    else:
        pass

    #####################PID method####################################
    s1, s2, s3 = line[0], line[1], line[2]
    sensor_value = s1*2000 + s2*1000 + s3*0
    target = 1000
    error = sensor_value - target
    derivative = error - previous_error
    integral = integral + error
    previous_error = error
    kp, ki, kd = 5.5, 1, 0
    max_s = 150
    power_difference = error * kp + integral*ki + derivative*kd

    if power_difference > max_s:
        power_difference = max_s
    if power_difference < -max_s:
        power_difference = -max_s

    if power_difference < 0:
        motor.move_pid(max_s+power_difference, max_s, 0.1)
    else:
        motor.move_pid(max_s, max_s+power_difference, 0.1)

    ###################################################################

    # if line == [0, 1, 0]:  # 가운데 감지일 경우 직진
    #     motor.move(-0.2, 0, 0.1)
    # elif line == [1, 0, 0]:  # 왼쪽 감지일 경우 왼쪽으로 회전
    #     motor.move(0.2, -0.2, 0.1)
    # elif line == [1, 1, 0]:
    #     motor.move(0.2, -0.2, 0.1)
    # elif line == [0, 0, 1]:  # 오른쪽 감지일 경우 오른쪽으로 회전
    #     motor.move(0.2, 0.2, 0.1)
    # elif line == [0, 1, 1]:
    #     motor.move(0.2, 0.2, 0.1)
    #
    # # elif line == [1,1,0]: # 왼쪽과 가운데를 감지 했을 경우
    # #    motor.turn(0.2,1,0.45) # 반시계 방향으로 회전
    # # elif line == [0,1,1]: # 가운데와 오른쪽이 감지됐을 경우
    # #    motor.turn(0.2,0,0.45) # 시계 방향으로 회전
    # # elif line == [1,1,1]:
    # #    motor.turn(0.15,1,0.45)
    # #    if count_turn == 0:
    # #        count_turn += 1
    # #    else:
    # #        motor.stop(0.1)
    # else:
    #     motor.stop(0.1)

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
        control()

#motor.stop(0.1)
GPIO.cleanup()





