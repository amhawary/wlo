def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two points."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_neighbors(pos, layout, aisle_width=1):
    """Get valid neighboring positions."""
    x, y = pos
    neighbors = []
    
    # Check all four directions
    for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
        new_x, new_y = x + dx, y + dy
        new_pos = (new_x, new_y)
        
        # Check if position is within bounds and not a wall
        if (1 <= new_x <= layout.width and 
            1 <= new_y <= layout.length and 
            new_pos not in layout.structure.get('wall', [])):
            neighbors.append(new_pos)
    
    return neighbors

def astar(start, goal, layout, aisle_width=1):
    """A* pathfinding algorithm."""
    if not start or not goal:
        return None
        
    # Initialize data structures
    open_set = {start}
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}
    
    while open_set:
        # Get node with lowest f_score
        current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
            
        open_set.remove(current)
        
        # Check neighbors
        for neighbor in get_neighbors(current, layout, aisle_width):
            tentative_g_score = g_score[current] + 1
            
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal)
                open_set.add(neighbor)
                
    return None  # No path found 