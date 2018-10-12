#!/usr/bin/env python3
#
# PIco UPS module
#

from smbus import SMBus
from RPi import GPIO
from time import sleep
from datetime import datetime
from sys import exit, argv
from os import system, getuid
from signal import signal, SIGTERM

# PIco constants
BYTE, WORD, BUS = 0, 1, 1
POWER = ('', 'RPI', 'BAT')
# PIco i2c addresses
MODE = (0x69, 0x00, BYTE)
BATLEVEL = (0x69, 0x01, WORD)
RPILEVEL = (0x69, 0x03, WORD)
TCELCIUS = (0x69, 0x0C, BYTE)
# PIco GPIO BCM pins
P_IN, P_OUT = 27, 22

i2c_bus = SMBus(BUS)


def now(): return str(datetime.now())


def read_i2c(i2c_addr, offset, read_word):
    if read_word:
        val = i2c_bus.read_word_data(i2c_addr, offset)
    else:
        val = i2c_bus.read_byte_data(i2c_addr, offset)
    return int(hex(val).split('x')[1])


def stats():
    return {
        'power mode': POWER[read_i2c(*MODE)],
        'LiPO battery voltage': read_i2c(*BATLEVEL) / 100.0,
        'RPI voltage': read_i2c(*RPILEVEL) / 100.0,
        'temperature': read_i2c(*TCELCIUS),
        'timestamp': now()
    }


def sigterm_handler(_signo, _stack_frame):
    print('[{0}] cleaning up pins!'.format(now()))
    GPIO.cleanup()
    exit(0)


if __name__ == '__main__':
    signal(SIGTERM, sigterm_handler)
    if len(argv) == 1 or argv[1] in ('stats', 'status'):
        print(stats())
    elif argv[1] == 'start' and getuid() == 0:
        print('[{0}] set up pins!'.format(now()))
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(P_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(P_OUT, GPIO.OUT)
        try:
            while GPIO.input(P_IN):
                GPIO.output(P_OUT, True)
                sleep(0.25)
                GPIO.output(P_OUT, False)
                sleep(0.25)
            print('[{0}] received ups power out, initiating shutdown...'.format(now()))
            system('shutdown -h now')
        except KeyboardInterrupt:
            print('[{0}] received interrupt, exiting...'.format(now()))
        finally:
            print('[{0}] cleaning up pins!'.format(now()))
            GPIO.cleanup()
            exit(0)
