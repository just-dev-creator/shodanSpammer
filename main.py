from quarry.net.server import ServerFactory, ServerProtocol
from twisted.internet import reactor

import logging
import os

# CONFIG

SERVER_MOTD = "LiveOverflow Let's Play"
SERVER_VERSION = "1.18.2"
SERVER_PORT = 25565
SERVER_MAX_PLAYERS = 20
SERVER_IP = "0.0.0.0"
ONLINE_MODE = True

# Configure logging
logger = logging.getLogger("honeypot")
if not os.path.exists("logs"):
    os.makedirs("logs")
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
file = logging.FileHandler("logs/honeypot.log")
file.setLevel(logging.INFO)
logger.addHandler(console)
logger.addHandler(file)


class QuarryProtocol(ServerProtocol):
    def player_joined(self):
        ServerProtocol.player_joined(self)
        logger.info("Player joined: {}".format(self.player.name))
        self.close("You are banned from this server\nReason: You are using shodan")


class QuarryFactory(ServerFactory):
    protocol = QuarryProtocol

    def __init__(self):
        self.motd = SERVER_MOTD
        self.max_players = SERVER_MAX_PLAYERS
        self.online_mode = ONLINE_MODE
        self.players = []
        # self.server.start()


def main():
    factory = QuarryFactory()
    logger.info("Server starting...")
    factory.listen(SERVER_IP, SERVER_PORT)
    reactor.run()


if __name__ == '__main__':
    main()