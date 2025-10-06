#!/bin/bash
 
#set -x
set -e
SHARE_SRC=$1
USERNAME=$2
PASSW=$3
MOUNT_POINT=$4
SUBDIR_SRC=$5
SUBDIR_DEST=$6
 
echo "mounting share..."
# Mount de SMB share (pas aan naar jouw specifieke opties)
mkdir -p $MOUNT_POINT

# Mount alleen als SHARE_SRC niet leeg is
#if [ -n "$SHARE_SRC" ]; then
#  mount -t cifs "$SHARE_SRC" "$MOUNT_POINT" -o username="$USERNAME",password="$PASSW",vers=2.0,uid=1000
#fi


# Export for Python to access
export MOUNT_POINT
export SUBDIR_SRC
export SUBDIR_DEST
 
echo "starting watcher ..."
# Start het Python script
python3 app/main.py 2>&1
 
#set +x