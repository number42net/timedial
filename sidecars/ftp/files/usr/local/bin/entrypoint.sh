#!/bin/bash
/sbin/syslogd # -l 7 # Syslog daemon, no debug messages
timedial-priv-create-user-daemon --no-home-dir & # User creation daemon

filename="/var/log/archive/ftp-$(date '+%Y-%m-%d_%H-%M-%S').log"
touch $filename
ln -sf $filename /var/log/messages

/usr/sbin/vsftpd /etc/vsftpd.conf &

tail -F /var/log/messages # Show syslog
