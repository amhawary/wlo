import math
from ..algorithm.__helpers import astar, manhattan_distance
from typing import List, Dict, Any
import numpy as np

def get_fitness(layout, weights=None):
    if weights is None:
        weights = [1, 1, 1, 1, 1]  # travel_distance, congestion_risk, turns, clustering, utility_access

    # First try static metrics
    routes = []
    for operation in layout.operations:
        from_coord = operation.from_entity
        to_coord = operation.to_entity
        path = astar(from_coord, to_coord, layout, layout.aisle_width)
        if path:
            routes.append(path)
        else:
            metrics = {
                'travel_distance': 1.0,
                'congestion_risk': 1.0,
                'turns': 1.0,
                'clustering': 0.0,
                'utility_access': 0.0,
                'total_fitness': -1.0
            }
            return -1, metrics  # Invalid layout if no path found

    if not routes:
        metrics = {
            'travel_distance': 1.0,
            'congestion_risk': 1.0,
            'turns': 1.0,
            'clustering': 0.0,
            'utility_access': 0.0,
            'total_fitness': -1.0
        }
        return -1, metrics  # No valid routes found

    # Calculate static metrics
    travel_distance = calc_avrg_distance(routes)
    congestion_risk = calc_congestion_risk(routes, layout.width, layout.length)
    nturns = calc_avrg_turns(routes)
    
    # Calculate clustering score based on entity types
    entity_types = {}
    for entity in layout.entities:
        etype = entity['type']
        if etype not in entity_types:
            entity_types[etype] = []
        entity_types[etype].append(entity['position'])
    
    # Calculate average distance between entities of same type
    clustering = 0
    total_pairs = 0
    for positions in entity_types.values():
        if len(positions) > 1:
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = manhattan_distance(positions[i], positions[j])
                    clustering += 1 / (dist + 1)  # Closer entities = higher score
                    total_pairs += 1
    
    clustering = clustering / total_pairs if total_pairs > 0 else 0

    # Calculate utility access
    utility_access = calc_utility_access(layout)

    # Combine metrics with weights
    fitness = (
        weights[0] * (1 - travel_distance) +
        weights[1] * (1 - congestion_risk) +
        weights[2] * (1 - nturns) +
        weights[3] * clustering +
        weights[4] * utility_access
    )

    # Return both total fitness and individual metrics
    metrics = {
        'travel_distance': travel_distance,
        'congestion_risk': congestion_risk,
        'turns': nturns,
        'clustering': clustering,
        'utility_access': utility_access,
        'total_fitness': fitness
    }

    return fitness, metrics

def calc_congestion_risk(routes, width, length):
    if not routes:
        return 1.0  # Maximum congestion if no routes
        
    # Create a grid to track path usage
    grid = [[0 for _ in range(width)] for _ in range(length)]
    count = 0
    for route in routes:
        for x, y in route:
            # Convert 1-based coordinates to 0-based
            grid_x = x - 1
            grid_y = y - 1
            if 0 <= grid_x < width and 0 <= grid_y < length:
                grid[grid_x][grid_y] += 1
                count += 1
    
    if count == 0:
        return 1.0
        
    congested_paths = []
    for x in range(width):
        for y in range(length):
            if grid[x][y] != 0:
                congested_paths.append(grid[x][y])

    if not congested_paths:
        return 0.0
        
    max_congestion = max(congested_paths)
    min_congestion = min(congested_paths)
    avrg_congestion = sum(congested_paths) / len(congested_paths)
    
    # Normalize to 0-1 range
    return avrg_congestion / max_congestion if max_congestion > 0 else 0.0

def calc_avrg_distance(routes):
    if not routes:
        return 1.0  # Maximum distance if no routes
        
    distances = []
    for route in routes: 
        distances.append(len(route))

    if not distances:
        return 1.0
        
    max_distance = max(distances)
    min_distance = min(distances)
    avrg_distance = sum(distances)/len(routes)
    
    # Normalize to 0-1 range
    return avrg_distance / max_distance if max_distance > 0 else 1.0

def calc_avrg_turns(routes):
    if not routes:
        return 1.0  # Maximum turns if no routes
        
    turns_list = []
    for path in routes:
        turns = 0
        if not path or len(path) < 3:
            continue  # No turns if path is too short

        prev_move = (path[1][0] - path[0][0], path[1][1] - path[0][1])

        for i in range(2, len(path)):
            move = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
            if move != prev_move:
                turns += 1
            prev_move = move

        turns_list.append(turns)

    if not turns_list:
        return 1.0
        
    max_turns = max(turns_list)
    min_turns = min(turns_list)
    avrg_turns = sum(turns_list)/len(turns_list)

    # Normalize to 0-1 range
    return avrg_turns / max_turns if max_turns > 0 else 1.0

def calc_space_utilisation(width, length, routes, layout):
    l = [[0 for x in range(width)] for y in range(length)]
    count = 0
    # Get all unoccupied cells
    empty_cells = [(x, y) for x in range(width) for y in range(length) if l[x][y] == 0]
    
    # Remove cells used as aisles in routes
    used_cells = set()
    for route in routes:
        used_cells.update(route)
    
    # Get truly unused cells by removing aisle cells
    unused_cells = [cell for cell in empty_cells if cell not in used_cells]
    # Remove cells occupied by walls
    for wall in layout.structure['wall']:
        x, y = wall
        if 0 <= x-1 < width and 0 <= y-1 < length:  # Convert 1-based to 0-based indexing
            unused_cells = [cell for cell in unused_cells if cell != (x-1, y-1)]
            
    # Remove cells occupied by entities
    for entity in layout.entities:
        pos = entity.get('position')
        if pos:
            x, y = pos
            if 0 <= x-1 < width and 0 <= y-1 < length:  # Convert 1-based to 0-based indexing
                unused_cells = [cell for cell in unused_cells if cell != (x-1, y-1)]
    # Calculate space utilisation as ratio of used space to total space
    total_cells = width * length
    unused_ratio = len(unused_cells) / total_cells
    for route in routes:
        for x, y in route:
            l[x][y] += 1
            count += 1
    
    print(l)
    return

def calc_safety():
    pass

def calc_avrg_clustering(layout):
    total_cluster_score = 0

    for category in layout.utilities.keys():
        entities_in_category = layout.get_category_entities()
        for i in range(len(entities_in_category)):
            for j in range(i+1, len(entities_in_category)):
                pos1 = entities_in_category[i].position
                pos2 = entities_in_category[j].position
                dist = manhattan_distance(pos1, pos2)
                total_cluster_score += 1 / (dist + 1)

def calc_utility_access(layout):
    total_utility_score = 0
    entity_count = 0

    # For each entity that requires utilities
    for entity in layout.entities:
        if entity.get('depends_on') and entity['depends_on'] != ['none']:  # Skip entities with no dependencies
            entity_count += 1
            entity_score = 0
            
            # Get entity's position
            entity_pos = entity.get('position')
            if not entity_pos:
                continue
                
            # For each utility type this entity depends on
            for utility_type in entity['depends_on']:
                # Find the nearest utility point of this type
                min_dist = float('inf')
                for utility_pos in layout.utilities.get(utility_type, []):
                    dist = manhattan_distance(entity_pos, utility_pos)
                    if dist < min_dist:
                        min_dist = dist
                
                # Add inverse distance to score (closer = better)
                if min_dist != float('inf'):
                    entity_score += 1 / (min_dist + 1)  # +1 to avoid division by zero
            
            # Average the utility scores for this entity
            if entity_score > 0:
                total_utility_score += entity_score / len(entity['depends_on'])
    
    # Return average utility access score across all entities
    return total_utility_score / entity_count if entity_count > 0 else 0.0

def _diagonal_and_cross_score(self):
        # Aisle = all empty positions
        filled = set(self.structure['wall'])
        for entity in self.entities:
            filled.update(entity.positions)

        aisles = [
            (x, y)
            for x in range(1, self.width + 1)
            for y in range(1, self.length + 1)
            if (x, y) not in filled
        ]

        diagonal_count = 0
        horiz_aisles = set()
        vert_aisles = set()

        for x, y in aisles:
            if (x+1, y+1) in aisles or (x-1, y-1) in aisles or (x+1, y-1) in aisles or (x-1, y+1) in aisles:
                diagonal_count += 1
            if (x+1, y) in aisles or (x-1, y) in aisles:
                horiz_aisles.add((x, y))
            if (x, y+1) in aisles or (x, y-1) in aisles:
                vert_aisles.add((x, y))

        cross_points = horiz_aisles & vert_aisles
        if not aisles:
            return 0
        score = 0.5 * (diagonal_count / len(aisles)) + 0.5 * (len(cross_points) / len(aisles))
        return score