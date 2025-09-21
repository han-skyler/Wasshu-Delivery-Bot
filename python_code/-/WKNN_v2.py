import pandas as pd
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

PROJECT_ID = "cd-fc010"
# 온라인 및 오프라인 데이터 세트 로드 
data_offline  = pd.read_csv("/home/pi/dataset/offline_data_v3_2.csv")
data_online = pd.read_csv("/home/pi/dataset/wifi_network/wifi_networks.csv")

cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")

firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'}, name='xy_app')
xy_app = firebase_admin.get_app('xy_app')
xy_db = firebase_admin.db.reference(app=xy_app)

# WiFi fingerprint - current
ref_x_new = xy_db.child('MAP').child('current').child('x_new')
ref_y_new = xy_db.child('MAP').child('current').child('y_new')

x_old = ref_x_new.get()
y_old = ref_y_new.get()


# 불필요한 열 제거
data_online = data_online.drop_duplicates() # 중복되는 행 제거
data_offline = data_offline.drop_duplicates() # 중복되는 행 제거

# 각 액세스 지점 및 테스트 위치에 대한 RSSi 값 집계
# posx, posy, mac으로 그룹을 정의하고 rss의평균값을 낸다
# 각 액세스 지점 및 테스트 위치에 대한 RSSi 값 집계
# posx, posy, mac으로 그룹을 정의하고 rss의평균값을 낸다
data_online = data_online.groupby(['mac'])['rss'].mean().reset_index()
data_offline = data_offline.groupby(['posx','posy','mac'])['rss'].mean().reset_index()

# 오류 평가를 위한 테스트 데이터 세트 생성
data_test = data_online.drop_duplicates() # 중복되는 행 제거

# 액세스 지점에서 오프라인 및 온라인 데이터셋 가입
# 두 데이터프레임을 각 데이터에 존재하는 고유값(key)을 기준으로 병합
data = pd.merge(data_online,data_offline,on=['mac'],suffixes=['_online','_offline'])

print(data)

# 온라인 및 오프라인 레코드 간의 RSSi 편차 계산
#data['D'] = (data['rss_offline']-data['rss_online'])**2
    
for i in range(len(data)):
    if data.iloc[i, 3] >= y_old -2 and data.iloc[i, 3] <= y_old +2:
        data['D'] = ((data['rss_offline']-data['rss_online']) ** 2) * 0.5

    else:
        
        data['D'] = (data['rss_offline']-data['rss_online']) ** 2

# test_id, posx_offline, posy_offline을 기준으로 그룹 정의하여 D의 값을 sum한다
data2 = data.groupby(['posx','posy'])['D'].sum().reset_index()

data2['D'] = data2['D']**0.5
        



# WKNN을 사용하여 오프라인 데이터베이스에서 가장 가까운 k개 지점 선택
# 이웃의 개수
k=4

# 'D' 열의 값으로 역수를 계산하여 'inverse_distance' 열을 생성
# '1 / data2['D']'는 'D' 열의 모든 값에 대해 1을 나누어 역수를 계산
data2['inverse_distance'] = 1 / data2['D']

# 'test_id'로 그룹화된 데이터프레임에서 'inverse_distance' 열의 값을 기준으로 랭크를 계산합니다.
# 'transform()' 함수를 이용하여 그룹화된 데이터프레임의 원래 인덱스를 유지한 채 랭크 값을 계산합니다.
# 'ascending=False'는 역순으로 랭크 값을 계산하라는 것을 의미합니다.
data2['Rank'] = data2.transform('rank', ascending=False)['inverse_distance']

# 'Rank' 열이 k 이하인 데이터만 선택하여 'data3' 데이터프레임을 생성합니다.
# 'data2['Rank']<=k'는 'Rank' 열의 모든 값에 대해 k 이하인 값을 True로, 그렇지 않은 값을 False로 변환합니다.
# 이를 이용하여 'data2' 데이터프레임에서 True에 해당하는 행들만 선택하여 'data3' 데이터프레임으로 저장합니다.
data3 = data2[data2['Rank']<=k]

# rank 열의 값이 1인 행 필터링
filtered_data = data3[data3['Rank'] == 1]

print(filtered_data)

# posx 열의 값과 posy 열의 값을 변수로 저장
#x= filtered_data['posx'].iloc[0]
#y = filtered_data['posy'].iloc[0]

###############################################################
# upload position
 
#cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
#firebase_admin.initialize_app(cred,{'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'})

#ref = db.reference("MAP")
#ref.update({'x' : x})
#ref.update({'y' : y})

