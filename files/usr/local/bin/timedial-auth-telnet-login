#!/bin/sh
# VT-100 terminals require both newline and carriage return! 
awk '{printf "%s\r\n", $0}' /etc/issue.net
exec /usr/sbin/in.telnetd
