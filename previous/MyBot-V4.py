import hlt
import logging
import custom_entities_V4
from collections import OrderedDict


def create_target(_ship, _game_map):
    entities_by_distance = _game_map.nearby_entities_by_distance(_ship)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
    closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if
                             isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and (not
                             entities_by_distance[distance][0].is_owned() or (not
                                entities_by_distance[distance][0].is_full() and
                                entities_by_distance[distance][0].owner.id == game_map.get_me().id))]
    if len(closest_empty_planets) > 0:
        return closest_empty_planets[0]
    return None

game = hlt.Game("Custom_Bot_V4")
logging.info("Starting the bot")

ship_ids = []
ships = []


while True:
    game_map = game.update_map()
    command_queue = []

    new_ships = game_map.get_me().all_ships()

    for ship in new_ships:
        if ship.id in ship_ids:
            continue
        else:
            ships.append(custom_entities_V4.Ships(ship, target=create_target(ship, game_map)))
            ship_ids.append(ship.id)

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

    for ship in ships:
        command = ship.get_command(game_map)
        if command:
            command_queue.append(command)

    game.send_command_queue(command_queue)
