FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update

RUN apt-get install -y nginx python3-pip

RUN mkdir /opt/timedial
RUN mkdir /opt/timedial/html
COPY src /opt/timedial/src
RUN pip3 install Markdown jinja2

RUN cd /opt/timedial/src; python3 generate.py

COPY timedial.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
