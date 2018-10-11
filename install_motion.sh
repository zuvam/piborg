#!/bin/bash
[[ $(id -u) == 0 ]] || exit 1
[[ x$1 == 'x-u' ]] && {
  service motion stop
  update-rc.d motion remove
  rm -rf /usr/local/bin/motion.py* /usr/local/bin/motion /etc/init.d/motion /home/pi/.motion /var/log/motion
}
[[ x$1 == 'x-i' ]] && {
  export DIR=$(dirname $(readlink -f $0))
  openssl rand -base64 512 -o /home/pi/.motion
  cp $DIR/motion.py /usr/local/bin/motion.py
  cp $DIR/motion.sh /etc/init.d/motion
  chmod 755 /usr/local/bin/motion.py /etc/init.d/motion
  mkdir -p /var/log/motion
  chown pi:pi /var/log/motion
  openssl rand -base64 512 >/home/pi/.motion
  cd /usr/local/bin
  ln -s motion.py motion
  python -m compileall motion.py
  chmod 644 motion.pyc
  update-rc.d motion defaults
  service motion start
}
