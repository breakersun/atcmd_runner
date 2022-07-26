try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Please install the following packages:")
    print("pip install pyserial")
    print("pip install pyserial-tools")
    exit(1)

import logging
import re
from time import sleep

FORMAT = "%(levelname)7s %(asctime)s [%(filename)13s:%(lineno)4d] %(message)s"
DATEFMT = "%H:%M:%S"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATEFMT)
_logger = logging.getLogger(__name__)


class ATSerial:
    def __init__(self, port=None, log_level=logging.INFO, baudrate=115200):
        self.serial = self.find_serial_port(port, baudrate)
        self.input_timeout = 10
        _logger.setLevel(log_level)

    def find_serial_port(self, port, baudrate=115200, timeout=15):
        if port is not None:
            _logger.info("Using port: %s", port)
            return serial.Serial(port, baudrate, timeout=timeout)
        _logger.error("No serial port specified")

    def serial_write(self, cmd):
        cmd += "\r\n"
        _logger.debug(f"[running] {cmd}")
        self.serial.write(cmd.encode('utf-8'))

    def serial_command(self, cmd, expected_response):
        self.serial_write(cmd)
        response = ""
        while True:
            response += self.serial.readline().decode('utf-8')
            _logger.debug(f"[response] {response}")
            if expected_response in response:
                return True
            if self.serial.inWaiting() == 0:
                return False
