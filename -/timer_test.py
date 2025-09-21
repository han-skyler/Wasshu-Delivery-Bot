import datetime
import math
import threading
import time

time_laps = 0

def print_second():
	now = time.strftime('%H:%M:%S')
	time_laps = math.floor(time.time() - start_time)
	print(f'{now} : {time_laps}초 경과')
	threading.Timer(2, print_second).start()
	pass
	
start_time = time.time()
print_second()
