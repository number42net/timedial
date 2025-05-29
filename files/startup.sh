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

# Build simh
bash /opt/simh/build.sh

# Allow w and who
touch /var/run/utmp

# Prepare logfile
filename="/var/log/archive/messages-$(date '+%Y-%m-%d_%H-%M-%S').log"
touch $filename
ln -sf $filename /var/log/messages

# Enforce permissions and remove unwanted packages
chown -R root:root /var/log/*
chmod -R ug=rw,ug+X,o= /var/log/*
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
/sbin/syslogd  -l 7 # Syslog daemon, no debug messages
service ssh start # SSH daemon
service xinetd start # Telnet daemon
# socat TCP-LISTEN:24,reuseaddr,fork EXEC:/bin/login,pty,setsid,stderr,raw,echo=0,sane & # Raw connection daemon
socat TCP-LISTEN:24,reuseaddr,fork EXEC:"script -q -c /bin/login /dev/null",pty,setsid,stderr,raw,echo=0,sane &
timedial_create_user_daemon & # User creation daemon

tail -F /var/log/messages # Show syslog
