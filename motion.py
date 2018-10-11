#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Motion controller module for DiddyBorg"""
from multiprocessing.connection import Listener, Client, AuthenticationError
from os import getpid
from signal import signal, SIGTERM
from smbus import SMBus
from threading import Thread, Event, active_count

I2CBUS, I2CADDRESS = 1, 0x44  # i2cbus number and address of the PiBorgReverse (PBR) board
HEARTBEAT, TIMEOUT = 0.2, 20  # Time interval to send heartbeat to PBR and silence interval before switching off motors
PWM_MAX = int(255.0 * 12.0 / 18.0)  # Max value of PWM to scale down 18 V input to max 12 V
I2C_MAX_LEN = 4  # Max length of PBR response
I2C_ID_PICOBORG_REV = 0x15  # PBR identifer value
SET_LED = 1  # Set the LED status
GET_LED = 2  # Get the LED status
SET_A_FWD = 4  # Set motor 2 PWM rate in a forwards direction
SET_A_REV = 3  # Set motor 2 PWM rate in a reverse direction
GET_A = 5  # Get motor 2 direction and PWM rate
SET_B_FWD = 6  # Set motor 1 PWM rate in a forwards direction
SET_B_REV = 7  # Set motor 1 PWM rate in a reverse direction
GET_B = 8  # Get motor 1 direction and PWM rate
RESET_EPO = 10  # Resets the EPO flag, use after EPO has been tripped and switch is now clear
SET_FAILSAFE = 17  # Set the failsafe flag, turns the motors off if communication is interrupted
GET_FAILSAFE = 18  # Get the failsafe flag
GET_ID = 0x99  # Get the board identifier
A_DIR = (0, -1, 1)
B_DIR = (0, 1, -1)

IP, PORT = '127.0.0.1', 1092  # Default address on which to listen for drive commands
AUTH_KEY_FILE = '/home/pi/.motion'  # Default authkey for the connection
with open(AUTH_KEY_FILE, 'r') as auth_file: TOKEN = auth_file.read().replace('\n', '')

i2c_bus = SMBus(I2CBUS)  # i2c bus used


def is_norm_one(n):
    """return True if n is a number between -1.0 and 1.0"""
    return -1.0 <= n <= 1.0


def norm_pwm(duty_factor):
    """return int duty_factor bounded within ± Maximum Pulse Width Modulatin"""
    return int(min(max(duty_factor, -PWM_MAX), PWM_MAX))


def read_i2c(offset):
    """read block of data at address given by 'offset' from PicoBorgRev module"""
    return i2c_bus.read_i2c_block_data(I2CADDRESS, offset, I2C_MAX_LEN)


def write_i2c(offset, byteVal):
    """write byte given by 'byteVal' to PicoBorgRev module at address given by 'offset'"""
    try:
        i2c_bus.write_byte_data(I2CADDRESS, offset, byteVal)
    except:
        return False
    else:
        return True


class MotionControlServer():
    """Motion Control Server for DiddyBorg
    Example:
    from motion import MotionControlServer
    mcs = MotionControlServer()
    mcs.start()
    """

    def __init__(self, ip_address=IP, ip_port=PORT, token=TOKEN):
        """Initialize Motion Control Server
        :param ip_address: IP address (localhost or external IP address), default is 127.0.0.1
        :param ip_port: port number, default is 1092
        :param token: authkey, default is read from /home/pi/.motion
        :return: MotionControlServer
        """
        self.__ip, self.__port, self.__token = ip_address, ip_port, token
        self.__cmds = (SET_A_FWD, 0), (SET_B_FWD, 0), (SET_LED, 0)
        self.__run = Event()
        self.__updated = Event()
        self.__timeout = Event()
        self.__funcs = dict([(f[25:], getattr(self, f)) for f in dir(self) if f[0:25] == '_MotionControlServer__x__'])
        self.__pid = getpid()
        signal(SIGTERM, self.__sigterm__)

    def start(self):
        """start the Motion Control Server
        Start three threads:
            heartbeat - communicates with the PicoBorgRev
            watchdog - stops the motors if inactive for timeout
            listener - listen for connections (daemon) and starts new daemon thread to handle client requests
                       Connections authkey authenticated by token
        Wait for heartbeat and watchdog to finish
        """
        self.__run.set()
        self.__updated.set()
        self.__timeout.set()
        heartbeat = Thread(target=self.__heartbeat__)
        watchdog = Thread(target=self.__watchdog__)
        listener = Thread(target=self.__listen__)
        listener.daemon = True
        watchdog.start()
        heartbeat.start()
        listener.start()
        heartbeat.join()
        watchdog.join()

    def __heartbeat__(self):
        """Send motor PWM and LED state to the PicoBorgRev module when updated, otherwise every HEARTBEAT interval"""
        while read_i2c(GET_FAILSAFE) == 0: write_i2c(SET_FAILSAFE, 1)
        while self.__run.is_set():
            if self.__updated.wait(HEARTBEAT): self.__updated.clear()
            for cmd in self.__cmds: write_i2c(*cmd)
        write_i2c(SET_FAILSAFE, 0)
        write_i2c(RESET_EPO, 0)
        write_i2c(SET_A_FWD, 0)
        write_i2c(SET_B_FWD, 0)
        write_i2c(SET_LED, 0)

    def __watchdog__(self):
        """Set motor PWM and LED State to 0 (off) if no interaction for more than TIMEOUT interval"""
        while self.__run.is_set():
            if self.__timeout.wait(TIMEOUT):
                self.__timeout.clear()
            else:
                self.__cmds = (SET_A_FWD, 0), (SET_B_FWD, 0), (SET_LED, 0)

    def __listen__(self):
        """Start listening for connections and assign handler thread for new connections"""
        server = Listener((self.__ip, self.__port), authkey=self.__token)
        while self.__run.is_set():
            try:
                connect = server.accept()
                thread = Thread(target=self.__handle__, args=(connect,))
                thread.daemon = True
                thread.start()
            except AuthenticationError:
                pass
        server.close()

    def __handle__(self, conn):
        """accept commands via connection (conn), handle and respond; recieve verb aka function to execute, arguments and named arguments; send result object or exception"""
        inuse = True
        while inuse:
            try:
                verb, args, kwargs = conn.recv()
            except:
                conn.send(Exception('bad request'))
            self.__timeout.set()
            if verb in ('bye', 'close', 'exit'):
                inuse = False
            else:
                try:
                    conn.send(self.__funcs[verb](*args, **kwargs))
                except Exception as e:
                    conn.send(e)
        conn.close()

    def __sigterm__(self, signum, frame):
        """handler function for sigterm"""
        self.__x__stop()

    def __x__stop(self):
        """send stop event to all active threads, returns pid and number of active threads"""
        self.__run.clear()
        self.__timeout.set()
        self.__updated.set()
        return ('pid', self.__pid), ('threads', active_count())

    def __x__status(self):
        """return motor direction and PWM setting, LED state, pid, and number of active threads"""
        return self.__x__get_velocity() + self.__x__get_led() + (('pid', self.__pid), ('threads', active_count()))

    def __x__get_velocity(self):
        """return motor direction and PWM setting"""
        a, b = read_i2c(GET_A), read_i2c(GET_B)
        return ('motorA', A_DIR[a[1]] * a[2]), ('motorB', B_DIR[b[1]] * b[2])

    def __x__set_velocity(self, linear, angular=0.0):
        """set linear velocity and angular velocity, accept values between -1.0 and 1.0, default angular is 0.0"""
        assert is_norm_one(linear) and is_norm_one(angular)
        pwm_r, pwm_l = norm_pwm(PWM_MAX * (linear + angular)), norm_pwm(PWM_MAX * (linear - angular))
        self.__cmds = (SET_A_REV, -pwm_r) if pwm_r < 0 else (SET_A_FWD, pwm_r), (SET_B_REV, -pwm_l) if pwm_l < 0 else (
            SET_B_FWD, pwm_l)
        self.__updated.set()
        return ('linear', linear), ('angular', angular), ('motorA', pwm_r), ('motorB', pwm_l)

    def __x__get_led(self):
        """return LED state"""
        return ('led', 'ON' if read_i2c(GET_LED)[1] == 1 else 'OFF'),

    def __x__set_led(self, on_off_num):
        """set LED state, accept any number 0 -> OFF and non-zero number -> ON"""
        on_off = 1 if on_off_num else 0
        self.__cmds += (SET_LED, on_off),
        self.__updated.set()
        return ('led', 'ON' if on_off == 1 else 'OFF'),

    def __x__get_id(self):
        """return board identifier"""
        return ('id', read_i2c(GET_ID)),

    def __x__get_pid(self):
        """return pid"""
        return ('id', self.__pid),

    def __x__help(self):
        """return docstrings of available functions"""
        return tuple((n + '(' + ', '.join(f.__code__.co_varnames[1:f.__code__.co_argcount]) + ')', f.__doc__)
                     for (n, f) in sorted(self.__funcs.items(), key=lambda x: x[1].__code__.co_firstlineno))


class MotionController(object):
    """Client for Motion Control Server for DiddyBorg
    Example:
    from motion import MotionController
    try:
        list_steps = [(1.0,0),(-1.0,0),(0,1.0),(0,-1.0),(0,0)] # forward, reverse, spin clockwise, spin counter, stop
        with MotionController() as mc:
            mc.set_led(1)
            for linear, angular in list_steps:
                mc.set_velocity(linear, angular)
                time.sleep(1)
            mc.set_led(0)
    Except Exception as e:
        print(e.msg)

    Example:
    from motion import MotionController
    remote_host='192.168.1.1'
    token='shared authToken'
    try:
        with MotionController(remote_host, 1092, token) as mc:
            print(mc.help())
            mc.set_velocity(0.0,0.0)
    Except Exception as e:
        print(e.msg)
    """

    def __init__(self, ip_address=IP, ip_port=PORT, token=TOKEN):
        """connect to Motion Control Server at ip_address:ip_port using AuthKey token
        :param ip_address: IP address (localhost or external IP address), default is 127.0.0.1
        :param ip_port: port number, default is 1092
        :param token: authkey, default is read from /home/pi/.motion
        :return: MotionController
        """
        try:
            self.connection = Client((ip_address, ip_port), authkey=token)
        except AuthenticationError as e:
            e.msg = 'failed to authenticate, check the token used by the client is the same as that used by the server ... default token is saved at /home/pi/.motion'
            raise
        except IOError as e:
            e.msg = 'failed to connect to the server, default server is 127.0.0.1:1092'
            raise

    def __enter__(self):
        """definition of __enter__ for use by context mangaer"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """definition of __exit__ for use by context manager"""
        return self.close()

    def close(self):
        """close connection with Motion Control Server and return False"""
        try:
            self.connection.send(('bye', None, None))
            self.connection.close()
        except:
            pass
        finally:
            return False

    def __getattr__(self, item):
        """custom attribute getter
        attribute(args) = RPC(args)
        RPC: send attribute and arguments to Motion Control Server over connection and return recieved object or raise recieved exception 
        """

        def attribute(*args, **kwargs):
            self.connection.send((item, args, kwargs))
            val = self.connection.recv()
            if isinstance(val, Exception): raise val
            return val

        return attribute


if __name__ == '__main__':
    __doc__ = """Command line interface for Motion Control Server
    Usage:
    motion                        -> display CLI usage
    motion help|h|-h              -> display CLI and library usage
    motion start|s|-s             -> start the Motion Control Server (to be used within a start-up script), by default listens on 127.0.0.1:1092
    motion cmd [nums]             -> RPC execute cmd(*nums) on Motion Control Server and print returned object """
    from sys import argv

    if len(argv) == 1:
        print(__doc__)
    elif argv[1] in ('h', '-h', 'help'):
        print(__doc__)
        print("Available cmd's:")
        try:
            with MotionController() as m:
                for item in m.help(): print('    {0:<30s}-> {1}'.format(*item))
        except Exception as e:
            print(e.msg)
        print('\nLibrary usage:')
        print(MotionControlServer.__doc__)
        print(MotionController.__doc__)
    elif argv[1] in ('s', '-s', 'start'):
        MotionControlServer().start()
    else:
        try:
            with MotionController() as m:
                print(getattr(m, argv[1])(*[float(i) for i in argv[2:]]))
        except Exception as e:
            print(e.msg)
