#!/bin/bash

# Remove existing users
while IFS=: read -r username _ uid _ _ _ home shell; do
  # Skip system accounts and non-user shells
  if [ "$uid" -ge 1000 ] && [ "$username" != "nobody" ]; then
    userdel "$username" 2>/dev/null
    if [ $? -eq 0 ]; then
      echo "User $username deleted successfully."
    else
      echo "Failed to delete $username or user is currently logged in."
    fi
  fi  
done < /etc/passwd


# Copy game data, diskimages, etc.
echo "Copying disk images and game data..."
bash /opt/simh/build.sh
mv /menu.yaml $DATA_DIR/menu.yaml
rsync -a --no-perms $SYNC_DIR/simh $SYNC_DIR/games /opt/

# Enforce permissions and remove unwanted packages
chmod -R go-w /opt/
chown root:guest $DATA_DIR
chmod 0751 $DATA_DIR
chmod 0500 $DATA_DIR/ssh_host_keys
chmod 0400 $DATA_DIR/ssh_host_keys/*
chown -R root:guest $DATA_DIR/guests
chmod 0771 $DATA_DIR/guests
chmod 0640 $DATA_DIR/guests/*
chmod 0711 /home
chmod 0700 /mnt
if [ "$TARGETARCH" = "amd64" ]; then \
      apt-get -qq remove -y gcc g++ make curl wget python3-pip git; apt-get -qq autoremove -y; \
fi

# Start services
/sbin/syslogd # Syslog daemon
service ssh start # SSH daemon
service xinetd start # Telnet daemon
socat TCP-LISTEN:24,reuseaddr,fork EXEC:/bin/login,pty,setsid,stderr,raw,echo=0,sane & # Raw connection daemon
timedial_create_user_daemon & # User creation daemon

tail -F /var/log/messages # Show syslog
