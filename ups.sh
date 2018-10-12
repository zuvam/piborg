#!/bin/sh
#
# init script for PIco UPS
#

### BEGIN INIT INFO
# Provides:		ups
# Required-Start:
# Required-Stop:
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	init script for the PIco UPS
# Description:		PIco UPS module
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NAME=ups
DAEMON=/usr/local/bin/ups
DAEMONARGS="start"
DAEMONUSER="root"
STOPSIGNAL=2
PIDFILE=/var/run/$NAME.pid
LOGFILE=/var/log/$NAME/$NAME.log

. /lib/lsb/init-functions

test -f $DAEMON || exit 0

case "$1" in
    start)
        log_daemon_msg "Syncing PIco HW emulated clock" "PIco clock "
        echo ds1307 0x68 >/sys/class/i2c-adapter/i2c-1/new_device
        hwclock -s
        log_end_msg $?
        log_daemon_msg "Starting PIco UPS monitor" "PIco UPS "
        start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --chuid $DAEMONUSER --quiet --oknodo \
          --startas /bin/bash -- -c "exec stdbuf -oL -eL $DAEMON $DAEMONARGS >$LOGFILE 2>&1"
        log_end_msg $?
        ;;
    stop)
        log_daemon_msg "Stopping PIco UPS monitor" "PIco UPS "
        start-stop-daemon --stop --signal $STOPSIGNAL --pidfile $PIDFILE --quiet --oknodo --retry 5
        log_end_msg $?
        start-stop-daemon --status --pidfile $PIDFILE --quiet || rm -f $PIDFILE
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    status)
        log_daemon_msg "Status PIco UPS monitor" "PIco UPS "
        start-stop-daemon --status --pidfile $PIDFILE --quiet
        log_end_msg $?
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 2
        ;;
esac

exit 0
