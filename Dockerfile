FROM ubuntu:22.04

# Update and install required packages for system
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update && apt-get install -y \
    openssh-server \
    xinetd \
    telnetd \
    net-tools \
    iputils-ping \
    busybox-syslogd \
    locales \
    python3.11 \
    python3-pip \
    socat \
    vim \
    && apt-get clean

# Install simh
RUN apt-get -qq install -y libpcre3-dev libedit-dev libpng-dev libsdl2-dev libvdeplug-dev libpcap-dev git expect rsync
COPY /files/simh /opt/simh

# Install specific games, emulators, etc.
# These are seperate to speed up container creation
RUN apt-get install -y frotz

# Install Timedial
RUN mkdir /timedial
COPY pyproject.toml /timedial
COPY timedial /timedial/timedial
RUN ls -lha
RUN cd /timedial; python3.11 -m pip -q install --upgrade pip && python3.11 -m pip -q install .
COPY files/menu.yaml /

# Configure telnet and SSH
COPY files/telnet /etc/xinetd.d/telnet
RUN echo '#!/bin/sh\ncat /etc/issue.net\nexec /usr/sbin/in.telnetd' > /usr/sbin/telnet-login
RUN chmod +x /usr/sbin/telnet-login
COPY files/issue.net /etc
COPY files/sshd_config /etc/
RUN rm /etc/legal
COPY files/sshd_config /etc/ssh
# RUN mkdir /var/run/sshd

# Configure PAM and other security
RUN sed -i '1i auth optional pam_faildelay.so delay=30000000' /etc/pam.d/login
RUN sed -i '/pam_systemd.so/d' /etc/pam.d/common-session
COPY files/pam.d/* /etc/pam.d
COPY files/limits.conf /etc/security/limits.conf

# Create users and groups
# user guest is to create new accounts, guestusers group is for actual users
RUN useradd -ms "/usr/local/bin/timedial_create_user" -u 999 guest
RUN echo "guest:guest" | chpasswd guest
RUN groupadd guestusers

# Start-up
COPY files/startup.sh /usr/sbin
RUN chmod 700 /usr/sbin/startup.sh

EXPOSE 22 23 24
CMD ["/usr/sbin/startup.sh"]
