
BUFFER_SIZE = 4096
PACKET_DROP_RATE = 0

BROADCAST_INTERVAL = 6

LISTENING_PORT = 8880
TCP_BACKLOG = 5

HUB_ADDRESS = ("127.0.0.1", 9000)
HUB_TIMEOUT = 6

AVAILABLE_PORTS = range(9001, 10001)


class NodeCommand():
    SHUTDOWN = "shutdown"
    OK = "ok"
    EXIT = "exit"
    DESCRIBE = "describe"
    DISPLAY = "display"
    ECHO = "echo"
    DISPLAY_NODE = "display_node"
    PEERS = "peers"