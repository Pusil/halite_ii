import hlt
from collections import OrderedDict

import time
import logging


class Ships:

    def __init__(self, ship, target=None):
        self.ship = ship
        self.target = target
        self.checkpoints = []

    def change_target(self, target):
        self.target = target

    def get_command(self, game_map):
        self.checkpoints = []
        self.checkpoints.append(("beginning", time.time()))
        command = self.get_command_wrapped(game_map)
        self.checkpoints.append(("end of individual command", time.time()))
        logging.info("command total time: ")
        logging.info(self.checkpoints[-1][1] - self.checkpoints[0][1])
        logging.info("individual command times")
        for x in range(len(self.checkpoints)):
            if x == 0:
                continue
            else:
                if self.checkpoints[x][1] - self.checkpoints[x - 1][1] > 0.01:
                    logging.info(self.checkpoints[x][0])
                    logging.info(self.checkpoints[x][1] - self.checkpoints[x - 1][1])
        return command

    def get_command_wrapped(self, game_map):
        self.update(game_map)

        self.checkpoints.append(("updated", time.time()))

        command = None
        if not self.target:
            self.get_target(game_map)

        self.checkpoints.append(("got target", time.time()))

        if self.ship.docking_status != self.ship.DockingStatus.UNDOCKED:
            return command

        self.checkpoints.append(("if undocked", time.time()))

        if isinstance(self.target, hlt.entity.Planet) and self.ship.can_dock(self.target):
            command = self.ship.dock(self.target)
            return command

        self.checkpoints.append(("dock", time.time()))

        command = self.ship.navigate(
            self.ship.closest_point_to(self.target),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False
        )

        return command

    def get_target(self, game_map):
        entities_by_distance = game_map.nearby_entities_by_distance(self.ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0].owner.id != game_map.get_me().id]
        self.target = closest_enemy_ships[0]

    def update(self, game_map):
        self.ship = game_map.get_me().get_ship(self.ship.id)
        if self.target:
            if isinstance(self.target, hlt.entity.Planet):
                self.target = game_map.get_planet(self.target.id)
            else:
                self.target = game_map.get_player(self.target.owner.id).get_ship(self.target.id)
