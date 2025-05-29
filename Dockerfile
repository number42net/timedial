FROM ubuntu:22.04

# Update and install required packages for system
# Generate man pages, locales, etc.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update
RUN rm /etc/dpkg/dpkg.cfg.d/excludes
RUN dpkg -S /usr/share/man/ |sed 's|, |\n|g;s|: [^:]*$||' | DEBIAN_FRONTEND=noninteractive xargs apt-get install --reinstall -y
RUN dpkg --verify --verify-format rpm | awk '$2 ~ /\/usr\/share\/doc/ {print $2}' | sed 's|/[^/]*$||' | sort | uniq | xargs dpkg -S | sed 's|, |\n|g;s|: [^:]*$||' | uniq | DEBIAN_FRONTEND=noninteractive xargs apt-get install --reinstall -y
RUN dpkg --verify --verify-format rpm | awk '$2 ~ /\/usr\/share\/locale/ {print $2}' | sed 's|/[^/]*$||' | sort | uniq | xargs dpkg -S | sed 's|, |\n|g;s|: [^:]*$||' | uniq | DEBIAN_FRONTEND=noninteractive xargs apt-get install --reinstall -y
RUN if  [ "$(dpkg-divert --truename /usr/bin/man)" = "/usr/bin/man.REAL" ]; then rm -f /usr/bin/man; dpkg-divert --quiet --remove --rename /usr/bin/man; fi
RUN apt-get install -y \
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
RUN python3.11 -m pip -q install --upgrade pip

# Install simh
RUN apt-get -qq install -y libpcre3-dev libedit-dev libpng-dev libsdl2-dev libvdeplug-dev libpcap-dev git expect rsync
COPY files/simh /opt/simh
RUN find /opt/simh -name "*.gz" -exec gunzip {} \;

# Install specific games, emulators, etc.
# These are seperate to speed up container creation
COPY files/games /opt/games
RUN find /opt/games -name "*.gz" -exec gunzip {} \;
RUN apt-get install -y frotz
RUN apt-get install -y bsdgames bsdgames-nonfree
# Configure telnet and SSH
COPY files/telnet /etc/xinetd.d/telnet
RUN echo '#!/bin/sh\ncat /etc/issue.net\nexec /usr/sbin/in.telnetd' > /usr/sbin/telnet-login
RUN chmod +x /usr/sbin/telnet-login
COPY files/issue.net /etc
COPY files/sshd_config /etc/
RUN rm /etc/legal
COPY files/sshd_config /etc/ssh

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

# Install Timedial
RUN mkdir /timedial
RUN mkdir /opt/timedial
RUN find /usr/share/terminfo -type f,l | sed 's|.*/||' | sort > /opt/timedial/supported_terminals
COPY pyproject.toml /timedial
COPY timedial /timedial/timedial
RUN cd /timedial; python3.11 -m pip -q install .
COPY files/menu.yaml /opt/timedial

# Start-up
COPY files/startup.sh /usr/sbin
RUN chmod 700 /usr/sbin/startup.sh

EXPOSE 22 23 24
CMD ["/usr/sbin/startup.sh"]
