from queue import PriorityQueue
import math

def normalise(self, value, min_val, max_val):
        if max_val == min_val:
            return 0
        
        return (value - min_val) / (max_val - min_val)

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def astar(start, goal, layout, aisle_width = 1):
    rows = layout.width
    cols = layout.length

    MOVES = [
        (1, 0), (-1, 0), (0, 1), (0, -1),  # Up, Down, Left, Right
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonals
    ]

    def heuristic(a, b):
        (x1, y1) = a
        (x2, y2) = b
        return math.hypot(x2 - x1, y2 - y1)

    def has_clearance(current, neighbor):
        (x1, y1) = current
        (x2, y2) = neighbor
        dx = x2 - x1
        dy = y2 - y1

        # Bounds check
        if not (0 <= x2 < rows and 0 <= y2 < cols):
            return False
        if layout[x2][y2] == 0:
            return False

        # Straight moves
        if dx == 0 or dy == 0:
            for i in range(-aisle_width // 2 + 1, aisle_width // 2 + 1):
                check_x = x2 + (i if dx == 0 else 0)
                check_y = y2 + (i if dy == 0 else 0)
                if not (0 <= check_x < rows and 0 <= check_y < cols) or layout[check_x][check_y] == 0:
                    return False

        # Diagonal moves
        if dx != 0 and dy != 0:
            if layout[x1][y2] == 0 or layout[x2][y1] == 0:
                return False

        return True

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for move in MOVES:
            neighbor = (current[0] + move[0], current[1] + move[1])

            if has_clearance(current, neighbor):
                new_cost = cost_so_far[current] + 1  # cost of 1 per move
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + heuristic(neighbor, goal)
                    frontier.put((priority, neighbor))
                    came_from[neighbor] = current

    # Reconstruct path
    if goal not in came_from:
        return None

    path = []
    current = goal
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    if path == []:
        return None
    else:
        return path
