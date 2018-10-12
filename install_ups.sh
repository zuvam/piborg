#!/bin/bash
if [[ $(id -u) != 0 ]]; then
    sudo $0 $*
elif [[ "$1" == '-u' ]]; then
    service ups stop
    update-rc.d ups remove
    rm -rf /usr/local/bin/ups.py* /usr/local/bin/ups /etc/init.d/ups /var/log/ups
    echo "uninstalled ups"
elif [[ "$1" == '-i' ]]; then
    export DIR=$(dirname $(readlink -f $0))
    cp $DIR/ups.py /usr/local/bin/ups.py
    cp $DIR/ups.sh /etc/init.d/ups
    chmod 755 /usr/local/bin/ups.py /etc/init.d/ups
    mkdir -p /var/log/ups
    chown pi:pi /var/log/ups
    cd /usr/local/bin
    ln -sf ups.py ups
    update-rc.d ups defaults
    service ups start
    echo "installed ups"
    systemctl status ups
else
    echo -e "usage:\n\t sudo $0 -i to install\n\t sudo $0 -u to uninstall"
fi
