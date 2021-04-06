#!/bin/bash

# Define variables
DIRNAME="`/usr/bin/dirname $0`"
BASENAME="`/usr/bin/basename $0`"
INSTALL_DIR="/opt/discord_stu"
BINARY="${INSTALL_DIR}/discord_stu/discord_stu.py"
PID_FILE="${INSTALL_DIR}/var/pid/discord_stu.pid"
SERVICE_NAME="discord_stu"
SERVICE_USER="root"
SERVICE_FILE="${INSTALL_DIR}/bin/service/discord_stu.service"

# Set the usage information
USAGE="
Usage: ${BASENAME} [OPTION]...

  --install-dir=<directory>          : The installation directory (Default:${INSTALL_DIR})
  --service-name=<service name>      : The service name (default: ${SERVICE_NAME})
  --service-user=<username>          : The service user (Default: ${SERVICE_USER})
  --pif-file=<pid file>              : The pid file (Default: ${PID_FILE})
"

# Parse command line options
for i in "$@"
do
    case $i in
        --help)
          echo "${USAGE}"
          exit 0
          ;;
        --install-dir=*)
          INSTALL_DIR="${i#*=}"
          shift
          ;;
        --service-name=*)
          SERVICE_NAME="${i#*=}"
          shift
          ;;
        --service-user=*)
          SERVICE_USER="${i#*=}"
          shift
          ;;
        --pid-file=*)
          PID_FILE="${i#*=}"
          shift
          ;;
        *)
          echo "Unknown option (${i})"
          exit 1
          ;;
    esac
done

# If the installation directory is present
if [ -d "$INSTALL_DIR" ]; then
    # Check if the caller is root
    if [[ $EUID -ne 0 ]]; then
       echo "This script must be run as root"
       exit 1
    fi

    # This allows for multiple installations one per user
    # only root is not personified
    if [ $SERVICE_USER == "root" ]; then
        UNITFILENAME="${SERVICE_NAME}.service"
        SERVICE_NAME="${SERVICE_NAME}"
    else
        UNITFILENAME="${SERVICE_NAME}_${SERVICE_USER}.service"
        SERVICE_NAME="${SERVICE_NAME}_${SERVICE_USER}"
    fi

    # check if an installation is already in place
    if [ -f /etc/systemd/system/${UNITFILENAME} ]; then
        echo "An installation of the ${SERVICE_NAME} already exists"
        exit 1
    else
        echo "---------------------------------"
        echo "Installing the ${SERVICE_NAME}"
        echo "---------------------------------"

        echo "Install the systemd unit file ..."
        /usr/bin/cp ${SERVICE_FILE} /etc/systemd/system/${UNITFILENAME} >/dev/null 2>&1
        /usr/bin/sed -i 's|<SERVICE_NAME>|'"${SERVICE_NAME}"'|g' /etc/systemd/system/${UNITFILENAME}
        /usr/bin/sed -i 's|<BINARY>|'"${BINARY}"'|g' /etc/systemd/system/${UNITFILENAME}
        /usr/bin/sed -i 's|<CONFIG_NAME>|'"${CONFIG_NAME}"'|g' /etc/systemd/system/${UNITFILENAME}
        /usr/bin/sed -i 's|<CONFIG_FILE>|'"${CONFIG_FILE}"'|g' /etc/systemd/system/${UNITFILENAME}
        /usr/bin/sed -i 's|<SERVICE_STOP_POST>|'"${SERVICE_STOP_POST}"'|g' /etc/systemd/system/${UNITFILENAME}
        /usr/bin/sed -i 's|<PID_FILE>|'"${PID_FILE}"'|g' /etc/systemd/system/${UNITFILENAME}

        echo "Reload systemd service ..."
        /usr/bin/systemctl daemon-reload >/dev/null 2>&1

        echo "Enable the service ..."
        /usr/bin/systemctl enable ${UNITFILENAME} >/dev/null 2>&1

        echo "Start the service ..."
        /usr/bin/systemctl start ${UNITFILENAME} >/dev/null 2>&1

        echo "Status of the service ..."
        echo ""

        /usr/bin/systemctl status ${UNITFILENAME}
        echo ""

        echo "Complete ..."
    fi
else
    echo "Installation directory not present ($INSTALL_DIR)"
    exit 1
fi

exit 0
