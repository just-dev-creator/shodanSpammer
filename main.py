import mcstatus
from quarry.net.server import ServerFactory, ServerProtocol
from twisted.internet import reactor
from dotenv import load_dotenv

import logging
import os

# CONFIG

load_dotenv()
SERVER_MOTD = "LiveOverflow Let's Play"
SERVER_VERSION = "Paper 1.18.2"
SERVER_PROTOCOL_VERSION = 758
SERVER_PORT = 25565
SERVER_MAX_PLAYERS = 20
SERVER_IP = "0.0.0.0"
ONLINE_MODE = True
# Players in the sample player list. Set to None to get live player list from the real server.
PLAYERS = None
# If you want to get the player list from the real server, set the real server ip here. It's already public knowledge
# but don't want to leak it here.
REAL_SERVER_IP = ""

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
        logger.info("Player joined: {} and ip {}".format(self.player.name, self.remote_addr.host))
        self.close("You are banned from this server\nReason: You are using shodan")

    def packet_status_request(self, buff):
        protocol_version = self.factory.force_protocol_version
        if protocol_version is None:
            protocol_version = self.protocol_version

        d = {
            "description": {
                "text": self.factory.motd
            },
            "players": {
                "online": len(self.factory.players),
                "max": self.factory.max_players,
                "sample": self.factory.players
            },
            "version": {
                "name": SERVER_VERSION,
                "protocol": SERVER_PROTOCOL_VERSION
            }
        }

        logger.info("Caught someone with ip: {}".format(self.remote_addr.host))
        # send status response
        self.send_packet("status_response", self.buff_type.pack_json(d))


def get_players_real_server():
    status = mcstatus.JavaServer(REAL_SERVER_IP, 25565).status()
    players = []
    for player in status.players.sample:
        players.append({
            "name": player.name,
            "id": player.id
        })
    return players


class QuarryFactory(ServerFactory):
    protocol = QuarryProtocol

    def __init__(self):
        self.motd = SERVER_MOTD
        self.max_players = SERVER_MAX_PLAYERS
        self.online_mode = ONLINE_MODE
        self.minecraft_versions = SERVER_VERSION
        if PLAYERS is None and REAL_SERVER_IP != "":
            # Get real server player list
            self.players = get_players_real_server()
        else:
            self.players = []


def main():
    factory = QuarryFactory()
    logger.info("Server starting...")
    factory.listen(SERVER_IP, SERVER_PORT)
    reactor.run()


if __name__ == '__main__':
    main()
