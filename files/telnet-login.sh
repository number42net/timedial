#!/bin/sh
awk '{printf "%s\r\n", $0}' /etc/issue.net
exec /usr/sbin/in.telnetd
