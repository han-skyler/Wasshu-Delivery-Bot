# 와슈 딜리버리봇 (Wasshu Delivery Bot)

<p align="center">
  <img src="https://github.com/user-attachments/assets/6a06215d-84f0-45bf-957e-1c1fa4314810" 
       alt="image" 
       width="500" />
</p>



본 프로젝트는 와이파이 신호 세기(RSSI)를 활용하여 실내에서 현재 위치를 파악하고, 지정된 목적지까지 라인을 따라 자율주행하는 배달 로봇의 소스 코드입니다.

## 📖 주요 기능

- **라인 트레이싱 (Line Tracing)**: 바닥의 라인을 인식하여 따라가는 주행
- **실내 위치 추정 (Indoor Positioning)**: 수집된 WiFi RSSI 데이터를 WKNN 알고리즘에 적용하여 현재 위치 추정
- **객체 인식 (Object Detection)**: YOLO 모델을 통해 특정 객체 인식
- **QR 코드 인식 (QR Code Recognition)**: QR 코드를 읽어 목적지 정보나 명령을 수신
- **장애물 감지 (Obstacle Detection)**: 거리 센서를 이용한 전방 장애물 감지
- **모터 제어 (Motor Control)**: 로봇의 정밀한 이동 및 방향 전환 제어

## 🛠️ 핵심 기술 및 알고리즘

- **위치 추정 (Positioning)**: 주변 WiFi AP의 RSSI 값을 기반으로 한 **WKNN(Weighted K-Nearest Neighbors)** 알고리즘
- **주행 (Navigation)**: 카메라를 이용한 라인 트레이싱
- **객체 인식 (Object Recognition)**: YOLO (You Only Look Once)

## 📂 주요 코드 설명

- **`main.py`**, **`MainRobot.py`**: 로봇의 전체 동작을 제어하는 메인 실행 파일입니다.
- **`WKNN_ras_v2.py`**: WiFi 신호 세기를 이용한 실내 위치 추정(WKNN) 알고리즘의 핵심 로직을 담고 있습니다.
- **`GetLine.py`**: 카메라로 라인을 인식하고 차선을 유지하며 주행하는 기능을 구현한 모듈입니다.
- **`GetMotor.py`**, **`MotorModule.py`**: 로봇의 DC모터를 제어하는 모듈입니다.
- **`GetYolo.py`**: YOLO 모델을 사용하여 객체를 탐지하는 모듈입니다.
- **`GetQR.py`**: QR 코드를 인식하고 포함된 정보를 디코딩하는 모듈입니다.
- **`GetDistance.py`**: 거리 센서를 통해 장애물과의 거리를 측정하는 모듈입니다.
- **`collect_rss_v1.py`**, **`wifi_scan_save.py`**: 위치 추정을 위한 WiFi 신호 세기(RSSI) 핑거프린팅 데이터를 수집하는 스크립트입니다.

## 🏆 논문 및 수상 내역

- 📄 **논문**  
  *Line Tracking Delivery Robot Using Wi-Fi-based Indoor Positioning*  
  *2023 14th International Conference on Information and Communication Technology Convergence (ICTC)*  
  [[DOI 링크]](https://doi.org/10.1109/ICTC58733.2023.10393789)

- 🥇 **대상**  
  미래모빌리티 & 첨단반도체 캡스톤디자인 경진대회 (조선대학교)  
  *2024.01*

- 🥇 **금상**  
  정보통신공학부 캡스톤디자인 경진대회 (조선대학교)  
  *2023.11*

---

## © 저작권 등록

<p align="center">
  <img src="https://github.com/user-attachments/assets/057acc2b-f0c4-420f-916c-bad5eaef5311"
       alt="저작권 등록증" 
       width="300" />
</p>

- **저작권 등록명**: Operation of Wi-Fi-Based Indoor Delivery Robots Combined with Line Tracking  
- **등록번호**: C-2023-048873  
- **등록일**: 2023.11.03  
- **저작자**: 조선대학교 산학협력단


## 🔗 관련 자료

- **발표 자료:** [Wi-Fi 기반 실내 측위를 활용한 도서관 서비스 로봇](https://han-skyler.github.io/portfolio_first/pjt3.html)
- **어플리케이션 GitHub:** [Library-Kiosk](https://github.com/han-skyler/Library-Kiosk)

## 📝 라이선스

자세한 내용은 `LICENSE` 파일을 참고해 주세요.
