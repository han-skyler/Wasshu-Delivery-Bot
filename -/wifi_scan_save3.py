# 필요한 파일 import
from scapy.all import *
from threading import Thread
import pandas as pd
import time
import os

# 수집한 와이파이 정보를 저장할 데이터 프레임 생성
networks = pd.DataFrame(columns=["mac", "rss"])
# 각 열의 인덱스 값(행)은 잡히는 신호(BSSID)의 이름으로 한다.
networks.set_index("mac", inplace=True)

# 잡히는 신호의 갯수 초기화
network_counter = 0

# 패킷이 스니핑(감지)될 때마다 실행되는 콜백 기능을 사용하는 snip() 기능을 사용
# 스니핑된 패킷에 비콘 계층이 있는지 확인 -> 신호 및 일부 통계 추출
def callback(packet):
    global network_counter

    # Dot11Beacon 클래스는 네트워크에서 채널, 속도, 암호화 유형과 같은 정보 추출
    if packet.haslayer(Dot11Beacon): 
        # Wi-Fi 신호의 고유 주소 추출
        bssid = packet[Dot11].addr2
        # 해당 Wi-Fi의 이름 추출
        ssid = packet[Dot11Elt].info.decode()
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
        
        # 잡힌 신호 수 세기 (30개가 넘으면 csv로 저장)
        network_counter += 1
        if network_counter >= 30:
            save_to_csv()

            
# 잡힌 30개의 신호의 값을 저장할 파일 명 설정
def save_to_csv():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"/home/pi/dataset/wifi_network/wifi_network_{timestamp}.csv"
    networks.to_csv(filename)
    print(f"Networks saved to {filename}")

def change_channel():
    ch = 1
    while True:
        os.system(f"iwconfig {interface} channel {ch}")
        # Switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)
        
        
def main():
    # Start the channel changer
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()
    # Start sniffing
    sniff(prn=callback, iface=interface)
    

if __name__ == "__main__":
    # Interface name, check using iwconfig
    interface = "wlan1"
    main()
    
    
