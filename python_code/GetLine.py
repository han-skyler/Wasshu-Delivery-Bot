import time
import pyfirmata as pf
import pandas as pd
import csv

csv_file_path = '/home/pi/python_code/current.csv'
df = pd.read_csv(csv_file_path)
df['line_error'] = [0]
df.to_csv(csv_file_path, index = False)

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

# 이전의 정상적인 라인 값 저장
global line_before
line_before = [0, 0, 0] # 초기화

def Line():
    ########### 라인코드 ###########
    global line_before
    line = LineSet() # [0,1,0]과 같은 형태로 값이 출력됨

    #line의 값이 정상적인지 확인
    if line != [0, 0, 0] and line !=[1, 0, 1] and line != [1,1,1]:
        #line_before = line # 정상일 경우, 이전의 라인 값을 저장
        LineSave(line)
    else:   # 라인의 값에 오류 값이 들어올 경우
        line = LineError(line)
        
    #print(line)
    return line

def LineSet():
    # 초기에 들어오는 센서의 값을 감지
    val = [0, 0, 0]
    val[0] = s0.read()
    val[1] = s1.read()
    val[2] = s2.read()

    # 초기값이 None으로 들어오기 때문에
    # None값일 경우 0으로 설정
    if val[0] is None:
        val[0] = 0
    if val[1] is None:
        val[1] = 0
    if val[2] is None:
        val[2] = 0

    ############## 라인센서 전처리 ###############
    # 정규화
    val[0] = val[0] * 100000 / 252
    val[1] = val[1] * 100000 / 252
    val[2] = val[2] * 100000 / 252

    # 4비트 정수로 변환
    val[0] = int(val[0])
    val[1] = int(val[1])
    val[2] = int(val[2])

    line = LineVal(val)

    return line

def LineVal(line):
    ########### 라인값 0,1 변환 ###########
    ########### 0 = 라인 X ###############
    ########### 1 = 라인 O ###############

    # 라인센서가 일정 값 이하일 경우 검은선을 인지했다고 설정
    # v1은 가운데 센서이므로 값을 더 민감하게 받도록 설정
    # 현재 임계값 : 75

    if line[0] <= 75 : line[0] = 1
    else: line[0] = 0
    if line[1] <= 75: line[1] = 1
    else: line[1] = 0
    if line[2] <= 75: line[2] = 1
    else: line[2] = 0

    return line

# 라인의 값이 정상적일 경우 실행됨
def LineSave(line):
    global line_before
    df = pd.read_csv(csv_file_path)
    df['line_error'] = 0 # error값 초기화
    df.to_csv(csv_file_path, index = False)
    line_before = line  # 정상일 경우, 이전의 라인 값을 저장
    #print("Line Save : ",line_before)

def LineError(line):
    global line_before
    #print("Line Error : ",line)
    df = pd.read_csv(csv_file_path)
    df['line_error'] = df['line_error'] + 1 # error값 추가
    df.to_csv(csv_file_path, index = False)
    #print(df['line_error'].tolist())
    
    print("ERROR : ", line)
    if (df['line_error'].astype(int) == 3).any():
        line_before = LineChange(line_before)
        line = line_before
    elif(df['line_error'].astype(int) == 33).any():
        line_before = LineChange(line_before)
        line = line_before
    elif(df['line_error'].astype(int) == 63).any():
        line_before = LineChange(line_before)
        line = line_before
        df['stop_sign'] = [1]
        df.to_csv(csv_file_path, index = False)
    else:
        line = line_before
        
    return line
    
def LineChange(line):
    
    if line == [0,1,0]:
        line = [0,0,1]  # 우선 오른쪽으로 가도록 위치를 보정해준다.
    else:
        temp = line[0]
        line[0] = line[2]
        line[2] = temp
    
    return line

def LineRotate():
    rotate_big = 

if __name__ == '__main__':
    while True:
        line = Line()
        count = 0

        print("main : ", line)

        time.sleep(0.5)



