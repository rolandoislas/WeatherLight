import json
import os
from os import path
from os.path import expanduser

from util.logger import Logger
from data import default_config


class Config:
    CONFIG_DIR = expanduser("~/.config")
    CONFIG_PATH = path.join(CONFIG_DIR, "weather_light.json")
    FORECAST_OFFSET_KEY = "forecast_offset"
    COLOR_THUNDERSTORM_NO_RAIN = "color_thunderstorm_no_rain"
    COLOR_THUNDERSTORM_RAIN = "color_thunderstorm_rain"
    COLOR_DRIZZLE = "color_drizzle"
    COLOR_RAIN = "color_rain"
    COLOR_RAIN_HEAVY = "color_rain_heavy"
    COLOR_SNOW = "color_snow"
    COLOR_ATMOSPHERE = "color_atmosphere"
    COLOR_CLEAR = "color_clear"
    COLOR_CLOUDS = "color_clouds"
    CITY_ID = "city_id"
    CITY_NAME = "city_name"
    config = None

    @classmethod
    def get(cls, key, default=None):
        if cls.config is None:
            cls.load()
        return cls.config.get(key, default)

    @classmethod
    def set(cls, key, value):
        if cls.config is None:
            cls.load()
        cls.config[key] = value

    @classmethod
    def get_config(cls):
        text = None
        try:
            if not path.exists(cls.CONFIG_DIR):
                os.makedirs(cls.CONFIG_DIR)
            with open(cls.CONFIG_PATH, "r") as config:
                text = config.read()
        except OSError as e:
            Logger.get_logger().exception(e)
        if text is None:
            Logger.get_logger().warn("Empty config file: {0}".format(cls.CONFIG_PATH))
            return cls.create_empty_config()
        try:
            config_dict = json.loads(text)
            if not cls.verify_config(config_dict):
                Logger.get_logger().warn("Config invalid format: {0}".format(cls.CONFIG_PATH))
                return cls.create_empty_config()
        except ValueError as e:
            Logger.get_logger().exception(e)
            return cls.create_empty_config()
        return config_dict

    @classmethod
    def set_config(cls, config_dict):
        if type(config_dict) is not dict:
            return
        config_json = json.dumps(config_dict)
        with open(cls.CONFIG_PATH, "w") as config:
            config.write(config_json)

    @classmethod
    def commit(cls):
        cls.set_config(cls.config)

    @classmethod
    def load(cls):
        cls.config = cls.get_config()

    @classmethod
    def verify_config(cls, config):
        """
        Ensure all the values in the config are populated with the correct type
        :param config: config dict
        :return: True if the config passes verification
        """
        if type(config) is not dict:
            return False
        if type(config.get(cls.FORECAST_OFFSET_KEY, 0)) is not int:
            return False
        if type(config.get(cls.COLOR_THUNDERSTORM_NO_RAIN, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_THUNDERSTORM_NO_RAIN, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_THUNDERSTORM_RAIN, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_THUNDERSTORM_RAIN, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_DRIZZLE, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_DRIZZLE, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_RAIN, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_RAIN, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_RAIN_HEAVY, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_RAIN_HEAVY, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_SNOW, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_SNOW, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_ATMOSPHERE, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_ATMOSPHERE, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_CLEAR, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_CLEAR, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.COLOR_CLOUDS, [0, 0, 0])) is not list or \
                len(config.get(cls.COLOR_CLOUDS, [0, 0, 0])) != 3:
            return False
        if type(config.get(cls.CITY_ID, "")) is not str:
            return False
        if type(config.get(cls.CITY_NAME, "")) is not str:
            return False
        return True

    @classmethod
    def create_empty_config(cls):
        config = {
            cls.FORECAST_OFFSET_KEY: default_config.FORECAST_OFFSET,
            cls.COLOR_THUNDERSTORM_NO_RAIN: default_config.COLOR_THUNDERSTORM_NO_RAIN.value,
            cls.COLOR_THUNDERSTORM_RAIN: default_config.COLOR_THUNDERSTORM_RAIN.value,
            cls.COLOR_DRIZZLE: default_config.COLOR_DRIZZLE.value,
            cls.COLOR_RAIN: default_config.COLOR_RAIN.value,
            cls.COLOR_RAIN_HEAVY: default_config.COLOR_RAIN_HEAVY.value,
            cls.COLOR_SNOW: default_config.COLOR_SNOW.value,
            cls.COLOR_ATMOSPHERE: default_config.COLOR_ATMOSPHERE.value,
            cls.COLOR_CLEAR: default_config.COLOR_CLEAR.value,
            cls.COLOR_CLOUDS: default_config.COLOR_CLOUDS.value,
            cls.CITY_ID: default_config.CITY_ID,
            cls.CITY_NAME: default_config.CITY_NAME
        }
        return config
