import mcstatus
import schedule
from quarry.net.server import ServerFactory, ServerProtocol
from twisted.internet import reactor

import logging
import os

# CONFIG

# Recommended - gets the current information from the real server
AUTO_MODE = True
REAL_SERVER_IP = ""

# Set values if not in auto mode
SERVER_MOTD = "LiveOverflow Let's Play"
SERVER_VERSION = "Paper 1.18.2"
SERVER_PROTOCOL_VERSION = 758
SERVER_PORT = 25565
SERVER_MAX_PLAYERS = 20
PLAYERS = []
SERVER_PLAYERS_ONLINE = len(PLAYERS)
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


def get_current_server_info():
    global SERVER_MOTD, SERVER_VERSION, SERVER_PROTOCOL_VERSION, SERVER_PORT, SERVER_MAX_PLAYERS, SERVER_IP, ONLINE_MODE, PLAYERS, SERVER_PLAYERS_ONLINE
    status = mcstatus.JavaServer(REAL_SERVER_IP, 25565).status()
    for player in status.players.sample:
        PLAYERS.append({
            "name": player.name,
            "id": player.id
        })
    SERVER_MOTD = status.description
    SERVER_VERSION = status.version.name
    SERVER_PROTOCOL_VERSION = status.version.protocol
    SERVER_MAX_PLAYERS = status.players.max
    SERVER_PLAYERS_ONLINE = status.players.online.real
    logger.info("Auto mode updated the server info")

class QuarryProtocol(ServerProtocol):
    def player_joined(self):
        ServerProtocol.player_joined(self)
        logger.info("Player joined: {} and ip {}".format(self.player.name, self.remote_addr.host))
        self.close("You are banned from this server\nReason: You are using shodan")

    def packet_status_request(self, buff):
        protocol_version = self.factory.force_protocol_version
        if protocol_version is None:
            protocol_version = self.protocol_version

        d = {
            "description": {
                "text": SERVER_MOTD
            },
            "players": {
                "online": SERVER_PLAYERS_ONLINE,
                "max": SERVER_MAX_PLAYERS,
                "sample": PLAYERS
            },
            "version": {
                "name": SERVER_VERSION,
                "protocol": SERVER_PROTOCOL_VERSION
            }
        }

        logger.info("Caught someone with ip: {}".format(self.remote_addr.host))
        # send status response
        self.send_packet("status_response", self.buff_type.pack_json(d))


class QuarryFactory(ServerFactory):
    protocol = QuarryProtocol


def main():
    # Schedule auto mode if applicable
    if AUTO_MODE:
        get_current_server_info()
        schedule.every(2).minutes.do(get_current_server_info)
    # Start honeypot server
    factory = QuarryFactory()
    logger.info("Server starting...")
    factory.listen(SERVER_IP, SERVER_PORT)
    reactor.run()


if __name__ == '__main__':
    main()
