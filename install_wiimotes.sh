#!/bin/bash
[[ $(id -u) == 0 ]] || exit 1
[[ x$1 == 'x-u' ]] && {
  service wiimote stop
  update-rc.d wiimote remove
  rm -rf /usr/local/bin/wiimote.py /usr/local/bin/wiimote /etc/init.d/wiimote /var/log/wiimote
}
[[ x$1 == 'x-i' ]] && {
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
}
