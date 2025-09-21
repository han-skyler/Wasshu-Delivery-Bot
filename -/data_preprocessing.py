import os
import csv
import pandas as pd

data = pd.read_csv("/home/pi/dataset/wifi_networks_20230525_152613.csv")

data = data.drop(columns=['SSID', 'Channel', 'Crypto'])
data.rename(columns={'BSSID': 'mac'}, inplace=True)
data.rename(columns={'dBm_Signal': 'rss'}, inplace=True)

data.to_csv("/home/pi/dataset/wifi_networks2.csv", index=False, encoding='UTF8')