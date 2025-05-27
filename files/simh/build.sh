#!/bin/bash

data_dir=/data/simh-bin
simh_dir=/opt/simh
expected_file=$simh_dir/expected-emulators

buildsimh() {
    cd $simh_dir
    echo "Building simh $1..."
    if [[ ! -d $simh_dir/git ]]; then
        echo "Cloning repo..."
        git clone -q https://github.com/simh/simh.git git
    fi
    cd git
    make -j$(nproc) $1
    cp BIN/$1 $data_dir
}

if [[ ! -d $data_dir ]]; then
    mkdir $data_dir
fi

while read -r emulator; do
  echo "Processing $emulator..."
  if [[ ! -x "$data_dir/$emulator" ]]; then
    buildsimh $emulator
  fi
  cp $data_dir/$emulator /usr/bin/ 
done < "$expected_file"
