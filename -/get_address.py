from scapy.all import *
from threading import Thread
import pandas as pd
import time
import os
import csv

capture_time = 10
start_time = time.time()
end_time = start_time + capture_time

# interface name, check using iwconfig
interface = "wlan1"

# initialize the networks dataframe that will contain all access points nearby
network_address = []

def callback(packet):
    if packet.haslayer(Dot11Beacon):
        # extract the MAC address of the network
        bssid = packet[Dot11].addr2
        network_address.append(bssid)

def change_channel():
    ch = 1
    while True:
        os.system(f"iwconfig {interface} channel {ch}")
        # switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)
   
    
# 잡힌 wifi 주소와 각 시간마다 신호 세기 저장
def save_to_csv():
    filename = "/home/pi/dataset/position/network_address.csv"
    
    data = pd.DataFrame({'MAC': network_address})
    
    data.to_csv(filename, index = False)
    print(f"Networks saved to {filename}")


def main():
    # start the channel changer
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()
        
    # start sniffing
    sniff(prn=callback, iface=interface)

if __name__ == "__main__":            
    while time.time() < end_time:
        main()
        save_to_csv()
        os._exit(0)
        
    

