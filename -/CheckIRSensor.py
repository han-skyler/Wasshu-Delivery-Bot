import time
import pyfirmata as pf

# 아두이노 연결
board = pf.Arduino('/dev/ttyACM0')

pf.util.Iterator(board).start()
board.analog[0].enable_reporting()

# 아날로그 핀 설정
# a : analog / d : digital signal
# 숫자 : 아날로그 핀 넘버
# i : input / o : output
s0 = board.get_pin('a:1:i')
s1 = board.get_pin('a:2:i')
s2 = board.get_pin('a:3:i')

# 이전의 라인정보를 저장해줌
old_line = [0, 0, 0]


def LineTracking():
    # 아날로그 값 저장
    val = [0, 0, 0]
    val[0] = s0.read()
    val[1] = s1.read()
    val[2] = s2.read()

    # 초기값이 None으로 들어오기 때문에
    # None값일 경우 0으로 설정
    if val[0] == None:
        val[0] = 0
    if val[1] == None:
        val[1] = 0
    if val[2] == None:
        val[2] = 0

    # 정규화
    val[0] = val[0] * 100000 / 245
    val[1] = val[1] * 100000 / 245
    val[2] = val[2] * 100000 / 245

    # 정수로 변환
    val[0] = int(val[0])
    val[1] = int(val[1])
    val[2] = int(val[2])

    return val


def MinIndex():
    v0, v1, v2 = LineTracking()
    val = [v0, v1, v2]

    min_val = min(val)
    min_index = val.index(min_val) + 1

    if v0 > 90 and v1 > 90 and v2 > 90:
        min_index = 4

    return min_index


def LineWrite(v0, v1, v2):
    line = [0, 0, 0]

    # 라인센서가 일정 값 이하일 경우 검은선을 인지했다고 설정
    # v1은 가운데 센서이므로 값을 더 민감하게 받도록 설정
    if v0 <= 75: line[0] = 1
    if v1 <= 95: line[1] = 1
    if v2 <= 75: line[2] = 1

    return line


def LineSave(line):
    # 라인의 값을 저장
    old_line = line.copy()

    return old_line


# def clockwise(line):
# if line == [1,1,0]: clockwise
# elif line == [0,1,1]: anticlockwise
# elif line == [1,1,1]:

if __name__ == '__main__':
    while True:
        v0, v1, v2 = LineTracking()
        line = LineWrite(v0, v1, v2)

        # 라인의 값이 정상적으로 읽어졌을경우
        #if line != [0, 0, 0]:
        #    old_line = LineSave(line)
        # 라인의 값이 비정상적인 경우
        #elif line == [0, 0, 0]:
        #    line = old_line
        #    print("old")
        #else:
        #    pass
        print("v0:",v0,"v1:",v1,"v2:",v2)
        #print(line[0], line[1], line[2])
        # index = MinIndex(v0, v1, v2)
        # print("S0 : ", v0)
        # print("S1 : ", v1)
        # print("S2 : ", v2)
        # print(" ")
        # print("min index : ", index)

        time.sleep(0.2)


