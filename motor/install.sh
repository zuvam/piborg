#!/bin/bash
if [[ $(id -u) != 0 ]]; then
    sudo $0 $*
elif [[ "$1" == '-u' ]]; then
    service motor_server stop
    update-rc.d motor_server remove
    rm -rf /usr/local/bin/motor_server.py* /usr/local/bin/motor_server /etc/init.d/motor_server /home/pi/.motor_server /var/log/motor_server
    echo "uninstalled motor_server"

    service wiimote stop
    update-rc.d wiimote remove
    rm -rf /usr/local/bin/wiimote.py /usr/local/bin/wiimote /etc/init.d/wiimote /var/log/wiimote
    echo "uninstalled wiimote"
elif [[ "$1" == '-i' ]]; then
    export DIR=$(dirname $(readlink -f $0))
    openssl rand -base64 -out /home/pi/.motor_server 512
    chown pi:pi /home/pi/.motor_server
    cp $DIR/motor_server.py /usr/local/bin/motor_server.py
    cp $DIR/motor_server.sh /etc/init.d/motor_server
    chmod 755 /usr/local/bin/motor_server.py /etc/init.d/motor_server
    mkdir -p /var/log/motor_server
    chown pi:pi /var/log/motor_server
    cd /usr/local/bin
    ln -sf motor_server.py motor_server
    update-rc.d motor_server defaults
    service motor_server start
    echo "installed motor_server"

    apt-get -y install python-cwiid
    cp $DIR/wiimote.py /usr/local/bin/wiimote.py
    cp $DIR/wiimote.sh /etc/init.d/wiimote
    chmod 755 /usr/local/bin/wiimote.py /etc/init.d/wiimote
    mkdir -p /var/log/wiimote
    chown pi:pi /var/log/wiimote
    cd /usr/local/bin
    ln -sf wiimote.py wiimote
    update-rc.d wiimote defaults
    service wiimote start
    echo "installed wiimote"

    systemctl status wiimote
    systemctl status motor_server
else
    echo -e "usage:\n\t sudo $0 -i to install\n\t sudo $0 -u to uninstall"
fi
