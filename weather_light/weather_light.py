import argparse
import logging
import signal

from util.light_controller import LightController
from util.logger import Logger
from util.weather_watcher import WeatherWatcher
from util.server.config_server import ConfigServer

update_weather = True


def signal_handler(sig, frame):
    """
    Handle SIGINT
    :param sig: sigint
    :param frame: frame
    :return: None
    """
    LightController.reset_spwm()


def parse_args():
    """
    Parse args
    :return: Namespace
    """
    global update_weather
    arg_parser = argparse.ArgumentParser(description="WeatherLight")
    arg_parser.add_argument("-p", "--pwm-debug", action="store_const", const=True, default=False,
                            help="Enable PWM debug output")
    arg_parser.add_argument("-log", type=str, help="Log level: FATAL CRITICAL ERROR WARN INFO DEBUG",
                            default=logging.INFO)
    arg_parser.add_argument("-i", "--inverted", action="store_const", const=True, default=False,
                            help="Invert the PWN output")
    arg_parser.add_argument("-n", "--no-weather", action="store_const", const=True, default=False,
                            help="Do not start the weather update thread")
    args = arg_parser.parse_args()
    LightController.enable_debug(args.pwm_debug)
    LightController.set_inverted(args.inverted)
    Logger.set_level(args.log)
    update_weather = not args.no_weather


if __name__ == "__main__":
    parse_args()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    LightController.start_light()
    weather_watcher = WeatherWatcher()
    if update_weather:
        weather_watcher.start()
    else:
        Logger.get_logger().info("Weather will not be updated")
    config_server = ConfigServer()
    config_server.start()
    signal.pause()
