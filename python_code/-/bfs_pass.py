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


shortest_path = find_shortest_path(map_matrix, start_point, end_point)

if shortest_path:
    print(f"Shortest path from {start_point} to {end_point}: {shortest_path}")
else:
    print("No path found.")
