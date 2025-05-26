#!/bin/bash
set -e

if [ ! -d "~/$1" ]; then
    cp -R /simh/$1 ~/
fi

cd ~/$1

echo
echo "Now starting simh: $1"
echo "To exit, press CTR+E"
echo
read -n 1 -s -r -p "Press any key to continue..."
echo
./start
