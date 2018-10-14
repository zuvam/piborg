#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

from os import chmod, getuid, path, remove, system

unit_template = """[Unit]
Description={unit_name} headless start
After=network.target

[Service]
ExecStart={exec_start} {exec_args}
WorkingDirectory={working_dir}
StandardOutput=journal
StandardError=journal
Restart=always
User={user}

[Install]
WantedBy=multi-user.target"""


def setup_service_unit(executable_file: str, exec_args: str = '', user: str = 'pi') -> None:
    executable_file = path.abspath(executable_file)
    unit_name = path.splitext(path.basename(executable_file))[0]
    working_dir = path.dirname(executable_file)
    unit_file = '/etc/systemd/system/{}.service'.format(unit_name)
    chmod(executable_file, 0O755)
    with open(unit_file, 'w') as outfile:
        outfile.write(unit_template.format(exec_start=executable_file, exec_args=exec_args, unit_name=unit_name,
                                           working_dir=working_dir, user=user))
    for cmd in ('enable', 'start', 'status'):
        system('/bin/systemctl {} {}'.format(cmd, unit_name))


def tear_down_service_unit(executable_file: str) -> None:
    unit_name = path.splitext(path.basename(executable_file))[0]
    for cmd in ('stop', 'status', 'disable'):
        system('/bin/systemctl {} {}'.format(cmd, unit_name))
    remove('/etc/systemd/system/{}.service'.format(unit_name))


if __name__ == '__main__':
    from sys import argv

    if getuid() != 0:
        exit(system('/usr/bin/sudo {}'.format(' '.join(argv))))

    usage = """Usage:
    {cmd} -h                            -> print usage
    {cmd} -e [executable] [user] [args] -> enable headless start `executable args`
    {cmd} -e                            -> enable headless start using defaults (motion_server, wiimote, camera)
    {cmd} -d [unit_name]                -> disable headless start for unit_name and clean up log folder
    {cmd} -d                            -> disable headless start using defaults (motion_server, wiimote, camera)
    
    """.format(cmd=argv[0])

    if len(argv) == 2:  # use defaults for targets
        targets = (
            {'executable_file': 'motor_server.py', 'exec_args': 'start headless', },
            {'executable_file': 'wiimote.py', 'exec_args': 'start-wii-controller headless'},
            {'executable_file': 'camera.py', 'user': 'root', 'exec_args': 'headless', },
        )
    else:  # use command line arguments for targets
        targets = (
            {
                'executable_file': argv[2] if len(argv) > 2 else None,
                'user': argv[3] if len(argv) > 3 else 'pi',
                'exec_args': ' '.join(argv[4:]) if len(argv) > 4 else '',
            },
        )

    if len(argv) == 1 or argv[1] == '-h':
        print(usage)
    elif argv[1] == '-e':
        for target in targets:
            setup_service_unit(**target)
    elif argv[1] == '-d':
        for target in targets:
            tear_down_service_unit(executable_file=target['executable_file'])
    else:
        print(usage)
