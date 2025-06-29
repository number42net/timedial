#!/bin/bash
/sbin/syslogd  -l 7 # Syslog daemon, no debug messages
/usr/sbin/dovecot # Dovecot
timedial-priv-create-user-daemon --no-home-dir & # User creation daemon

filename="/var/log/archive/imap-$(date '+%Y-%m-%d_%H-%M-%S').log"
touch $filename
ln -sf $filename /var/log/messages

newaliases; postmap /etc/postfix/transport; postfix start # Postfix mail server

tail -F /var/log/messages # Show syslog
