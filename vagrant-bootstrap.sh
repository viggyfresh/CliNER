#! /bin/bash

export CLINER_DIR="/vagrant"

# Update repositories before attempting to download
sudo apt-get update

# Install system dependencies
sudo apt-get install python-pip python-virtualenv python-dev g++ gfortran libopenblas-dev liblapack-dev -y

# Install python dependencies, using apt-get
sudo apt-get install python-nose python-numpy python-scipy python-nltk -y

# trying to create the virtual env on the synced folder can lead to errors.
# The virtual env isn't needed here, so VIRTUAL_ENV prevents it.
export VIRTUAL_ENV="true"

# Run install script
cd $CLINER_DIR && sudo -E bash install.sh

# install nltk requirements
python -m nltk.downloader maxent_treebank_pos_tagger punkt 

echo export CLINER_DIR="$CLINER_DIR" >> /home/vagrant/.bashrc
