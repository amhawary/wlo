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

    travelDistance = calc_avrg_distance()
    # spaceUtilisation = calc_space_utilisation()
    congestionRisk = calc_congestion_risk()
    nturns = calc_avrg_turns()
    # clustering = calcAvrgClustering()
    # utilityAccess = calcUtilityAccess()

    fitness = (
        weights[0] * (1 - travelDistance) +
    #    weights[1] * spaceUtilisation +
        weights[2] * (1 - congestionRisk) +
        weights[3] * (1 - nturns)
    #   weights[4] * clustering +
    #    weights[5] * utilityAccess 
    )

    return fitness

def calc_congestion_risk(routes, width, length):
    l = [[0 for x in range(width)] for y in range(length)]
    count = 0
    for route in routes:
        for x, y in route:
            l[x][y] += 1
            count += 1
    
    congested_paths = []
    for x in range(width):
        for y in range(length):
            if l[x][y] != 0:
                congested_paths.append(l[x][y])

    max_congestion = max(congested_paths)
    min_congestion = min(congested_paths)
    avrg_congestion = sum(congested_paths) / len(congested_paths)
    
    return avrg_congestion

def calc_avrg_distance(routes):

    distances = []
    for route in routes: 
        distances.append(len(route))

    max_distance = max(distances)
    min_distance = min(distances)
    avrg_distance = sum(distances)/len(routes)
    
    return avrg_distance

def calc_avrg_turns(routes):
    turns_list = []
    for index, path in enumerate(routes):
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

    max_turns = max(turns_list)
    min_turns = min(turns_list)
    avrg_turns = sum(turns_list)/len(turns_list)

    return avrg_turns
    return normalise(avrg_turns, min_turns, max_turns)

def calc_space_utilisation(width, length):
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

    for category in layout.utilities.keys():
        entities_in_category = layout.get_category_entities()
        for i in range(len(entities_in_category)):
            for j in range(i+1, len(entities_in_category)):
                pos1 = entities_in_category[i].position
                pos2 = entities_in_category[j].position
                dist = manhattan_distance(pos1, pos2)
                total_cluster_score += 1 / (dist + 1)

def calcUtilityAccess(layout):
    total_utility_score = 0

    #for entity in layout.entities:
            
            # nearest_point = 
            #dist = manhattan_distance(entity.position, nearest_point)
            # stotal_utility_score += 1 / (dist + 1)  # +1 to avoid div by zero

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