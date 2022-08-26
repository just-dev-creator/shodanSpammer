import mcstatus
SERVER_IP = "127.0.0.1"
SERVER_PORT = 25565

server = mcstatus.JavaServer(SERVER_IP, SERVER_PORT)
status = server.status()
print("Raw answer:" + str(status.raw))