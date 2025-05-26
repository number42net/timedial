#!/bin/bash

cd /simh
mkdir tmp
cd tmp

if [ -d /simh_init ]; then
    ln -s /simh_init/211bsd_rpethset.tgz .
    ln -s /simh_init/v3.9-0.tar.gz .
else
    echo "Downloading requirements..."
    wget https://www.retro11.de/data/oc_w11/oskits/211bsd_rpethset.tgz
    wget https://github.com/simh/simh/archive/refs/tags/v3.9-0.tar.gz
fi

# Build simh
tar -xf v3.9-0.tar.gz
cd simh-3.9-0
make pdp11
cp BIN/pdp11 /usr/bin

# Prepare PDP11 BSD 2.11
cd /simh/pdp11-bsd211
tar -xvzf /simh/tmp/211bsd_rpethset.tgz ./211bsd_rpeth.dsk
chmod a+x start

# Run script
chmod a+x /simh/run.sh

# Clean-up
rm -rf /simh/tmp
