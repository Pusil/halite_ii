import hlt
from random import randint
from . import utilities
import logging


class Ships:
    def __init__(self, ship, target=None, game_map=None, squadron=False, mining=False, speed=hlt.constants.MAX_SPEED):
        self.ship = ship
        self.x = self.ship.x
        self.y = self.ship.y
        self.radius = self.ship.radius
        self.target = target
        self.game_map = game_map
        self.squadron = squadron
        self.mining = mining
        self.speed = speed

    def update(self, game_map):
        self.speed = hlt.constants.MAX_SPEED
        self.game_map = game_map
        self.ship = self.game_map.get_me().get_ship(self.ship.id)
        logging.info(str(abs(self.x - self.ship.x)) + ", " + str(abs(self.y - self.ship.y)))
        self.x = self.ship.x
        self.y = self.ship.y
        if self.target:
            if isinstance(self.target, hlt.entity.Planet):
                self.change_target(self.game_map.get_planet(self.target.id))
            elif not isinstance(self.target, hlt.entity.Position):
                self.change_target(self.game_map.get_player(self.target.owner.id).get_ship(self.target.id))

    def change_target(self, target):
        self.target = target

    def get_command(self, dispatch):
        command = None

        if self.ship.docking_status != self.ship.DockingStatus.UNDOCKED:
            if isinstance(self.target, hlt.entity.Ship):
                return self.ship.undock()
            else:
                return command

        if isinstance(self.target, hlt.entity.Planet):
            if self.ship.can_dock(self.target):
                command = self.ship.dock(self.target)
                return command

        command = utilities.navigate(
            self.ship,
            self.ship.closest_point_to(self.target),
            self.game_map,
            speed=int(self.speed),
            angular_step=2,
            max_corrections=90,
            dispatch=dispatch
        )

        return command
