FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update && apt-get install -y postfix dovecot-imapd busybox-syslogd git python3-pip
RUN pip install --upgrade pip
RUN pip install git+https://github.com/number42net/timedial.git

COPY files /
RUN groupadd -g 999 guest
RUN groupadd guestusers

EXPOSE 143 993
CMD ["/usr/local/bin/entrypoint.sh"]
