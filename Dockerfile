FROM ubuntu:22.04

# Update and install required packages for system
# Generate man pages, locales, etc.
ENV DEBIAN_FRONTEND=noninteractive
RUN rm /etc/dpkg/dpkg.cfg.d/excludes
RUN apt-get -qq update && dpkg -S /usr/share/man/ |sed 's|, |\n|g;s|: [^:]*$||' | xargs apt-get install --reinstall -y
RUN apt-get -qq update && dpkg --verify --verify-format rpm | awk '$2 ~ /\/usr\/share\/doc/ {print $2}' | sed 's|/[^/]*$||' | sort | uniq | xargs dpkg -S | sed 's|, |\n|g;s|: [^:]*$||' | uniq | xargs apt-get install --reinstall -y
RUN apt-get -qq update && dpkg --verify --verify-format rpm | awk '$2 ~ /\/usr\/share\/locale/ {print $2}' | sed 's|/[^/]*$||' | sort | uniq | xargs dpkg -S | sed 's|, |\n|g;s|: [^:]*$||' | uniq | xargs apt-get install --reinstall -y
RUN if  [ "$(dpkg-divert --truename /usr/bin/man)" = "/usr/bin/man.REAL" ]; then rm -f /usr/bin/man; dpkg-divert --quiet --remove --rename /usr/bin/man; fi
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
    postfix \
    mailutils \
    man \
    lynx \ 
    && apt-get clean
RUN python3.11 -m pip -q install --upgrade pip

# Install simh dependencies
RUN apt-get -qq update && apt-get -qq install -y libpcre3-dev libedit-dev libpng-dev libsdl2-dev libvdeplug-dev libpcap-dev git expect rsync libsdl2-ttf-dev curl

# Install games
RUN apt-get -qq update && apt-get install -y frotz
RUN apt-get -qq update && apt-get install -y bsdgames bsdgames-nonfree

# Remove legal message on first login
RUN rm /etc/legal

# Configure PAM and other security
RUN sed -i '1i auth optional pam_faildelay.so delay=30000000' /etc/pam.d/login
RUN sed -i '/pam_systemd.so/d' /etc/pam.d/common-session

# Create users and groups
# user guest is to create new accounts, guestusers group is for actual users
RUN groupadd -g 999 guest
RUN useradd -ms "/usr/local/bin/timedial-auth-create-user" -u 999 -g guest guest
RUN echo "guest:guest" | chpasswd guest
RUN groupadd guestusers

# Copy all files
RUN touch /var/run/utmp # Allow w and who
COPY files/ /

# Install Timedial
RUN find /usr/share/terminfo -type f,l | sed 's|.*/||' | sort > /opt/timedial/supported_terminals
RUN mkdir /opt/timedial/src
COPY pyproject.toml /opt/timedial/src
COPY timedial /opt/timedial/src/timedial
RUN cd /opt/timedial/src; python3.11 -m pip -q install .

# Set permissions
RUN chmod +x /usr/local/bin/*
RUN chown root:guest /usr/local/bin/timedial-auth*
RUN chmod 0554 /usr/local/bin/timedial-auth*

# Start-up
EXPOSE 22 23 24
CMD ["/usr/local/bin/container-start.sh"]
