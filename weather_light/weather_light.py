import argparse
import logging
import signal
import time

from util.light_controller import LightController
from util.weather_watcher import WeatherWatcher
from util.logger import Logger

from data.color import Color

from util.switch_poller import SwitchPoller


def signal_handler(sig, frame):
    """
    Handle SIGINT
    :param sig: sigint
    :param frame: frame
    :return: None
    """
    LightController.reset_spwm()
    SwitchPoller.reset_gpio()


def parse_args():
    """
    Parse args
    :return: Namespace
    """
    arg_parser = argparse.ArgumentParser(description="WeatherLight")
    arg_parser.add_argument("-p", "--pwm-debug", action="store_const", const=True, default=False,
                            help="Enable PWM debug output")
    arg_parser.add_argument("-log", type=str, help="Log level: FATAL CRITICAL ERROR WARN INFO DEBUG",
                            default=logging.INFO)
    arg_parser.add_argument("-i", "--inverted", action="store_const", const=True, default=False,
                            help="Invert the PWN output")
    args = arg_parser.parse_args()
    LightController.enable_debug(args.pwm_debug)
    LightController.set_inverted(args.inverted)
    Logger.set_level(args.log)


if __name__ == "__main__":
    parse_args()
    signal.signal(signal.SIGINT, signal_handler)
    LightController.start_light()
    weather_watcher = WeatherWatcher()
    weather_watcher.start()
    signal.pause()
