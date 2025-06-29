FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update && apt-get install -y vsftpd busybox-syslogd git python3-pip
RUN pip install --upgrade pip
RUN pip install git+https://github.com/number42net/timedial.git

COPY files /
RUN mkdir -p /var/run/vsftpd/empty
RUN echo "/usr/sbin/nologin" >> /etc/shells
RUN groupadd -g 999 guest
RUN groupadd guestusers

EXPOSE 21 990 40000-40100
CMD ["/usr/local/bin/entrypoint.sh"]
