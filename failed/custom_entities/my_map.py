import hlt
from . import utilities
from . import constants
import math
import logging


class Node:
    def __init__(self, x, y, my_map):
        self.radius = 0.5
        self.my_map = my_map
        self.x = x
        self.y = y
        self.neighbors = self.make_neighbors()
        self.g = 1000
        self.h = 0
        self.f = self.g + self.h
        self.parent = None
        self.obstructed = False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if self.f == other.f:
                return self.h < other.h
            return self.f < other.f
        return NotImplemented

    def reset(self):
        self.g = 1000
        self.change_h(0)
        self.parent = None
        self.obstructed = False

    def check_obstructed(self):
        # return self.my_map.check_obstructed(self.x, self.y)
        return self.obstructed

# TODO: I think this is useless so probably get rid of it
    def get_neighbors(self):
        neighbors = []

        for x in self.neighbors:
            for y in self.neighbors[x]:
                if 0 >= x < self.my_map.x and 0 >= y < self.my_map.y:
                    neighbors.append(self.my_map.my_map[x][y])

        return neighbors

    def change_g(self, g):
        self.g = g
        self.f = self.g + self.h

    def change_h(self, h):
        self.h = h
        self.f = self.g + self.h

    def make_neighbors(self):
        neighbors = []
        x = -1
        while x < 2:
            y = -1
            while y < 2:
                if x or y:
                    if (0 <= x + self.x < self.my_map.x) and (0 <= y + self.y < self.my_map.y):
                        neighbors.append((self.x + x, self.y + y))
                y += 1
            x += 1
        return neighbors


class Map:
    def __init__(self, game_map):
        self.x = game_map.width * constants.MAP_ACCURACY
        self.y = game_map.height * constants.MAP_ACCURACY
        self.game_map = game_map
        self.my_map = self.create_map()

    def update(self, game_map, ship_to_ignore, dispatch):
        self.game_map = game_map
        self.create_obstructions(ship_to_ignore, dispatch)

    def create_map(self):
        nodes = [[None for _ in range(self.y)] for _ in range(self.x)]
        for x in range(self.x):
            for y in range(self.y):
                nodes[x][y] = Node(x, y, self)
        return nodes

    def create_obstructions(self, ship_to_ignore, dispatch):
        entities = utilities.almost_all_ships(self.game_map, ship_to_ignore, dispatch)
        entities += self.game_map.all_planets()
        for entity in entities:
            self.check_neighbors(int(round(entity.x * constants.MAP_ACCURACY)), int(round(entity.y * constants.MAP_ACCURACY)), entity)

    def check_neighbors(self, x, y, entity):
        radius = int(math.ceil((entity.radius + 0.5 + 0.5) * constants.MAP_ACCURACY)) + 1
        j = -radius
        while j <= radius:
            k = -radius
            while k <= radius:
                if not self.my_map[x + j][y + k].obstructed:
                    place = hlt.entity.Position((x + j) / constants.MAP_ACCURACY, (y + k) / constants.MAP_ACCURACY)
                    if utilities.calculate_distance_between(place, entity) < entity.radius + 0.5 + 0.5:
                        self.mark_obstructed((x + j), (y + k))
                k += 1
            j += 1

    def mark_obstructed(self, x, y):
        self.my_map[x][y].obstructed = True
