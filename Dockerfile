FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install required packages
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
    && apt-get clean

# # Set authorized_keys for root
# RUN mkdir /root/.ssh
# RUN chmod 700 /root/.ssh
# COPY root_authorized_keys /root/.ssh/authorized_keys
# RUN chmod 600 /root/.ssh/authorized_keys

# Prevent legal message on first login
RUN rm /etc/legal

# Setup SSH
RUN mkdir /var/run/sshd

# Remove pam_systemd.so to avoid session errors
RUN sed -i '/pam_systemd.so/d' /etc/pam.d/common-session

# Setup Telnet using xinetd, including banner
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

# Copy configuration module
COPY pam.d/* /etc/pam.d

# Copy scripts
RUN mkdir /timedial
COPY pyproject.toml /timedial
COPY timedial /timedial/timedial
RUN ls -lha
WORKDIR /timedial
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install .

# Create the guest user and set correct permissions
RUN useradd -ms "/usr/local/bin/timedial_create_user" -u 999 guest
RUN echo "guest:guest" | chpasswd

# Expose ports for SSH and Telnet
EXPOSE 22 23

# Start-up script
CMD ["/usr/bin/bash",  "-c", "/sbin/syslogd; \
service ssh start; \
service xinetd start; \
timedial_create_user_daemon & \
tail -F /var/log/messages"]
