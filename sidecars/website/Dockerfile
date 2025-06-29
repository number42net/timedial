FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update; apt-get install -y nginx python3-pip libaugeas-dev
RUN pip3 install Markdown jinja2 certbot

RUN mkdir /opt/timedial
RUN mkdir /opt/timedial/html
COPY src /opt/timedial/src
COPY static /opt/timedial/html/static

RUN cd /opt/timedial/src; python3 generate.py
RUN mkdir /var/www/letsencrypt

COPY timedial.conf /etc/nginx/conf.d/

COPY entrypoint.sh /

EXPOSE 80 443
CMD ["/entrypoint.sh"]
