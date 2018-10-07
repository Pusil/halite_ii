import heapq
import hlt
import math
from . import utilities
from . import constants
import logging
import time


def navigate(ship, end, game_map, my_map, dispatch):
    x = int(round(ship.x * constants.MAP_ACCURACY))
    y = int(round(ship.y * constants.MAP_ACCURACY))
    start = my_map.my_map[x][y]
    x = int(round(end.x * constants.MAP_ACCURACY))
    y = int(round(end.y * constants.MAP_ACCURACY))
    update_begin = time.time()
    goal = my_map.my_map[x][y]
    my_map.update(game_map, ship, dispatch)
    update_end = time.time()
    path_begin = time.time()
    path = theta_star(start, goal, game_map, end.radius, my_map, dispatch, ship)
    path_end = time.time()
    logging.info("time to update: " + str(update_end - update_begin))
    logging.info("time to get path: " + str(path_end - path_begin))

    if len(path) > 1:
        begin_x = path[-1].x / constants.MAP_ACCURACY
        begin_y = path[-1].y / constants.MAP_ACCURACY
        beginning = hlt.entity.Position(begin_x, begin_y)
        end_x = path[-2].x / constants.MAP_ACCURACY
        end_y = path[-2].y / constants.MAP_ACCURACY
        ending = hlt.entity.Position(end_x, end_y)
        speed = utilities.calculate_distance_between(beginning, ending)
        angle = utilities.calculate_angle_between(beginning, ending)

        if speed > hlt.constants.MAX_SPEED:
            speed = hlt.constants.MAX_SPEED
        temp_enemy_dx = math.cos(math.radians(round(angle))) * int(speed)
        temp_enemy_dy = math.sin(math.radians(round(angle))) * int(speed)
        new_location = hlt.entity.Position(temp_enemy_dx + ship.x, temp_enemy_dy + ship.y)
        update_ship(new_location, ship)
        return utilities.thrust(ship, speed, angle)
    return None


def theta_star(start, goal, game_map, radius, my_map, dispatch, ship_to_ignore):
    start.reset()
    start.change_g(0)
    start.change_h(utilities.calculate_distance_between(start, goal))
    start.parent = start
    openq = []
    closedq = []
    heapq.heappush(openq, start)

    while openq:
        loop_begin = time.time()
        s = heapq.heappop(openq)
        if s == goal or utilities.calculate_distance_between(s, goal) <= radius + 0.5 + constants.STOPPING_DISTANCE:
            return reconstruct_path(s)
        heapq.heappush(closedq, s)
        for neighbor_coordinates in s.neighbors:
            neighbor = my_map.my_map[neighbor_coordinates[0]][neighbor_coordinates[1]]
            if neighbor not in closedq:
                if neighbor not in openq:
                    neighbor.reset()
                if not neighbor.check_obstructed():
                    vertex_begin = time.time()
                    update_vertex(s, neighbor, openq, game_map, goal, dispatch, ship_to_ignore)
                    vertex_end = time.time()
                    logging.info("time for vertex: " + str(vertex_end - vertex_begin))
        loop_end = time.time()
        logging.info("time for one loop: " + str(loop_end - loop_begin))
    logging.info("no path was found")
    return None


def update_vertex(s, neighbor, openq, game_map, goal, dispatch, ship_to_ignore):
    if not utilities.obstacles_between_theta_star(game_map, s.parent, neighbor, ship_to_ignore, dispatch):
        if s.parent.g + utilities.calculate_distance_between(s.parent, neighbor) < neighbor.g:
            neighbor.change_g(s.parent.g + utilities.calculate_distance_between(s.parent, neighbor))
            neighbor.change_h(utilities.calculate_distance_between(neighbor, goal))
            neighbor.parent = s.parent
            if neighbor in openq:
                openq.remove(neighbor)
                heapq.heapify(openq)
            heapq.heappush(openq, neighbor)
    else:
        if s.g + utilities.calculate_distance_between(s, neighbor) < neighbor.g:
            neighbor.change_g(s.g + utilities.calculate_distance_between(s, neighbor))
            neighbor.change_h(utilities.calculate_distance_between(neighbor, goal))
            neighbor.parent = s
            if neighbor in openq:
                openq.remove(neighbor)
                heapq.heapify(openq)
            heapq.heappush(openq, neighbor)


def reconstruct_path(s):
    total_path = list()
    total_path.append(s)
    if s.parent != s:
        path = reconstruct_path(s.parent)
        total_path += path
        return total_path
    else:
        return total_path


def update_ship(new_location, ship):
    ship.x = new_location.x
    ship.y = new_location.y
