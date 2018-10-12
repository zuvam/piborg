#!/bin/bash
if [[ $(id -u) != 0 ]]; then
    echo -e "usage:\n\t sudo $0 $*"
    exit 1
elif [[ "$1" == '-u' ]]; then
    service motion stop
    update-rc.d motion remove
    rm -rf /usr/local/bin/motion.py* /usr/local/bin/motion /etc/init.d/motion /home/pi/.motion /var/log/motion
    echo "uninstalled motion"
elif [[ "$1" == '-i' ]]; then
    export DIR=$(dirname $(readlink -f $0))
    openssl rand -base64 -out /home/pi/.motion 512
    chown pi:pi /home/pi/.motion
    cp $DIR/motion.py /usr/local/bin/motion.py
    cp $DIR/motion.sh /etc/init.d/motion
    chmod 755 /usr/local/bin/motion.py /etc/init.d/motion
    mkdir -p /var/log/motion
    chown pi:pi /var/log/motion
    cd /usr/local/bin
    ln -sf motion.py motion
    update-rc.d motion defaults
    service motion start
    echo "installed motion"
    systemctl status motion
else
    echo -e "usage:\n\t sudo $0 -i to install\n\t sudo $0 -u to uninstall"
fi
