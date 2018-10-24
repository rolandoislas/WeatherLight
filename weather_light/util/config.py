import json
import os
from os import path
from os.path import expanduser


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
        except OSError:
            pass
        if text is None:
            return {}
        try:
            config_dict = json.loads(text)
            if type(config_dict) != "dict":
                return {}
        except json.JSONDecodeError:
            return {}
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
