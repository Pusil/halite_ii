class Planets:
    def __init__(self, planet, game_map=None, mine=False, owned=False, enemy=False):
        self.planet = planet
        self.ships = []
        self.game_map = game_map
        self.mine = mine
        self.owned = owned
        self.enemy = enemy

    def remove_miner(self, ship):
        self.ships.remove(ship)

    def get_num_miners(self):
        return len(self.ships)

    def can_take_miner(self):
        if len(self.ships) < self.planet.num_docking_spots:
            return True
        return False

    def add_ship(self, ship):
        if ship not in self.ships and self.can_take_miner():
            self.ships.append(ship)
            return True
        return False

    def update(self, game_map):
        self.game_map = game_map
        self.planet = self.game_map.get_planet(self.planet.id)

        self.mine = self.planet.owner is self.game_map.get_me()
        self.owned = self.planet.owner is not None
        self.enemy = (self.planet.owner is not self.game_map.get_me()) and self.owned

        new_ships = game_map.get_me().all_ships()
        dead_ships = []
        for ship in self.ships:
            if not game_map.get_me().get_ship(ship.ship.id) in new_ships:
                dead_ships.append(ship)

        for ship in dead_ships:
            self.remove_miner(ship)
