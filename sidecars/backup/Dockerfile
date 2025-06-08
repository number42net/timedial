FROM ubuntu:22.04

# Install simh dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update
RUN apt-get -qq install -y rsync openssh-client

RUN mkdir /root/.ssh; chmod 400 /root/.ssh
RUN touch /root/.ssh/sidecars-backup.key
COPY known_hosts /root/.ssh/known_hosts
RUN chmod 500 /root/.ssh; chmod 400 /root/.ssh/*

COPY entrypoint.sh /
RUN chmod 700 entrypoint.sh
CMD ["./entrypoint.sh"]
