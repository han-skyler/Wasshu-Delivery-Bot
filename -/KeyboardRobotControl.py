from MotorDriver import Motor
import Keyboard as kp

# motor = Motor(2,3,4,17,22,27)
# motor = Motor(17,27,22,5,6,13)
motor = Motor(2, 3, 4, 22, 17, 27)
kp.init()

def main():
    # motor.stop(2)
    if kp.getKey('w'):
        motor.move(0.2, 0, 0.1)
    elif kp.getKey('s'):
        motor.move(-0.6, 0, 0.1)
    elif kp.getKey('a'):
        motor.move(0.3, 0.3, 0.1)
    elif kp.getKey('d'):
        motor.move(0.3, -0.3, 0.1)
    elif kp.getKey('q'):  # anticlockwise
        motor.turn(0.4, 1, 0.1)
    elif kp.getKey('e'):  # clockwise
        motor.turn(0.4, 0, 0.1)
    else:
        motor.stop(0.1)


if __name__ == '__main__':
    while True:
        main()



