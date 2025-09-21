from queue import Queue

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

def find_shortest_path_with_midpoint(matrix, start, midpoint, end):
    def bfs(start, end):
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

        return None

    rows, cols = len(matrix), len(matrix[0])

    # Find shortest path from start to midpoint
    path_start_to_midpoint = bfs(start, midpoint)

    # Find shortest path from midpoint to end
    path_midpoint_to_end = bfs(midpoint, end)

    # Combine the paths
    if path_start_to_midpoint and path_midpoint_to_end:
        # Exclude the duplicate midpoint when combining paths
        path_midpoint_to_end = path_midpoint_to_end[1:]
        shortest_path = path_start_to_midpoint + path_midpoint_to_end
        return shortest_path
    else:
        return None

a = 
b = 
c = 
d = 


start_point = (0, 2)
end_point = (a, b)
midpoint = (c, d)


shortest_path = find_shortest_path_with_midpoint(map_matrix, start_point, midpoint, end_point)

if shortest_path:
    print(f"Shortest path from {start_point} to {end_point} passing through {midpoint}: {shortest_path}")
else:
    print(f"No path from {start_point} to {end_point} passing through {midpoint}.")
