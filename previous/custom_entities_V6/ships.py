import hlt
from collections import OrderedDict


class Ships:

    def __init__(self, ship, target=None, game_map=None):
        self.ship = ship
        self.target = target
        self.game_map = game_map

    def change_target(self, target):
        self.target = target

    def get_command(self, game_map):
        self.game_map = game_map
        self.update()

        command = None
        if not self.target:
            self.get_target()

        if self.ship.docking_status != self.ship.DockingStatus.UNDOCKED:
            return command

        self.aggro()

        if isinstance(self.target, hlt.entity.Planet):
            if self.ship.can_dock(self.target):
                command = self.ship.dock(self.target)
                return command
            if self.target.is_full():
                self.get_target()
            elif self.target.is_owned():
                if self.target.owner.id != self.game_map.get_me().id:
                    self.get_target()

        command = self.ship.navigate(
            self.ship.closest_point_to(self.target),
            self.game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False,
            angular_step=5
        )

        return command

    def aggro(self):
        entities_by_distance = self.game_map.nearby_entities_by_distance(self.ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        for distance in entities_by_distance:
            if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0].owner.id != self.game_map.get_me().id:
                if distance < 10:
                    self.target = entities_by_distance[distance][0]
                return
        return

    def get_target(self):
        entities_by_distance = self.game_map.nearby_entities_by_distance(self.ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0].owner.id != self.game_map.get_me().id]
        self.target = closest_enemy_ships[0]

    def update(self):
        self.ship = self.game_map.get_me().get_ship(self.ship.id)
        if self.target:
            if isinstance(self.target, hlt.entity.Planet):
                self.target = self.game_map.get_planet(self.target.id)
            else:
                self.target = self.game_map.get_player(self.target.owner.id).get_ship(self.target.id)
