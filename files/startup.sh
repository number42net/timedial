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

fixperms # Run the fixperms function
mv /menu.yaml /data/menu.yaml

# Final security steps:
apt-get -qq remove -y gcc 
apt-get -qq remove -y g++ 
apt-get -qq remove -y make
apt-get -qq remove -y curl
apt-get -qq remove -y wget
apt-get -qq remove -y python3-pip
apt-get -qq autoremove -y
chmod 000 /bin/su

# Start services
/sbin/syslogd # Syslog daemon
service ssh start # SSH daemon
service xinetd start # Telnet daemon
socat TCP-LISTEN:24,reuseaddr,fork EXEC:'/sbin/agetty - -l /bin/login' & # Raw connection daemon
timedial_create_user_daemon & # User creation daemon

tail -F /var/log/messages # Show syslog
