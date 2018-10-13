#!/usr/bin/env bash
export DIR=$(dirname $(readlink -f $0))
sudo ${DIR}/camera/install.sh -u
sudo ${DIR}/motor/install.sh -u

