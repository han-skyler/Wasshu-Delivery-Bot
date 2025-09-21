from scapy.all import *
from threading import Thread
import pandas
import time
import os

# initialize the networks dataframe that will contain all access points nearby
networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto"])
# set the index BSSID (MAC address of the AP) 
networks.set_index("BSSID", inplace=True)

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
        networks.loc[bssid] = (ssid, dbm_signal, channel, crypto)

        network_counter += 1
        if network_counter >= 20:
            save_to_csv()
            os._exit(0)  # Terminate the program after saving to CSV

def save_to_csv():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"/home/pi/dataset/position/wifi_networks_{timestamp}.csv"
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

if __name__ == "__main__":
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
    
    
