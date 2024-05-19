import re
import telnetlib
import time
import logging
import threading
import queue

from crestron_bridge.services.state.lifetime import get_server_state


class TelnetManager:
    """A class to manage a telnet connection to a Crestron processor"""

    def __init__(self, host: str, port: int, timeout: int):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection = None
        self.requests = queue.Queue()
        self.responses = queue.Queue()
        self.server_state = get_server_state()
        self.lock = threading.RLock()

    def connect(self):
        self.connection = telnetlib.Telnet(self.host, self.port, self.timeout)
        time.sleep(1)
        ack = self.connection.read_very_eager().decode("ascii")

        success = "HELLO, I AM CONNECTED" in ack 

        # TODO: Add logging
        print("Connected to Crestron processor") if success else print("Failed to connect to Crestron processor")

        return success

    def send_command(self, command: str, priority: bool = False, timeout: int = 10, returning: bool = True):
        if not self.connection:
            raise RuntimeError("Telnet connection not established")

        if not command.endswith("\r\n"):
            command += "\r\n"

        with self.lock:
            if priority:
                priority_queue = queue.Queue()
                priority_queue.put(command)
                while not self.requests.empty():
                    priority_queue.put(self.requests.get())
                while not priority_queue.empty():
                    self.requests.put(priority_queue.get())
                self._execute_batch_commands()
            else:
                self.requests.put(command)

        if returning:
            start_time = time.time()
            while time.time() - start_time < timeout:
                with self.lock:
                    while not self.responses.empty():
                        response = self.responses.get()
                        if response.startswith(command.strip()):
                            return response
                        self.responses.put(response)
                time.sleep(0.1)
            raise TimeoutError(f"Timed out waiting for response to command: {command}")

    def send_batch_command(self, commands: list[str], timeout: int = 10):
        if not self.connection:
            raise RuntimeError("Telnet connection not established")

        batch_command = "\r\n".join(commands) + "\r\n"
        self.send_command(batch_command, priority=True, returning=False)

        start_time = time.time()
        responses = []
        while time.time() - start_time < timeout:
            with self.lock:
                while not self.responses.empty():
                    responses.append(self.responses.get())
                if len(responses) == len(commands):
                    return responses
            time.sleep(0.1)
        raise TimeoutError(f"Timed out waiting for responses to commands: {commands}")


    def _get_response(self, command: str):
        command = command.strip()
        while not self.responses.empty():
            response = self.responses.get()
            if response.startswith(command):
                return response
            self.responses.put(response)
        return None;

    def _execute_batch_commands(self):
        with self.lock:
            if not self.requests.empty():
                commands = []
                while not self.requests.empty():
                    commands.append(self.requests.get())
                batch_command = "\r\n".join(commands)
                try: 
                    self.connection.write(batch_command.encode("ascii"))
                except (BrokenPipeError, EOFError) as e:
                    logging.error("Connection lost. Attempting to reconnect.")
                    self.close()
                    self.connect()

    def _process_batch_commands(self):
        running = False
        while True:
            if self.connection:
                if not running:
                    print("Beginninng batch command execution")
                    running = True
                self._execute_batch_commands()
            else:
                if running:
                    print("No connection detected. Pausing batch command execution.")
                    running = False
            time.sleep(0.3)

    def _process_responses(self):
        running = False 
        while True:
            if self.connection:
                if not running:
                    print("Beginning response processing")
                    running = True
                try:
                    response = self.connection.read_until(b"\r\n").decode("ascii").strip()
                    self._handle_response(response)
                except (BrokenPipeError, EOFError) as e:
                    logging.error("Connection lost. Attempting to reconnect.")
                    self.close()
                    self.connect()
            else:
                if running:
                    print("No connection detected. Pausing response processing.")
                    running = False
            time.sleep(0.1)

    def _handle_response(self, response: str):
        if response.startswith("DISPATCH"):
            self._handle_dispatch(response)
        else:
            # print(f"Pushing response to queue: {response}")
            with self.lock:
                self.responses.put(response)

    def _handle_dispatch(self, response: str):
        # regex patterns for different dispatch types
        lights_pattern = r"^DISPATCH ([\w\s]+) LTS (S[1-3]|OFF) OK$"
        media_room_power_pattern = r"^DISPATCH MEDIA ROOM POWER (ON|OFF) OK$"
        media_room_source_pattern = r"DISPATCH MEDIA ROOM SRC (APPLETV|CABLE) OK$"
        audio_pattern = r"^DISPATCH ([\w\s]+) AUDIO SRC (SONOS|XM|FM|OFF)( OK$|)" # TODO: Update when fixed

        # Check for lights dispatch
        match = re.match(lights_pattern, response)
        if match:
            room = match.group(1)
            status = match.group(2)
            level = 100 if status == "S1" else 66 if status == "S2" else 33 if status == "S3" else 0
            is_active = "true" if status != "OFF" else "false"
            print(f"Updating light state for {room} to {status}")
            self.server_state.update_light_state(room=room, status=status, level=level, is_active=is_active)
            return

        # Check for media room power dispatch
        match = re.match(media_room_power_pattern, response)
        if match:
            status = match.group(1)
            print(f"Updating media room power state to {status}")
            self.server_state.update_media_room_state(status=status)
            return

        # Check for media room source dispatch
        match = re.match(media_room_source_pattern, response)
        if match:
            source = match.group(1)
            print(f"Updating media room source to {source}")
            self.server_state.update_media_room_state(source=source)
            return

        # Check for audio dispatch
        match = re.match(audio_pattern, response)
        if match:
            location = match.group(1)
            source = match.group(2)
            state = "ON" if source != "OFF" else "OFF"
            print(f"Updating audio state for {location} to {source}, {state}")
            self.server_state.update_audio_state(location=location, source=source, state=state)
            return

        # If no match is found, log an unknown dispatch message
        logging.warning(f"Unknown dispatch message: {response}")

    def close(self):
        self.connection.close()
        self.connection = None

    def start(self):
        self.connect()
        threading.Thread(target=self._process_batch_commands, daemon=True).start()
        threading.Thread(target=self._process_responses, daemon=True).start()

# def tm_get_current_state(tm: TelnetManager):
