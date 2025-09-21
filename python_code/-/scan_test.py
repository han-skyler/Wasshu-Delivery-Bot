from scapy.all import *
from threading import Thread
import pandas as pd
import time
import os
import threading

import csv

global num


# 잡히는 신호의 갯수 초기화
global network_counter
network_counter = 0

# 수집한 와이파이 정보를 저장할 데이터 프레임 생성
networks = pd.DataFrame(columns=["mac", "rss"])

# 각 열의 인덱스 값(행)은 잡히는 신호(BSSID)의 이름으로 한다.
networks.set_index("mac", inplace=True)

# wifi 신호 주소와 세기를 탐지
def callback(packet):
    global network_counter

    # Dot11Beacon 클래스는 네트워크에서 채널, 속도, 암호화 유형과 같은 정보 추출
    if packet.haslayer(Dot11Beacon): 
        # Wi-Fi 신호의 고유 주소 추출
        bssid = packet[Dot11].addr2
        # 해당 Wi-Fi의 이름 추출
        ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore')
        try:
            dbm_signal = packet.dBm_AntSignal
        except:
            dbm_signal = "N/A"
        # Wi-Fi 신호 상태 추출
        stats = packet[Dot11Beacon].network_stats()
        # 신호의 채널 얻기
        channel = stats.get("channel")
        # 암호 얻기
        crypto = stats.get("crypto")
        # bssid를 인덱스로해 데이터 프레임에 추가
        networks.loc[bssid] = (dbm_signal)
        
        # 잡힌 신호 수 세기 (25개가 넘으면 csv로 저장)
        network_counter += 1
        #print(f"Detected {network_counter} networks.")  # 추가된 로그 출력
        
        if network_counter >= 25:
            x, y = get_position_name()
            save_to_csv(x, y)



# 주변의 와이파이가 다른 채널에 있을 경우 다른 채널의 와이파이 주소를 찾기위해 채널을 0.5초마다 변경
def change_channel():
    ch = 1
    while True:
        os.system(f"iwconfig {interface} channel {ch}")
        # switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)


# 좌표 값 받기
def get_position_name():
    x_position = input("x 좌표 입력: ")
    y_position = input("y 좌표 입력: ")
    
    return x_position, y_position


# 잡힌 wifi 주소와 각 시간마다 신호 세기 저장
def save_to_csv(x, y):
    filename = f"/home/pi/dataset/position/" + x + " " + y + ".csv"
    networks.to_csv(filename, index=False)
    print(f"Networks saved to {filename}")


if __name__ == "__main__":
    # interface name, check using iwconfig
    interface = "wlan1"
    num = 0
    
    print("Running...")

    
    # start the channel changer
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()
        
    # timeout으로 신호를 탐색하는 시간 설정, timeout 시간동안 sniff 
    sniff(prn=callback, iface=interface, timeout = 3)

    
    # 해당 위치 좌표 설정 및 csv파일로 저장
    #x, y = get_position_name()
    #save_to_csv(x, y)
        
        
        
        
        
        

