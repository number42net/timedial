#!/bin/bash
/sbin/syslogd  -l 7 # Syslog daemon, no debug messages
/usr/sbin/dovecot # Dovecot
timedial-priv-create-user-daemon --no-home-dir & # User creation daemon

newaliases; postmap /etc/postfix/transport; postfix start # Postfix mail server

tail -F /var/log/messages # Show syslog
