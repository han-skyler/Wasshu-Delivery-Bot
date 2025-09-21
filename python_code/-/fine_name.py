from scapy.all import *
from threading import Thread
import pandas
import time
import os
import threading

import csv

total_iterations = 10
global num

# initialize the networks dataframe that will contain all access points nearby
networks = pandas.DataFrame(columns=["BSSID", "BSSID0", "SSID", "dBm_Signal", "Channel", "Crypto"])
# set the index BSSID (MAC address of the AP)
networks.set_index("BSSID", inplace=True)

# wifi 신호 주소와 세기를 탐지
def callback(packet):
    if packet.haslayer(Dot11Beacon):
        # extract the MAC address of the network
        bssid = packet[Dot11].addr2
        # get the name of it
        ssid = packet[Dot11Elt].info.decode()
        try:
            dbm_signal = packet.dBm_AntSignal
        except:
            dbm_signal = "N/A"
        # extract network stats
        stats = packet[Dot11Beacon].network_stats()
        # get the channel of the AP
        channel = stats.get("channel")
        # get the crypto
        crypto = stats.get("crypto")
        #networks.at[num, bssid] = dbm_signal
        networks.loc[bssid] = (bssid, ssid, dbm_signal, channel, crypto)
        #networks= (bssid, ssid, dbm_signal, channel, crypto)


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
    
    # 20번 (10초 * 20, 약 2분 40초) 수집
    for i in range(total_iterations):
        print("Now ", i + 1)
        
        # timeout으로 신호를 탐색하는 시간 설정, timeout 시간동안 sniff 
        sniff(prn=callback, iface=interface, timeout=10)
        
        time.sleep(0.5)
        num = num + 1
    
    # 해당 위치 좌표 설정 및 csv파일로 저장
    x, y = get_position_name()
    save_to_csv(x, y)
        
        
        
        
        
        

