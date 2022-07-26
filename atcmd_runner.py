import pathlib

from atcmd_controller import ATSerial
import logging
import json

FORMAT = "%(levelname)7s %(asctime)s [%(filename)13s:%(lineno)4d] %(message)s"
DATEFMT = "%H:%M:%S"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATEFMT)
_logger = logging.getLogger(__name__)


class CmdRunner:
    def __init__(self, script_file, port=None, log_level=logging.INFO, baudrate=115200):
        self.script_path = pathlib.Path(script_file)

        with open(script_file) as f:
            self.script = json.load(f)
            if "check_points" not in self.script:
                raise Exception("No check points specified")

            self.check_points = self.script["check_points"]
            _logger.debug(f"Check points: {self.check_points}")

            if 'serial' in self.script:
                self.serial = ATSerial(self.script['serial'], log_level, baudrate)
            else:
                self.serial = ATSerial(port, log_level, baudrate)

    def run(self):
        for check_point in self.check_points:
            _cmd = check_point['cmd']
            _expected_responses = check_point['answers']
            _result = False
            for _expected_response in _expected_responses:
                _result = _result or self.serial.serial_command(_cmd, _expected_response)
                if _result:
                    break
            if not _result:
                raise Exception(f"Command {_cmd} failed")
            else:
                _logger.info(f"Command {_cmd} passed")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AT Command Runner")
    parser.add_argument("-s", "--script", help="AT Command Script", required=True)
    parser.add_argument("-p", "--port", help="Serial Port")
    parser.add_argument("-l", "--log-level", help="Log Level", default=logging.DEBUG)
    parser.add_argument("-b", "--baudrate", help="Baudrate", default=115200)
    args = parser.parse_args()
    _logger.setLevel(args.log_level)
    runner = CmdRunner(args.script, args.port, args.log_level, args.baudrate)
    runner.run()
    # runner.serial.serial.close()
    exit(0)
