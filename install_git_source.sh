#!/usr/bin/env bash
# script to easy install / uninstall applications using git on raspberry pi

function create_service_unit(){
    local REPO_NAME=$1
    shift
    local USER=$1
    shift
    local HEADLESS_START=$*

    echo "HEADLESS_START is ${HEADLESS_START}"
    echo "USER is ${USER}"
    echo "REPO_NAME is ${REPO_NAME}"

    {
        echo "[Unit]"
        echo "Description=${REPO_NAME} headless start"
        echo "After=network.target"
        echo ""
        echo "[Service]"
        echo "ExecStart=${HEADLESS_START}"
        echo "WorkingDirectory=/home/pi/clones/${REPO_NAME}"
        echo "StandardOutput=inherit"
        echo "StandardError=inherit"
        echo "Restart=always"
        echo "User=${USER}"
        echo ""
        echo "[Install]"
        echo "WantedBy=multi-user.target"
        echo ""
    } | sudo tee /etc/systemd/system/${REPO_NAME}.service >/dev/null
}

function install(){
    local REPO_URL=$1
    shift
    local HEADLESS_START=$1
    shift
    local USER=$1
    shift
    local DEPENDENCIES_LIST=$*
    local REPO_NAME=$(basename "${REPO_URL%.*}")

    echo "REPO_URL is ${REPO_URL}"
    echo "HEADLESS_START is ${HEADLESS_START}"
    echo "USER is ${USER}"
    echo "DEPENDENCIES_LIST is ${DEPENDENCIES_LIST}"
    echo "REPO_NAME is ${REPO_NAME}"


    [[ -z ${DEPENDENCIES_LIST} ]] || sudo apt-get install -y ${DEPENDENCIES_LIST}

    cd
    mkdir -p clones
    cd clones
    if [[ -d ${REPO_NAME} ]]; then
        echo "going to update git repo ${REPO_NAME}"
        cd ${REPO_NAME}
        git pull
    else
        echo "going to clone git repo ${REPO_URL}"
        git clone ${REPO_URL}
        cd ${REPO_NAME}
    fi
    [[ -z ${HEADLESS_START} ]] || {
        echo create_service_unit ${REPO_NAME} ${USER} "${HEADLESS_START}"
        create_service_unit ${REPO_NAME} ${USER} "${HEADLESS_START}"
        for cmd in enable start status; do
            sudo systemctl ${cmd} ${REPO_NAME}.service
        done
    }
}

function uninstall(){
    local REPO_NAME=$1
    [[ -f /etc/systemd/system/${REPO_NAME}.service ]] && {
        for cmd in stop status disable; do
            sudo systemctl ${cmd} ${REPO_NAME}.service
        done
        sudo rm -f /etc/systemd/system/${REPO_NAME}.service
    }
}

function purge(){
    local REPO_NAME=$1
    shift
    local DEPENDENCIES_LIST=$*
    uninstall ${REPO_NAME}
    [[ -z ${DEPENDENCIES_LIST} ]] || sudo apt-get purge -y ${DEPENDENCIES_LIST}
    cd ~/clones
    rm -rf ${REPO_NAME}
}

function format_sources(){
    for x in $*; do
        echo ${x}
    done | grep -v 'REPO_URL\|HEADLESS_START\|DEPENDENCIES_LIST\|POST_INSTALL\|USER' | sort -u | tr '\n' '|'
}

if [[ $(id -u) -eq 0 ]]; then
    sudo -u pi $0 $*
    exit $?
fi

if [[ $(id -un) != 'pi' ]]; then
    echo 'me like to be pi'
    exit 1
fi

declare -A SOURCES

SOURCES['pistreaming REPO_URL']='https://github.com/waveform80/pistreaming.git'
SOURCES['pistreaming HEADLESS_START']='/usr/bin/python3 server.py'
SOURCES['pistreaming USER']='pi'
SOURCES['pistreaming DEPENDENCIES_LIST']='ffmpeg git python3-picamera python3-ws4py'

SOURCES['diddyborg REPO_URL']='https://github.com/piborg/diddyborg.git'

SOURCES['diddyborg-web REPO_URL']='https://github.com/piborg/diddyborg-web.git'
SOURCES['diddyborg-web HEADLESS_START']='/usr/bin/python2 metalWeb.py'
SOURCES['diddyborg-web USER']='root'

SOURCES['piborg REPO_URL']='https://github.com/zuvam/piborg.git'
SOURCES['piborg POST_INSTALL']='install.sh'

SOURCES['PiModules REPO_URL']='https://github.com/piborg/diddyborg.git'

SOURCES['pi-timolo REPO_URL']='https://github.com/pageauc/pi-timolo.git'

OPTION=$1
shift

if [[ ${OPTION} == '-i' ]]; then
    REPO=${SOURCES["$1 REPO_URL"]}
    if [[ -z ${REPO} ]]; then
        install $*
    else
        install ${REPO} """${SOURCES["$1 HEADLESS_START"]}""" ${SOURCES["$1 USER"]} ${SOURCES["$1 DEPENDENCIES_LIST"]}
        POST_INSTALL=${SOURCES["$1 POST_INSTALL"]}
        [[ -z ${POST_INSTALL} ]] || {
        cd ~/clones/$(basename "${REPO%.*}")
        ./${POST_INSTALL}
        }
    fi
elif [[ ${OPTION} == '-u' ]]; then
    uninstall $1
elif [[ ${OPTION} == '--purge' ]]; then
    purge $1 ${SOURCES["$1 DEPENDENCIES_LIST"]}
else
    echo """Usage:
    Install: git clone/pull repository and setup headless start
        $0 -i [$(format_sources ${!SOURCES[@]})]
        $0 -i REPO_URL 'HEADLESS START CMD' [DEPENDENCIES LIST]
    Uninstall: remove headless start, but leave git repository and any installed dependencies
        $0 -u [$(format_sources ${!SOURCES[@]})]
        $0 -u REPO_NAME
    Purge: remove headless start and remove local git repo and remove installed dependencies
        $0 --purge [$(format_sources ${!SOURCES[@]})]
    """
fi

