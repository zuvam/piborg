#!/bin/bash
if [[ $(id -u) != 0 ]]; then
    echo -e "usage:\n\t sudo $0 $*"
    exit 1
elif [[ "$1" == '-u' ]]; then
    service camera stop
    update-rc.d camera remove
    rm -rf /usr/local/bin/camera.py* /usr/local/bin/camera /etc/init.d/camera /var/log/camera
    echo "uninstalled camera"
elif [[ "$1" == '-i' ]]; then
    export DIR=$(dirname $(readlink -f $0))
    cp $DIR/camera.py /usr/local/bin/camera.py
    cp $DIR/camera.sh /etc/init.d/camera
    chmod 755 /usr/local/bin/camera.py /etc/init.d/camera
    mkdir -p /var/log/camera
    chown pi:pi /var/log/camera
    cd /usr/local/bin
    ln -sf camera.py camera
    update-rc.d camera defaults
    service camera start
    echo "installed camera"
    systemctl status camera
else
    echo -e "usage:\n\t sudo $0 -i to install\n\t sudo $0 -u to uninstall"
fi
