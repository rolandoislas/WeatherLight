import logging


class Logger:
    @classmethod
    def get_logger(cls):
        return logging.getLogger("WeatherLight")

    @classmethod
    def set_level(cls, level):
        logging.basicConfig(level=level)
        cls.get_logger().setLevel(level)
        for handler in cls.get_logger().handlers:
            handler.setLevel(level)
