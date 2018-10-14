#!/usr/bin/env python2
# -*- coding: utf-8 -*-
""" Wiimote controller for DiddiBorg """
import cwiid
from os import system
from signal import signal, SIGTERM
from time import sleep

from motor_server import MotorController

WII_LED = 9  # LEDs to light up on connected wii remote
BTNS_DISCONNECT = cwiid.BTN_PLUS + cwiid.BTN_MINUS
BTNS_FWD = cwiid.BTN_UP | cwiid.BTN_1
BTNS_REV = cwiid.BTN_DOWN | cwiid.BTN_2
BTNS_RIGHT = cwiid.BTN_RIGHT | cwiid.BTN_PLUS
BTNS_LEFT = cwiid.BTN_LEFT | cwiid.BTN_MINUS
BTNS_TURN = cwiid.BTN_RIGHT | cwiid.BTN_PLUS | cwiid.BTN_LEFT | cwiid.BTN_MINUS | cwiid.BTN_A
BTNS_STOP = cwiid.BTN_B
BTNS_NO_TURN = cwiid.BTN_HOME | cwiid.BTN_A
BTNS_SHUTDOWN = cwiid.BTN_1 + cwiid.BTN_2 + cwiid.BTN_A + cwiid.BTN_B


def rumble(wii, n):
    wii.rumble = 1
    sleep(n)
    wii.rumble = 0


if __name__ == '__main__':
    restart = running = True


    def sigterm(*args, **kwargs):
        global running
        global restart
        running = restart = False


    signal(SIGTERM, sigterm)

    wii = None
    linear = angular = 0

    while restart:
        running = True
        while wii is None and restart:
            try:
                wii = cwiid.Wiimote()
            except RuntimeError as e:
                sleep(1)
            except KeyboardInterrupt:
                running = restart = False
        if wii is not None:
            wii.rpt_mode = cwiid.RPT_BTN
            wii.led = WII_LED
            rumble(wii, 0.2)
            try:
                with MotorController() as mc:
                    while running:
                        try:
                            buttons = wii.state['buttons']
                            if buttons - BTNS_SHUTDOWN == 0:
                                running = restart = False
                                system('/usr/bin/sudo shutdown -h now')
                            if buttons - BTNS_DISCONNECT == 0:
                                running = False
                            if (buttons & BTNS_STOP):
                                linear = 0
                            if (buttons & BTNS_NO_TURN):
                                angular = 0
                            if (buttons & BTNS_FWD):
                                linear += 1 if linear < 100 else 0
                            if (buttons & BTNS_REV):
                                linear -= 1 if linear > -100 else 0
                            if (buttons & BTNS_RIGHT):
                                angular += 1 if angular < 100 else 0
                            if (buttons & BTNS_LEFT):
                                angular -= 1 if angular > -100 else 0
                            if angular != 0 and not (buttons & BTNS_TURN):
                                angular -= abs(angular) / angular
                            if buttons != 0 or angular != 0:
                                print(wii.state)
                                print(mc.set_velocity(linear / 100.0, angular / 100.0))
                            sleep(0.01)
                        except KeyboardInterrupt:
                            running = restart = False
                    mc.set_velocity(0.0, 0.0)
                    rumble(wii, 0.2)
                    wii = None
            except IOError:
                pass
            except KeyboardInterrupt:
                running = restart = False
