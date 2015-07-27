#! /bin/bash

export CLINER_DIR=$(pwd)

# Install system dependencies
sudo apt-get install python-pip python-virtualenv python-dev g++ gfortran libopenblas-dev liblapack-dev -y

# Install python dependencies, using apt-get
sudo apt-get install python-nose python-numpy python-scipy python-nltk -y

# trying to create the virtual env on the synced folder can lead to errors.
# The virtual env isn't needed here, so an optional flag prevents it.
# Run install script
bash install.sh

