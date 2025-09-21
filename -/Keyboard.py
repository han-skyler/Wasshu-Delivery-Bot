# 키보드로 로봇을 제어하기 위한 파이게임 모듈
import pygame

def init():
    # 파이게임 초기화
    pygame.init()
    # 창크기 100*100으로 설정
    win = pygame.display.set_mode((100,100))

def getKey(keyName):
    ans = False

    for eve in pygame.event.get():pass
    # 무언가 누를때 마다 감지함
    KeyInput = pygame.key.get_pressed()

    # 키 이벤트를 처리하기 위한 정의
    myKey = getattr(pygame,'K_{}'.format(keyName))

    # a키를 눌렀을때 이벤트
    if KeyInput [myKey]:
        ans = True

    pygame.display.update()

    return ans

def main():
    # a키를 눌렀을때 출력되는 메세지
    if getKey('a'):
        print('Key a was pressed')

if __name__ == '__main__':
    init()
    while True:
        main()

