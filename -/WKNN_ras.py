from scapy.all import *

import time

import threading
from threading import Thread
import pandas as pd
import os

import signal
import sys

# 서버 접속을 위한 import
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import numpy as np

# 수집한 와이파이 정보를 저장할 데이터 프레임 생성
networks = pd.DataFrame(columns=["mac", "rss"])

# 각 열의 인덱스 값(행)은 잡히는 신호(BSSID)의 이름으로 한다.
networks.set_index("mac", inplace=True)


# 잡히는 신호의 갯수 초기화
global network_counter
network_counter = 0

global x_fp
global y_fp
global x_old
global y_old
global x_new
global y_new

def load_position():
    # 서버에 저장된 현재 위치 로드
    cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
    firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'}, name='xy_app')
    firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'})
        
    xy_app = firebase_admin.get_app('xy_app')
    xy_db = firebase_admin.db.reference(app=xy_app)

    y = xy_db.child('y ').get()

    # WiFi fingerprint - current
    ref_x_new = xy_db.child('x_new')
    ref_y_new = xy_db.child('y_new')

    x_old = ref_x_new.get()
    y_old = ref_y_new.get()

    y_old = 0.03 * y_old + 1.2

    x_fp = x_old
    y_fp = y_old

    return x_old, y_old, x_fp, y_fp


# 패킷이 스니핑(감지)될 때마다 실행되는 콜백 기능을 사용하는 snip() 기능을 사용
# 스니핑된 패킷에 비콘 계층이 있는지 확인 -> 신호 및 일부 통계 추출
def callback(packet):
    global network_counter

    # Dot11Beacon 클래스는 네트워크에서 채널, 속도, 암호화 유형과 같은 정보 추출
    if packet.haslayer(Dot11Beacon): 
        # Wi-Fi 신호의 고유 주소 추출
        bssid = packet[Dot11].addr2
        try:
            dbm_signal = packet.dBm_AntSignal
        except:
            dbm_signal = "N/A"

        # bssid를 인덱스로해 데이터 프레임에 추가
        networks.loc[bssid] = (dbm_signal)
        
        # 잡힌 신호 수 세기 (25개가 넘으면 csv로 저장)
        network_counter += 1
        
        if network_counter >= 25:
            save_to_csv()
            
            # WKNN
            run_wknn()

        time.sleep(0.5)


def change_channel():
    global ch
    ch = 1
    while True:
        interface = "wlan1"
        os.system(f"iwconfig {interface} channel {ch}")
        # Switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)


# 잡힌 25개의 신호의 값을 저장할 파일 명 설정
def save_to_csv():
    filename = f"/home/pi/dataset/wifi_networks.csv"
    networks.to_csv(filename)
    #print(f"Networks saved to {filename}")

#########################################################################################

def run_wknn():
    global x_fp
    global y_fp
    global x_new
    global y_new
    
    data_online, data_offline = load_data()
    data = cal_dis(data_online, data_offline, y_fp)
    x_new, y_new, x_fp, y_fp = knn(data)
    upload_firebase()
    network_counter = 0
    
    
def load_data():
    # 온라인 및 오프라인 데이터 세트 로드
    data_offline  = pd.read_csv("/home/pi/dataset/offline_data_v3_2.csv")
    data_online = pd.read_csv("/home/pi/dataset/wifi_networks.csv")
        
    return data_online, data_offline


def cal_dis(data_online, data_offline, y_fp):
    # 각 액세스 지점 및 테스트 위치에 대한 RSSi 값 집계
    # posx, posy, mac으로 그룹을 정의하고 rss의평균값을 낸다
    data_online = data_online.groupby(['mac'])['rss'].mean().reset_index()
    data_offline = data_offline.groupby(['posx','posy','mac'])['rss'].mean().reset_index()
    
    data_test = data_online.copy()[['test_id','posx','posy']].drop_duplicates() # 중복되는 행 제거

    # 두 데이터프레임을 각 데이터에 존재하는 고유값(key)을 기준으로 병합
    data = pd.merge(data_online,data_offline,on=['mac'],suffixes=['_online','_offline'])

    data['D'] = (data['rss_offline']-data['rss_online'])**2

    
    while True:
        if data.empty:
            print("Empty DataFrame")
            ch += 1

        else:
            data['D'] = (data['rss_offline']-data['rss_online'])**2

    # test_id, posx_offline, posy_offline을 기준으로 그룹 정의하여 D의 값을 sum한다
    data2 = data.groupby(['test_id','posx_offline','posy_offline'])['D'].sum().reset_index()

    data2['D'] = data2['D'] ** 0.5
        
    return data2

def knn(data):
    global x_fp
    global y_fp
    global x_new
    global y_new
    
    # WKNN을 사용하여 오프라인 데이터베이스에서 가장 가까운 k개 지점 선택
    # 이웃의 개수
    k=4
    
    #print(data)
    # 'D' 열의 값으로 역수를 계산하여 'inverse_distance' 열을 생성
    # '1 / data2['D']'는 'D' 열의 모든 값에 대해 1을 나누어 역수를 계산
    data['inverse_distance'] = 1 / data['D']

    # 'test_id'로 그룹화된 데이터프레임에서 'inverse_distance' 열의 값을 기준으로 랭크를 계산합니다.
    # 'transform()' 함수를 이용하여 그룹화된 데이터프레임의 원래 인덱스를 유지한 채 랭크 값을 계산합니다.
    # 'ascending=False'는 역순으로 랭크 값을 계산하라는 것을 의미합니다.
    data['Rank'] = data.transform('rank', ascending=False)['inverse_distance']

    # 'Rank' 열이 k 이하인 데이터만 선택하여 'data3' 데이터프레임을 생성합니다.
    # 'data2['Rank']<=k'는 'Rank' 열의 모든 값에 대해 k 이하인 값을 True로, 그렇지 않은 값을 False로 변환합니다.
    # 이를 이용하여 'data2' 데이터프레임에서 True에 해당하는 행들만 선택하여 'data3' 데이터프레임으로 저장합니다.
    data3 = data[data['Rank']<=k]

    data4 = data3.groupby('test_id').apply(lambda x: np.average(x[['posx_offline', 'posy_offline']], weights=x['inverse_distance'], axis=0)).reset_index(name='pos')

    data4[['posx_est', 'posy_est']] = pd.DataFrame(data4['pos'].tolist(), index=data4.index) 
    
    print("Data4", data4)
    
    if len(filtered_data) > 0:
        x_new = data4['posx_est'].iloc[0]
        y_new = data4['posy_est'].iloc[0]
    
        # x 좌표: 0 ~ 700
        # y 좌표: 0 ~ 950
        x_fp = x_new
        y_fp = y_new
              
        x_new = 42.5 * x_new
        y_new = 32.78 * y_new - 25.06
    else:
        print("No match")
               
        x_new = 42.5 * x_fp
        y_new = 32.78 * y_fp - 25.06
    
    return x_new, y_new, x_fp, y_fp

def upload_firebase():
    global x_fp
    global y_fp
    global x_new
    global y_new
    global signal
    
    #print("Firebase Update...")
    df = pd.DataFrame(columns=['x', 'y'])
    y_fp = 32.78 * y_fp - 25.06
    
    df.loc[0] = [x_new, y_new]
    
    df.to_csv("/home/pi/python_code/current.csv")
    #print(df)
    
    ref_x_new = xy_db.child('x_new')
    x_new = ref_x_new.get()
    
    if x_new == 170:
        print("y_new update...")
        ref_map = db.reference("")
        ref_map.update({'y_new' : y_new})
    
    

##############################################################################

def main():
    # Interface name, check using iwconfig
    interface = "wlan1"

    # Start the channel changer
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()

    # Start sniffing
    #print("Start...")
    sniff(prn=callback, iface=interface)


if __name__ == "__main__":
    print("Running...")

    main()


