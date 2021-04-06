#!/bin/bash

# Define variables
DIRNAME="`/usr/bin/dirname $0`"
BASENAME="`/usr/bin/basename $0`"
INSTALL_DIR="/opt/discord_stu"
SERVICE_NAME="discord_stu"
SERVICE_USER="root"
SERVICE_FILE="${INSTALL_DIR}/bin/service/discord_stu.service"

# Set the usage information
USAGE="
Usage: ${BASENAME} [OPTION]...

  --install-dir=<directory>          : The installation directory (Default:${INSTALL_DIR})
  --service-name=<service name>      : The service name (Default: ${SERVICE_NAME})
  --service-user=<username>          : The service user (Default: ${SERVICE_USER})
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
    # only root not be personified
    if [ $SERVICE_USER == "root" ]; then
        UNITFILENAME="${SERVICE_NAME}.service"
    else
        UNITFILENAME="${SERVICE_NAME}_${SERVICE_USER}.service"
    fi

    echo "---------------------------------"
    echo "Uninstalling the ${SERVICE_NAME}"
    echo "---------------------------------"

    echo "Stop the service ..."
    /usr/bin/systemctl stop ${UNITFILENAME} >/dev/null 2>&1

    echo "Disable the service ..."
    /usr/bin/systemctl disable ${UNITFILENAME} >/dev/null 2>&1

    echo "Uninstall the systemd unit file ..."
    /usr/bin/rm -f /etc/systemd/system/${UNITFILENAME} >/dev/null 2>&1

    echo "Reload systemd service ..."
    /usr/bin/systemctl daemon-reload >/dev/null 2>&1

    echo "Complete ..."
else
    echo "Could not find $INSTALL_DIR"
    exit 1
fi

exit 0
