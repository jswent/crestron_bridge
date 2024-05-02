import telnetlib
import time
import logging
from threading import Lock

class TelnetManager:
    """A class to manage a telnet connection to a Crestron processor"""

    def __init__(self, host: str, port: int, timeout: int):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection = None
        self.lock = Lock()

    def connect(self):
        with self.lock:
            if self.connection is None:
                try:
                    self.connection = telnetlib.Telnet(self.host, self.port, self.timeout)
                    time.sleep(1)
                    ack = self.connection.read_very_eager().decode("ascii")
                    success = "HELLO, I AM CONNECTED" in ack
                    if success:
                        logging.info("Connected to Crestron processor")
                    else:
                        logging.error("Failed to connect to Crestron processor")
                    return success
                except Exception as e:
                    logging.error(f"Error connecting to Crestron processor: {str(e)}")
                    return False
            else:
                logging.warning("A connection is already established")
                return True

    def send_command(self, command: str, wait_for: str = None):
        with self.lock:
            if self.connection is None:
                raise RuntimeError("Telnet connection not established")

            try:
                if not command.endswith("\r\n"):
                    command += "\r\n"
                self.connection.write(command.encode("ascii"))

                if wait_for:
                    response = self.connection.read_until(
                        wait_for.encode("ascii"),
                        self.timeout,
                    ).decode("ascii")
                else:
                    time.sleep(1)
                    response = self.connection.read_very_eager().decode("ascii")

                return response

            except (BrokenPipeError, EOFError) as e:
                logging.error(f"Connection lost: {str(e)}. Attempting to reconnect...")
                self.close()
                self.connect()
                return self.send_command(command, wait_for)

    def close(self):
        with self.lock:
            if self.connection is not None:
                self.connection.close()
                self.connection = None