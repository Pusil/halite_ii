import hlt
import logging
import custom_entities_V3
from collections import OrderedDict

import time


def create_target(_ship, _game_map):
    entities_by_distance = _game_map.nearby_entities_by_distance(_ship)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
    closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if
                             isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not
                             entities_by_distance[distance][0].is_owned()]
    if len(closest_empty_planets) > 0:
        return closest_empty_planets[0]
    return None

game = hlt.Game("Custom_Bot_V3")
logging.info("Starting the bot")

ship_ids = []
ships = []


while True:
    checkpoints = []
    checkpoints.append(("beginning of loop", time.time()))

    game_map = game.update_map()
    command_queue = []

    checkpoints.append(("after initialized", time.time()))

    new_ships = game_map.get_me().all_ships()

    checkpoints.append(("got ships", time.time()))

    for ship in new_ships:
        if ship.id in ship_ids:
            continue
        else:
            ships.append(custom_entities_V3.Ships(ship, target=create_target(ship, game_map)))
            ship_ids.append(ship.id)

    checkpoints.append(("looped through ships", time.time()))

    ids = []
    s = []
    for place in range(len(ship_ids)):
        if game_map.get_me().get_ship(ship_ids[place]) in new_ships:
            ids.append(ship_ids[place])
            s.append(ships[place])
    ship_ids = ids
    ships = s
    del ids
    del s

    checkpoints.append(("removed destroyed ships", time.time()))

    for ship in ships:
        command = ship.get_command(game_map)
        if command:
            command_queue.append(command)

    checkpoints.append(("got commands", time.time()))

    game.send_command_queue(command_queue)

    checkpoints.append(("sent commands", time.time()))
    for x in range(len(checkpoints)):
        if x != 0:
            if checkpoints[x][1] - checkpoints[x - 1][1] > 0.3:
                logging.info(checkpoints[x][0])
                logging.info(checkpoints[x][1] - checkpoints[x - 1][1])
    if checkpoints[-1][1] - checkpoints[0][1] >= 1:
        logging.info("#########LONG MOVE#########")
        logging.info(checkpoints[-1][1] - checkpoints[0][1])
