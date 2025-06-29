FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update && apt-get install -y dovecot-imapd busybox-syslogd git python3-pip
RUN pip install --upgrade pip
COPY files /
RUN groupadd -g 999 guest
RUN groupadd guestusers
RUN pip install git+https://github.com/number42net/timedial.git

EXPOSE 143 993
CMD ["/usr/local/bin/entrypoint.sh"]
