#!/bin/sh
#
# init script for Wiimote Controller PicoBorgRev based motion control server
#

### BEGIN INIT INFO
# Provides:		wiimote
# Required-Start:       motion
# Required-Stop:        motion
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	init script for Wiimote controller for PicoBorgRev based motion control server
# Description:		init script for Wiimote controller for PicoBorgRev based motion control server
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NAME=wiimote
DAEMON=/usr/local/bin/wiimote
DAEMONARGS="start-wii-controller"
DAEMONUSER="pi"
DAEMONMSG="wiimote for motion control server"
STOPSIGNAL=2
PIDFILE=/var/run/$NAME.pid
LOGFILE=/var/log/$NAME/$NAME.log

. /lib/lsb/init-functions

test -f $DAEMON || exit 0

case "$1" in
    start)
        log_daemon_msg "Starting" "$DAEMONMSG"
        start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --chuid $DAEMONUSER --quiet --oknodo \
          --startas /bin/bash -- -c "exec stdbuf -oL -eL $DAEMON $DAEMONARGS >$LOGFILE 2>&1"
        log_end_msg $?
        ;;
    stop)
        log_daemon_msg "Stopping" "$DAEMONMSG"
        start-stop-daemon --stop --signal $STOPSIGNAL --pidfile $PIDFILE --quiet --oknodo  --retry 5
        log_end_msg $?
        start-stop-daemon --status --pidfile $PIDFILE --quiet || rm -f $PIDFILE
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    status)
        log_daemon_msg "Status" "$DAEMONMSG"
        start-stop-daemon --status --pidfile $PIDFILE --quiet
        log_end_msg $?
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 2
        ;;
esac

exit 0
