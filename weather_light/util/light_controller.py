import CHIP_IO.SOFTPWM as SPWM

from data.color import Color

from util.logger import Logger


class LightController:
    RED = "XIO-P2"
    GREEN = "XIO-P3"
    BLUE = "XIO-P4"
    pwn_debug = False  # type: bool
    inverted = False  # type: bool

    def __init__(self):
        pass

    @classmethod
    def start_light(cls):
        """
        Initialize the light
        :return: None
        """
        if cls.pwn_debug:
            SPWM.toggle_debug()
        cls.reset_spwm()
        frequency = 100
        polarity = 0 if cls.inverted else 1
        SPWM.start(cls.RED, 0, frequency=frequency, polarity=polarity)
        SPWM.start(cls.GREEN, 0, frequency=frequency, polarity=polarity)
        SPWM.start(cls.BLUE, 0, frequency=frequency, polarity=polarity)
        cls.set_color(color=Color.BLACK)

    @classmethod
    def reset_spwm(cls):
        """
        Stop all pins and cleanup
        :return: None
        """
        SPWM.stop(cls.RED)
        SPWM.stop(cls.GREEN)
        SPWM.stop(cls.BLUE)
        SPWM.cleanup(cls.RED)
        SPWM.cleanup(cls.GREEN)
        SPWM.cleanup(cls.BLUE)

    @classmethod
    def enable_debug(cls, pwm_debug):
        """
        Should the debug output be enabled for the PWM library
        :param pwm_debug: enabled
        :return: None
        """
        cls.pwn_debug = pwm_debug

    @classmethod
    def set_color(cls, r=255, g=255, b=255, color=None):
        """
        Set the RGB light color. Parameters should be between 0 (off) and 255 (full on).
        :param r: red
        :param g: green
        :param b: blue
        :param color: array of rgb
        :return: None
        """
        if color is not None:
            if type(color) is Color:
                color_val = color.value
            elif type(color) is list and len(color) == 3:
                color_val = color
            else:
                color_val = [255, 255, 255]
            r = color_val[0]
            g = color_val[1]
            b = color_val[2]
        Logger.get_logger().debug("Setting color RGB: {0} {1} {2}".format(r, g, b))
        mod = -255 if cls.inverted else 0
        SPWM.set_duty_cycle(cls.RED, abs((r % 256) + mod) / 255.0 * 100.0)
        SPWM.set_duty_cycle(cls.GREEN, abs((g % 256) + mod) / 255.0 * 100.0)
        SPWM.set_duty_cycle(cls.BLUE, abs((b % 256) + mod) / 255.0 * 100.0)

    @classmethod
    def set_inverted(cls, inverted):
        """
        Set if the output PWM should be inverted
        :param inverted: output PWM
        :return: None
        """
        cls.inverted = inverted
