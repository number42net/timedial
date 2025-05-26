#!/bin/bash
fixperms() {
    echo "Fixing permissions..."
    chown root:guest /data
    chmod 0751 /data
    chmod 0500 /data/ssh_host_keys
    chmod 0400 /data/ssh_host_keys/*
    chown -R root:guest /data/guests
    chmod 0771 /data/guests
    chmod 0640 /data/guests/*
    chmod 0711 /home
}

# Init process
if [ -d /init ]; then
    echo "Starting init process..."
    cp -R /init/* /data
    fixperms
    echo
    echo "Finished init, remove /init bind mount and restart"
    exit
fi

# Remove existing users
while IFS=: read -r username _ uid _ _ _ home shell; do
  # Skip system accounts and non-user shells
  if [ "$uid" -ge 1000 ] && [ "$username" != "nobody" ]; then
    userdel -r "$username" 2>/dev/null
    if [ $? -eq 0 ]; then
      echo "User $username deleted successfully."
    else
      echo "Failed to delete $username or user is currently logged in."
    fi
  fi
done < /etc/passwd

fixperms # Run the fixperms function
mv /menu.yaml /data/menu.yaml

# Start services
/sbin/syslogd # Syslog daemon
service ssh start # SSH daemon
service xinetd start # Telnet daemon
socat TCP-LISTEN:24,reuseaddr,fork EXEC:/bin/login,pty,setsid,stderr,raw,echo=0,sane & # Raw connection daemon
timedial_create_user_daemon & # User creation daemon

tail -F /var/log/messages # Show syslog
