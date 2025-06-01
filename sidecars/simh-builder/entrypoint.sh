#!/bin/bash

bin_dir=/opt/simh/bin
simh_dir=/opt/simh/src

# Clone repo if needed
cd $simh_dir
if [[ ! -d $simh_dir/simh ]]; then
    echo "Cloning repo..."
    git clone -q https://github.com/simh/simh.git
fi
cd simh

if [[ $(git rev-parse HEAD) != $COMMIT ]]; then
    make clean
fi

git checkout $COMMIT
make
cp $(find BIN -maxdepth 1 -type f) $bin_dir

# trap "echo 'Caught SIGTERM, exiting...'; exit 0" TERM INT
# # Infinite wait loop with short sleep
# while true; do
#   sleep 1
# done
