from scapy.all import *

import time
import csv

import threading
from threading import Thread
import pandas as pd
import os

import signal
import sys

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import numpy as np

# Example usage:
map_matrix = [
	[0, 0, 1, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0],
	[1, 1, 1, 1, 1, 1, 1, 1],
	[0, 0, 1, 0, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 1, 0, 0],
	[1, 1, 1, 1, 1, 1, 1, 1],
	[0, 0, 1, 0, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 1, 0, 0],
	[1, 1, 1, 1, 1, 1, 1, 1],
	[0, 0, 1, 0, 0, 1, 0, 0]
]

cred = credentials.Certificate("/home/pi/Key/cd-fc010.json")
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'}, name='xy_app')
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://cd-fc010-default-rtdb.firebaseio.com/'})
		
xy_app = firebase_admin.get_app('xy_app')
xy_db = firebase_admin.db.reference(app=xy_app)
	
def get_state():
	print("get_state 실행 중...")
	# WiFi fingerprint - current
	ref_state = xy_db.child('delivery_state')
	state = ref_state.get()
	
	if state == 1:
		x_start = 0
		y_start = 2
		
		ref_x_end = xy_db.child('x_book')
		ref_y_end = xy_db.child('y_book')
		x_end = ref_x_end.get()
		y_end = ref_y_end.get()		
		
		
	elif state == 2:
		ref_x_start = xy_db.child('x_book')
		ref_y_start = xy_db.child('y_book')
		x_start = ref_x_start.get()
		y_start = ref_y_start.get()
		
		ref_x_end = xy_db.child('x_user')
		ref_y_end = xy_db.child('y_user')
		x_end = ref_x_end.get()
		y_end = ref_y_end.get()			
		
	elif state == 4:
		ref_x_start = xy_db.child('x_user')
		ref_y_start = xy_db.child('y_user')
		x_start = ref_x_start.get()
		y_start = ref_y_start.get()
		
		x_end = 0
		y_end = 2		
		
	return x_start, y_start, x_end, y_end


# 최단 경로 탐색
def find_shortest_path(matrix, start, end):
    rows, cols = len(matrix), len(matrix[0])
    visited = [[False] * cols for _ in range(rows)]

    queue = Queue()
    queue.put(start)
    visited[start[0]][start[1]] = True
    predecessors = {}

    while not queue.empty():
        current = queue.get()

        if current == end:
            path = []
            while current in predecessors:
                path.insert(0, current)
                current = predecessors[current]
            path.insert(0, start)
            return path

        row, col = current
        neighbors = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]

        for neighbor in neighbors:
            n_row, n_col = neighbor
            if 0 <= n_row < rows and 0 <= n_col < cols and matrix[n_row][n_col] == 1 and not visited[n_row][n_col]:
                queue.put(neighbor)
                visited[n_row][n_col] = True
                predecessors[neighbor] = current

    return None  # No path found

def save_paths_to_csv(file_path, matrix):
	with open(file_path, mode = 'w', newline = '') as file:
		writer = csv.writer(file)
		
		for row in matrix:
			writer.writerow([int(col) for col in row])
		#writer.writerow([(int(row), int(col)) for row, col in all_paths])
	

def get_road(a, b, c, d):	
	print("get road...")
	start_point = (a, b)
	end_point = (c, d)
	
	all_path = find_shortest_path(map_matrix, start_point, end_point)
	
	if all_path:
		print(f"All paths from {start_point} to {end_point}: {all_path}")
		filename = "/home/pi/dataset/shortest_pass/shortest_pass.csv"
		save_paths_to_csv(filename, all_path)
		print("save to csv...")
	else:
		print("No path found")


while True:
    #schedule_execution()  # Firebase
    x_start, y_start, x_end, y_end = get_state()
    print(f"출발 {x_start}, {y_start}  도착: {x_end}, {y_end}")
    get_road(x_start, y_start, x_end, y_end)
    
    time.sleep(5)
    
    

