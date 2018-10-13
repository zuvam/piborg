#!/usr/bin/env bash
export DIR=$(dirname $(readlink -f $0))
sudo ${DIR}/motor_server/install.sh -i
sudo ${DIR}/wiimotes/install.sh -i
sudo ${DIR}/camera/install.sh.sh -i

