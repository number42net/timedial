#!/bin/bash
set -e

if [ ! -d "~/$1" ]; then
    cp -R /opt/simh/$1 ~/
fi

cd ~/$1

echo
echo "Now starting your personal $1"
cat ~/$1/login-info.txt
echo "To exit, press CTR+E"
echo
read -n 1 -s -r -p "Press any key to continue..."
echo
./start
