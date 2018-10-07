import hlt
import logging
import custom_entities_V7

game = hlt.Game("Custom_Bot_V7")
logging.info("Starting the bot")
game_map = game.update_map()
dispatch = custom_entities_V7.Dispatch(game_map=game_map)
dispatch.update(game_map)
logging.info("getting targets in MyBot")
dispatch.get_targets()
logging.info("sending commands in MyBot")
game.send_command_queue(dispatch.get_commands())


while True:
    game_map = game.update_map()
    dispatch.update(game_map)
    dispatch.get_targets()
    command_queue = dispatch.get_commands()

    game.send_command_queue(command_queue)
