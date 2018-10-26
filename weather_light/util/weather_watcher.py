import time
from threading import Thread

import requests
from util.logger import Logger

from data import default_config
from util.config import Config

from data.color import Color
from util.light_controller import LightController


class WeatherWatcher:
    UPDATE_INTERVAL = 60 * 60 * 3  # 3 hours
    RETRY_INTERVAL = 60 * 10  # 10 minutes
    API_KEY = "17049ae6b6187712ea3e0fb2ffc1bac6"

    def __init__(self):
        self.running = False
        self.last_update_time = 0

    def start(self):
        """
        Start the weather update thread
        :return: None
        """
        self.running = True
        weather_thread = Thread(target=self.run)
        weather_thread.setDaemon(True)
        weather_thread.setName("WeatherWatcher")
        weather_thread.start()

    def run(self):
        """
        Internal main loop
        :return: None
        """
        while self.running:
            time_since_last_update = time.time() - self.last_update_time
            # Update every three hours
            if time_since_last_update >= self.UPDATE_INTERVAL:
                weather_code = self.get_weather_code()
                if weather_code is not None:
                    try:
                        self.handle_weather_code(weather_code)
                    except Exception as e:
                        Logger.get_logger().exception(e)
                    self.last_update_time = time.time()
                else:
                    self.last_update_time = time.time() - self.RETRY_INTERVAL

    def get_weather_code(self):
        """
        Attempts to fetch and parses the forecast data
        :return: weather type string or None on error
        """
        realtime = Config.get(Config.FORECAST_OFFSET_KEY, default_config.FORECAST_OFFSET) == 0
        if realtime:
            response = requests.get("https://api.openweathermap.org/data/2.5/weather?id={0}&mode=json&appid={1}"
                                    .format(Config.get(Config.CITY_ID, default_config.CITY_ID), self.API_KEY))
        else:
            response = requests.get("https://api.openweathermap.org/data/2.5/forecast?id={0}&mode=json&appid={1}"
                                    .format(Config.get(Config.CITY_ID, default_config.CITY_ID), self.API_KEY))
        if response.status_code != 200:
            Logger.get_logger().warn("Failed request to forecast endpoint.")
            Logger.get_logger().debug(response.text)
            return None
        try:
            data = response.json()
            if realtime and type(data.get("list")) is list:
                for forecast_index, forecast in enumerate(data.get("list")):
                    ignore_offset = forecast_index == len(data.get("list")) - 1
                    valid, weather_id = self.parse_weather_id(forecast, ignore_offset)
                    if not valid:
                        continue
                    return weather_id
            elif realtime and type(data) is dict:
                valid, weather_id = self.parse_weather_id(data, True)
                if valid:
                    return weather_id
            else:
                Logger.get_logger().debug("Forecast response missing list array field")
        except ValueError as e:
            Logger.get_logger().exception(e)
            return None
        return None

    @staticmethod
    def parse_weather_id(forecast, ignore_offset):
        """
        Parse a full weather object
        This the root object and should not be confused with the sub weather object.
        :param ignore_offset:
        :param forecast: root weather object (dt, weather, clouds, name, cod, etc in root)
        :return: tuple(bool valid, int weather_Id) The valid bool will be false if the structure is not valid
        or the time
        """
        if type(forecast.get("dt")) is int and type(forecast.get("weather")) is list:
            weather_list = forecast.get("weather")
            if type(weather_list) is list and len(weather_list) > 0:
                datetime = forecast.get("dt")
                offset = Config.get(Config.FORECAST_OFFSET_KEY, default_config.FORECAST_OFFSET)
                current_offset = abs(time.time() - datetime)
                if current_offset >= offset and not ignore_offset:
                    return False, None
                weather = weather_list[0]
                if type(weather) is dict and type(weather.get("id")) is int:
                    return True, weather.get("id")
        return False, None

    @staticmethod
    def handle_weather_code(code):
        """
        Handle a weather code
        :param code: weather code from openweathermap
        :return: None
        """
        Logger.get_logger().debug("Weather code: {0}".format(code))
        # Thunderstorm
        if 200 <= code < 300:
            # No Rain
            if 210 <= code <= 221:
                LightController.set_color(color=Config.get(Config.COLOR_THUNDERSTORM_NO_RAIN,
                                                           default_config.COLOR_THUNDERSTORM_NO_RAIN))
            # Rain
            else:
                LightController.set_color(color=Config.get(Config.COLOR_THUNDERSTORM_RAIN,
                                                           default_config.COLOR_THUNDERSTORM_RAIN))
        # Drizzle
        elif 300 <= code < 400:
            LightController.set_color(color=Config.get(Config.COLOR_DRIZZLE, default_config.COLOR_DRIZZLE))
        # Rain
        elif 500 <= code < 600:
            heavy_rain = [502, 503, 504, 511, 521, 522]
            # Heavy rain
            if code in heavy_rain:
                LightController.set_color(color=Config.get(Config.COLOR_RAIN_HEAVY, default_config.COLOR_RAIN_HEAVY))
            else:
                LightController.set_color(color=Config.get(Config.COLOR_RAIN, default_config.COLOR_RAIN))
        # Snow
        elif 600 <= code < 700:
            LightController.set_color(color=Config.get(Config.COLOR_SNOW, default_config.COLOR_SNOW))
        # Atmosphere
        elif 700 <= code < 800:
            LightController.set_color(color=Config.get(Config.COLOR_ATMOSPHERE, default_config.COLOR_ATMOSPHERE))
        # Clear
        elif code == 800:
            LightController.set_color(color=Config.get(Config.COLOR_CLEAR, default_config.COLOR_CLEAR))
        # Clouds
        elif 801 <= code < 900:
            LightController.set_color(color=Config.get(Config.COLOR_CLOUDS, default_config.COLOR_CLOUDS))
        else:
            Logger.get_logger().warn("Unhandled weather type: {0}".format(code))
