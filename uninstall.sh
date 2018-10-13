#!/usr/bin/env bash
export DIR=$(dirname $(readlink -f $0))
sudo ${DIR}/camera/install.sh.sh -u
sudo ${DIR}/wiimotes/install.sh -u
sudo ${DIR}/motor_server/install.sh -u

