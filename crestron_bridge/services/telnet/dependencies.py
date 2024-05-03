import telnetlib
import time
import logging


class TelnetManager:
    """A class to manage a telnet connection to a Crestron processor"""

    def __init__(self, host: str, port: int, timeout: int):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection = None

    def connect(self):
        self.connection = telnetlib.Telnet(self.host, self.port, self.timeout)
        time.sleep(1)
        ack = self.connection.read_very_eager().decode("ascii")

        success = "HELLO, I AM CONNECTED" in ack 

        # TODO: Add logging
        print("Connected to Crestron processor") if success else print("Failed to connect to Crestron processor")

        return success

    def send_command(self, command: str, wait_for: str = None):
        if not self.connection:
            raise RuntimeError("Telnet connection not established")

        if not command.endswith("\r\n"):
            command += "\r\n"

        try:
            self.connection.write(command.encode("ascii"))
        except (BrokenPipeError, EOFError) as e:
            print("Connection lost. Attempting to reconnect...")
            self.close()
            self.connect()
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

    def close(self):
        self.connection.close()
        self.connection = None
