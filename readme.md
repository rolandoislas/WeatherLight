# WeatherLight

A weather forecast RGB LED controller

# Dependencies

- python3
- [CHIP IO][1]
- [requests][2]

# Running

## Usage

```
usage: weather_light.py [-h] [-p] [-log LOG] [-i]

WeatherLight

optional arguments:
  -h, --help       show this help message and exit
  -p, --pwm-debug  Enable PWM debug output
  -log LOG         Log level: FATAL CRITICAL ERROR WARN INFO DEBUG
  -i, --inverted   Invert the PWN output
```

Note on the inverted flag: 

The default PWM duty cycle will be from 0 to 100 percent
 for off and on states. The inverted flag will invert the duty cycle 
 and will be 100 to 0 percent for off and on.
 
This is useful for switching between common anode and common cathode
 RGB LEDs.

During operation the pins "XIO-P2" (red), "XIO-P3" (green), "XIO-P4" (blue)
 on a [C.H.I.P microcomputer][3] will output a pulse modulated signal.

[1]: https://github.com/xtacocorex/CHIP_IO
[2]: https://github.com/requests/requests
[3]: https://en.wikipedia.org/wiki/CHIP_(computer)
