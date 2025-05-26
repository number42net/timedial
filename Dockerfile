FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install required packages for system
RUN apt-get update && apt-get install -y \
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
    && apt-get clean

# Install specific games, emulators, etc.
# These are seperate to speed up container creation
RUN apt-get install -y frotz
RUN apt-get install -y simh

# Prevent legal message on first login
RUN rm /etc/legal

# Setup SSH
RUN mkdir /var/run/sshd

# Remove pam_systemd.so to avoid session errors
RUN sed -i '/pam_systemd.so/d' /etc/pam.d/common-session

RUN printf '%s\n' \
  "service telnet" \
  "{" \
  "    disable         = no" \
  "    socket_type     = stream" \
  "    wait            = no" \
  "    user            = root" \
  "    server          = /usr/sbin/telnet-login" \
  "    log_on_success  += USERID" \
  "    log_on_failure  += USERID" \
  "    type            = UNLISTED" \
  "    port            = 23" \
  "}" > /etc/xinetd.d/telnet

RUN echo '#!/bin/sh\ncat /etc/issue.net\nexec /usr/sbin/in.telnetd' > /usr/sbin/telnet-login
RUN chmod +x /usr/sbin/telnet-login

# Limit login attempts
RUN sed -i '1i auth optional pam_faildelay.so delay=30000000' /etc/pam.d/sshd
RUN sed -i '1i auth optional pam_faildelay.so delay=30000000' /etc/pam.d/login

# Copy configuration files
COPY files/pam.d/* /etc/pam.d
COPY files/issue.net /etc
COPY files/sshd_config /etc/ssh
COPY files/menu.yaml /
COPY files/limits.conf /etc/security/limits.conf

# Copy scripts
COPY files/startup.sh /usr/sbin
RUN chmod 700 /usr/sbin/startup.sh
RUN mkdir /timedial
COPY pyproject.toml /timedial
COPY timedial /timedial/timedial
RUN ls -lha
WORKDIR /timedial
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install .

# Create the guest user and set correct permissions
RUN useradd -ms "/usr/local/bin/timedial_create_user" -u 999 guest
RUN echo "guest:guest" | chpasswd guest

# Create guestusers group:
RUN groupadd guestusers

# Expose ports for SSH and Telnet
EXPOSE 22 23 24

# Start-up script
CMD ["/usr/sbin/startup.sh"]
