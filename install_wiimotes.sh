#!/bin/bash
if [[ $(id -u) != 0 ]]; then
    echo -e "usage:\n\t sudo $0 $*"
    exit 1
elif [[ "$1" == '-u' ]]; then
    service wiimote stop
    update-rc.d wiimote remove
    rm -rf /usr/local/bin/wiimote.py /usr/local/bin/wiimote /etc/init.d/wiimote /var/log/wiimote
    echo "uninstalled wiimote"
elif [[ "$1" == '-i' ]]; then
    apt-get -y install python-cwiid
    export DIR=$(dirname $(readlink -f $0))
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
else
    echo -e "usage:\n\t sudo $0 -i to install\n\t sudo $0 -u to uninstall"
fi

