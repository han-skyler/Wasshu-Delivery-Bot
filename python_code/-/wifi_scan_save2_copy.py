from scapy.all import *
from threading import Thread
import pandas as pd
import time
import os
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize the networks dataframe that will contain all access points nearby
networks = pd.DataFrame(columns=["mac", "rss"])
# Set the index BSSID (MAC address of the AP)
networks.set_index("mac", inplace=True)

# Counter to track the number of networks collected
network_counter = 0

def callback(packet):
    global network_counter

    if packet.haslayer(Dot11Beacon):
        # Extract the MAC address of the network
        bssid = packet[Dot11].addr2
        # Get the name of it
        ssid = packet[Dot11Elt].info.decode()
        try:
            dbm_signal = packet.dBm_AntSignal
        except:
            dbm_signal = "N/A"
        # Extract network stats
        stats = packet[Dot11Beacon].network_stats()
        # Get the channel of the AP
        channel = stats.get("channel")
        # Get the crypto
        crypto = stats.get("crypto")
        networks.loc[bssid] = (dbm_signal)

        network_counter += 1
        if network_counter >= 20:
            save_to_csv()
            #os._exit(0)  # Terminate the program after saving to CSV

def save_to_csv():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"/home/pi/dataset/wifi_network/wifi_networks.csv"
    networks.to_csv(filename)
    print(f"Networks saved to {filename}")

def print_all():
    while True:
        os.system("clear")
        print(networks)
        time.sleep(0.5)

def change_channel():
    ch = 1
    while True:
        os.system(f"iwconfig {interface} channel {ch}")
        # Switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)
        
def load_data():
    # 온라인 및 오프라인 데이터 세트 로드 
    data_offline  = pd.read_csv("/home/pi/dataset/offline_data_v3_2.csv")
    data_online = pd.read_csv("/home/pi/dataset/wifi_network/wifi_networks.csv")
    
    # 불필요한 열 제거
    data_online = data_online.drop_duplicates() # 중복되는 행 제거
    data_offline = data_offline.drop_duplicates() # 중복되는 행 제거
    
    return data_online, data_offline

def cal_dis(data_online,data_offline):
    # 각 액세스 지점 및 테스트 위치에 대한 RSSi 값 집계
    # posx, posy, mac으로 그룹을 정의하고 rss의평균값을 낸다
    data_online = data_online.groupby(['mac'])['rss'].mean().reset_index()
    data_offline = data_offline.groupby(['posx','posy','mac'])['rss'].mean().reset_index()

    # 오류 평가를 위한 테스트 데이터 세트 생성
    data_test = data_online.drop_duplicates() # 중복되는 행 제거

    # 액세스 지점에서 오프라인 및 온라인 데이터셋 가입
    # 두 데이터프레임을 각 데이터에 존재하는 고유값(key)을 기준으로 병합
    data = pd.merge(data_online,data_offline,on=['mac'],suffixes=['_online','_offline'])


    # 온라인 및 오프라인 레코드 간의 RSSi 편차 계산
    data['D'] = (data['rss_offline']-data['rss_online'])**2

    # test_id, posx_offline, posy_offline을 기준으로 그룹 정의하여 D의 값을 sum한다
    data2 = data.groupby(['posx','posy'])['D'].sum().reset_index()

    data2['D'] = data2['D']**0.5
    
    return data2

def knn(data):
    # WKNN을 사용하여 오프라인 데이터베이스에서 가장 가까운 k개 지점 선택
    # 이웃의 개수
    k=4

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

    # rank 열의 값이 1인 행 필터링
    filtered_data = data3[data3['Rank'] == 1]

    # posx 열의 값과 posy 열의 값을 변수로 저장
    x_new = filtered_data['posx'].iloc[0]
    y_new = filtered_data['posy'].iloc[0]
    
    return x_new, y_new

def upload_firebase(x_new, y_new):
    # upload position
    cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'})

    ref_map = db.reference("MAP/current")
    ref_map.update({'x_new' : x_new})
    ref_map.update({'y_new' : y_new})

def main():
    # Interface name, check using iwconfig
    interface = "wlan1"
    
    # Start the thread that prints all the networks
    printer = Thread(target=print_all)
    printer.daemon = True
    printer.start()
    
    # Start the channel changer
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()
    
    # Start sniffing
    sniff(prn=callback, iface=interface)
    
    # WKNN
    data_online, data_offline = load_data()
    data = cal_dis(data_online,data_offline)
    x_new, y_new = knn(data)
    upload_firebase(x_new, y_new)


if __name__ == "__main__":
    main()

    
    
