from crestron_bridge.services.state.dependencies import ServerState

state = ServerState()

def get_server_state():
    return state