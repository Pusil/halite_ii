import hlt
import logging
import custom_entities
import time

game = hlt.Game("Custom_Bot_V8")
my_map = custom_entities.Map(game.map)
logging.info("Starting the bot")
game_map = game.update_map()
dispatch = custom_entities.Dispatch(game_map, my_map)
dispatch.update(game_map)
logging.info("getting targets in MyBot")
dispatch.get_targets()
logging.info("sending commands in MyBot")
game.send_command_queue(dispatch.get_commands())


while True:
    begin = time.time()
    game_map = game.update_map()
    dispatch.update(game_map)
    dispatch.get_targets()
    command_queue = dispatch.get_commands()

    end = time.time()
    logging.info("whole turn time: " + str(end - begin))

    game.send_command_queue(command_queue)
