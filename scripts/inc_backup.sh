#!/bin/bash

#/usr/local/bin/inc_backup.sh

API_TOKEN="XXXX"
CHAT_ID=XXXX
API_URL="https://api.telegram.org/bot${API_TOKEN}/sendMessage"

error(){
        echo "ERROR" >> $LOG
        exit 1
}

DATE=$(date +%Y-%m-%d)
SOURCE1="/media/storage/public/fotos"
SOURCE2="/media/storage/ramiro"
LOG="/tmp/LOG${DATE}"

echo "------------------------------------" >> $LOG
echo "STARTING $DATE INCREMENTAL BACKUP" >> $LOG
echo "Stopping SMB service..." >> $LOG
systemctl stop smbd || error

echo "Mounting HDD..." >> $LOG
mount -t xfs /dev/disk/by-uuid/2415d5bb-9e93-41b8-8443-a3b8496df63a /mnt/HDD_BACKUP || error

BACKUP_DIR="/mnt/HDD_BACKUP"
LAST_BACKUP=$(ls -1tr $BACKUP_DIR | tail -n 1)
DEST="${BACKUP_DIR}/${LAST_BACKUP}"

echo "Copying files..." >> $LOG

echo "$SOURCE1 -> $DEST" >> $LOG
rsync -av --delete $SOURCE1 $DEST >> $LOG || error

echo "$SOURCE2 -> $DEST" >> $LOG
rsync -av --delete $SOURCE2 $DEST >> $LOG || error

sleep 30s
echo "Unmounting HDD..." >> $LOG 
umount /mnt/HDD_BACKUP || error

echo "Shutting down HDD" >> $LOG
#shutdown HDD, 1m sleep just to make sure all the cached data is written to disk
sync
sleep 1m
hdparm -Y /dev/disk/by-uuid/2415d5bb-9e93-41b8-8443-a3b8496df63a || error

echo "Starting SMB service..." >> $LOG
systemctl start smbd || error

echo "FINISHED $DATE INCREMENTAL BACKUP" >> $LOG

curl -s -X POST $API_URL -d chat_id=$CHAT_ID -d text="$(cat "${LOG}")"

cat $LOG >> /var/log/BACKUP_LOG

rm $LOG
