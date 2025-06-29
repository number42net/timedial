#!/bin/bash
/sbin/syslogd # -l 7 # Syslog daemon, no debug messages
timedial-priv-create-user-daemon --no-home-dir & # User creation daemon

/usr/sbin/vsftpd /etc/vsftpd.conf &

tail -F /var/log/messages # Show syslog
