#!/bin/bash
while true; do
    echo "Starting sync at: $(date)"
    rsync --exclude=".cache" --archive --human-readable --verbose --delete --rsh "ssh -i /root/.ssh/sidecars-backup.key -p 23" /home/ u463815-sub1@u463815.your-storagebox.de:home-backup
    echo "Finished sync at: $(date)"
    sleep 3600
done
