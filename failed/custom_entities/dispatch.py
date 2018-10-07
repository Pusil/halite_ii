import hlt
import custom_entities
from . import utilities
from . import constants
import time
import logging


class Dispatch:
    def __init__(self, game_map, my_map):
        self.game_map = game_map
        self.my_map = my_map
        self.ships = []
        self.create_ships()
        self.planets = []
        self.create_planets()
        self.squadrons = []

    def update(self, game_map):
        self.next_turn_ships = []
        self.game_map = game_map
        for planet in self.planets:
            planet.update(self.game_map)

        to_remove = []
        new_ships = [self.game_map.get_me().all_ships()[x].id for x in range(len(self.game_map.get_me().all_ships()))]
        for ship in self.ships:
            if ship.ship.id in new_ships:
                ship.update(self.game_map)
                new_ships.remove(ship.ship.id)
            else:
                to_remove.append(ship)

        for ship in to_remove:
            self.ships.remove(ship)
        del to_remove

        for ship in new_ships:
            self.create_ship(self.game_map.get_me().get_ship(ship))
        del new_ships

        for squadron in self.squadrons:
            squadron.update(self.game_map)

        dead_squadrons = []
        for squadron in self.squadrons:
            if not len(squadron.ships):
                dead_squadrons.append(squadron)

        for squadron in dead_squadrons:
            self.squadrons.remove(squadron)

        self.combine_squadrons()

        for squadron in self.squadrons:
            squadron.update_rest()

    def combine_squadrons(self):
        if len(self.squadrons) > 1:
            for squadron in self.squadrons:
                if not len(squadron.ships) > squadron.dangerous:
                    closest_squadron = None
                    entities_by_distance = utilities.get_nearby_sorted_squadron(squadron, self.squadrons)
                    dist = 0
                    for distance in entities_by_distance:
                        closest_squadron = entities_by_distance[distance][0]
                        dist = distance
                        break
                    if dist < constants.COMBINE_SQUADRONS and not len(closest_squadron.ships) > closest_squadron.dangerous:
                        self.combine_two_squadrons(squadron, closest_squadron)

    def combine_two_squadrons(self, squadron, second_squadron):
        for ship in second_squadron.ships:
            squadron.ships.append(ship)
        self.squadrons.remove(second_squadron)

    def get_targets(self):
        for ship in self.ships:
            if not ship.squadron:
                if not self.aggro(ship):
                    if not ship.mining:
                        self.get_target(ship)

    def get_target(self, ship):
        if ship.target:
            return

        entities_by_distance = utilities.get_nearby_sorted_planet(ship.ship, self.game_map)
        closest_planets = []
        for distance in entities_by_distance:
            if isinstance(entities_by_distance[distance][0], hlt.entity.Planet):
                for x in entities_by_distance[distance]:
                    closest_planets.append(x)

        for planet in closest_planets:
            for planet_object in self.planets:
                if planet.id == planet_object.planet.id:
                    if (not planet_object.enemy) and planet_object.can_take_miner():
                        planet_object.add_ship(ship)
                        ship.change_target(planet_object.planet)
                        return
        self.get_ship_target(ship)

    def aggro(self, ship):
        if ship.ship.docking_status != ship.ship.DockingStatus.UNDOCKED:
            return False
        entities_by_distance = utilities.get_nearby_sorted(ship.ship, self.game_map)
        for distance in entities_by_distance:
            if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0].owner.id != self.game_map.get_me().id:
                if distance < constants.AGGRO_DISTANCE:
                    for squadron in self.squadrons:
                        if utilities.calculate_distance_between(squadron, entities_by_distance[distance][0]) < utilities.calculate_distance_between(ship.ship, entities_by_distance[distance][0]) and utilities.calculate_distance_between(ship.ship, squadron) < constants.PROTECTED_DISTANCE:
                            return False
                    self.create_squadron(ship)
                    return True
        return False

    def get_ship(self, ship):
        for ship_object in self.ships:
            if ship_object.ship == ship:
                return ship_object
        return None

    def get_planet(self, ship):
        for planet in self.planets:
            if ship in planet.ships:
                return planet
        return None

    def get_commands(self):
        logging.info("number of ships: " + str(len(self.ships)))
        command_queue = []
        begin = time.time()
        for ship in self.ships:
            begin_ship = time.time()
            command = ship.get_command(self)
            if command:
                command_queue.append(command)
            end_ship = time.time()
            logging.info("time of single ship: " + str(end_ship - begin_ship))
        end = time.time()
        logging.info("time for getting commands: " + str(end - begin))
        return command_queue

    def get_ship_target(self, ship):
        entities_by_distance = utilities.get_nearby_sorted(ship.ship, self.game_map)
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if
                               isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                               entities_by_distance[distance][0].owner.id != self.game_map.get_me().id]
        ship.change_target(closest_enemy_ships[0])

    def create_ships(self):
        for ship in self.game_map.get_me().all_ships():
            self.create_ship(ship)

    def create_ship(self, ship):
        self.ships.append(custom_entities.Ships(ship, self.my_map, game_map=self.game_map))

    def create_planets(self):
        for planet in self.game_map.all_planets():
            self.planets.append(custom_entities.Planets(planet, game_map=self.game_map))

    def create_squadron(self, ship):
        self.squadrons.append(custom_entities.Squadron(ship, self, game_map=self.game_map))
