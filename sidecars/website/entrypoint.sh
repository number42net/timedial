#!/bin/sh

trap "echo 'Caught SIGTERM, exiting...'; exit 0" TERM INT

if [[ -f /etc/letsencrypt/live/timedial.org/fullchain.pem ]]; then
    certbot renew
else
    certbot certonly --non-interactive --standalone --email toor@timedia.org --agree-tos --no-eff-email -d timedial.org
fi

nginx -g "daemon off;"

while true; do sleep 3600; done
