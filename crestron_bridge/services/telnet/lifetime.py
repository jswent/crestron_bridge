from crestron_bridge.services.telnet.dependencies import TelnetManager

HOST = "172.20.60.45"
PORT = 41702
TIMEOUT = 10

telnet_manager = TelnetManager(HOST, PORT, TIMEOUT)


async def startup_event():
    telnet_manager.connect()


async def shutdown_event():
    telnet_manager.close()


def get_telnet_manager():
    return telnet_manager
