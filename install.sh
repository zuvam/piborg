#!/usr/bin/env bash
export DIR=$(dirname $(readlink -f $0))
sudo ${DIR}/motor/install.sh -i
sudo ${DIR}/camera/install.sh -i

