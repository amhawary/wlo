import math
from __helpers import *

def getFitness(layout, weights):
    if weights:
        pass
    else:
        weights = [1, 1, 1, 1, 1, 1, 1]

    routes = []
    for operation in layout.operations:
        from_coord = operation.from_entity
        to_coord = operation.to_entity
        path = astar(from_coord, to_coord, layout, layout.aisle_width)
        if path:
            routes.append(path)

    travelDistance = calcAvrgRouteDistance()
    spaceUtilisation = calcSpaceUtilisation()
    congestionRisk = calcCongestionRisk()
    nturns = calcAvrgTurns()
    clustering = calcAvrgClustering()
    utilityAccess = calcUtilityAccess()

    fitness = (
        weights[0] * (1 - travelDistance) +
        weights[1] * spaceUtilisation +
        weights[2] * (1 - congestionRisk) +
        weights[3] * (1 - nturns) +
        weights[4] * clustering +
        weights[5] * utilityAccess 
    )

    return fitness

def calcCongestionRisk(routes, width, length):
    l = [[0 for x in range(width)] for y in range(length)]
    count = 0
    for route in routes:
        for x, y in route:
            l[x][y] += 1
            count += 1
    
    print(l)
    return

def calcAvrgRouteDistance(routes):
    totalDistance = 0
    min_distance = 
    max_distance =

    for route in routes: 
        distance = len(route) 
        totalDistance += distance 

        if max_distance < distance:
            max_distance = distance
        if min_distance > distance:
            min_distance = distance

    return totalDistance/len(routes)

def calcAvrgTurns(routes):
    total_turns = 0
    max_turns = len(routes[0])
    min_turns = len(routes[0])
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

            if max_turns < turns:
                max_turns = turns
            if min_turns > turns:
                min_turns = turns

    return normalise(total_turns/len(routes), min_turns, max_turns)


def calcSpaceUtilisation(routes, width, length):
    l = [[0 for x in range(width)] for y in range(length)]
    count = 0
    # get empty cells, 
    for route in routes:
        for x, y in route:
            l[x][y] += 1
            count += 1
    
    print(l)
    return

def calcSafety():
    pass

def calcAvrgClustering(layout):
    total_cluster_score = 0

    for category in layout.getEntityCategories:
        entities_in_category = get_entities(category)
        for i in range(len(entities_in_category)):
            for j in range(i+1, len(entities_in_category)):
                pos1 = entities_in_category[i].position
                pos2 = entities_in_category[j].position
                dist = manhattan_distance(pos1, pos2)
                total_cluster_score += 1 / (dist + 1)

def calcUtilityAccess(layout):
    total_utility_score = 0

    for entity in layout.entities:
        for required_utility in entity.required_utilities:
            nearest_point = find_nearest(utility_positions[required_utility], entity.position)
            dist = manhattan_distance(entity.position, nearest_point)
            total_utility_score += 1 / (dist + 1)  # +1 to avoid div by zero

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