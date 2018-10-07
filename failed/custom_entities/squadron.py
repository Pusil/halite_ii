import hlt
from . import utilities
from . import constants


class Squadron:
    def __init__(self, ship, dispatch, game_map=None):
        self.game_map = game_map
        self.dispatch = dispatch
        self.ships = [ship]
        self.x = ship.ship.x
        self.y = ship.ship.y
        self.dangerous = 1
        ship.squadron = True
        self.target = None
        self.radius = 0

        self.update(game_map)
        self.update_rest()

    def update(self, game_map):
        self.game_map = game_map

        for ship in self.ships:
            ship.squadron = True

        new_ships = [self.game_map.get_me().all_ships()[x].id for x in range(len(self.game_map.get_me().all_ships()))]
        dead_ships = []
        for ship in self.ships:
            if ship.ship.id not in new_ships:
                dead_ships.append(ship)

        for ship in dead_ships:
            self.ships.remove(ship)

    def update_rest(self):
        self.update_enemies()
        self.update_position()
        self.find_target()

    def find_target(self):
        if len(self.ships) > self.dangerous:
            if self.get_present() > self.dangerous:
                self.safe()
            else:
                self.attack()
        else:
            self.grow()

        for ship in self.ships:
            ship.change_target(self.target)

    def safe(self):
        self.navigate_safe_distance()

    def attack(self):
        self.target = utilities.get_nearest_enemy(self, self.game_map)

    def grow(self):
        need = self.dangerous + 1 - len(self.ships)
        entities_by_distance = utilities.get_nearby_sorted_docked(self, self.game_map)
        for distance in entities_by_distance:
            if need:
                if distance < constants.RECRUIT_DISTANCE:
                    if isinstance(entities_by_distance[distance][0], hlt.entity.Ship):
                        if entities_by_distance[distance][0].owner == self.game_map.get_me():
                            for ship in entities_by_distance[distance]:
                                if need:
                                    if self.recruit(ship):
                                        need -= 1
        self.navigate_safe_distance()

    def recruit(self, ship):
        ship_object = self.dispatch.get_ship(ship)
        if ship_object in self.ships:
            return False
        if ship_object.squadron:
            return False
        if ship_object.mining:
            planet = self.dispatch.get_planet(ship_object)
            ship_object.mining = False
            ship_object.squadron = True
            planet.remove_miner(ship_object)
            self.ships.append(ship_object)
            return True
        ship_object.squadron = True
        self.ships.append(ship_object)
        return True

    def navigate_safe_distance(self):
        enemy = utilities.get_nearest_enemy(self, self.game_map)
        position = utilities.clean_enemy(self, enemy)
        self.target = position

    def update_enemies(self):
        enemy = utilities.get_nearest_enemy(self.ships[0].ship, self.game_map)
        self.dangerous = 1
        entities_by_distance = utilities.get_nearby_sorted(enemy, self.game_map)
        for distance in entities_by_distance:
            if distance < constants.GROUPING_DISTANCE:
                if isinstance(entities_by_distance[distance][0], hlt.entity.Ship):
                    if entities_by_distance[distance][0].owner != self.game_map.get_me():
                        if entities_by_distance[distance][0].docking_status == entities_by_distance[
                                distance][0].DockingStatus.UNDOCKED:
                            self.dangerous += 1

    def get_present(self):
        present = 0
        entities_by_distance = utilities.get_nearby_sorted_docked(utilities.get_nearest_friendly(utilities.get_nearest_enemy(self, self.game_map), self.game_map), self.game_map)
        for distance in entities_by_distance:
            if distance < constants.FRIENDLY_GROUPING_DISTANCE:
                if isinstance(entities_by_distance[distance][0], hlt.entity.Ship):
                    if self.dispatch.get_ship(entities_by_distance[distance][0]) in self.ships:
                        present += 1
        return present

    def update_position(self):
        x = 0
        y = 0
        for ship in self.ships:
            if utilities.calculate_distance_between(self, ship.ship) < constants.FRIENDLY_GROUPING_DISTANCE:
                x += ship.ship.x
                y += ship.ship.y
        if x:
            self.x = x / len(self.ships)
            self.y = y / len(self.ships)
        else:
            ship = self.get_closest_attacking_ship()
            self.x = ship.ship.x
            self.y = ship.ship.y

    def get_closest_attacking_ship(self):
        closest = 500
        closest_ship = None
        for ship in self.ships:
            if utilities.calculate_distance_between(self, ship.ship) < closest:
                closest_ship = ship
        return closest_ship
