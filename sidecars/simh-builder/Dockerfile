FROM ubuntu:22.04

# Install simh dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update
RUN apt-get -qq install -y build-essential libpcre3-dev libedit-dev libpng-dev libsdl2-dev libvdeplug-dev libpcap-dev git expect rsync libsdl2-ttf-dev curl

# Prepare sim-h 
RUN mkdir /opt/simh

COPY entrypoint.sh /
RUN chmod 700 entrypoint.sh
CMD ["./entrypoint.sh"]
