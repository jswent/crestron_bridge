from crestron_bridge.services.commander.dependencies import Commander

commander = Commander()

async def startup_event():
  commander.initialize_device_states()

async def shutdown_event():
  commander.close()

def get_commander():
  return commander