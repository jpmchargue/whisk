#!/bin/bash

set -e

# Download Gentle
git submodule init
git submodule update

# Install Gentle's missing dependencies.
# There's a few packages which Gentle / Kaldi depend on but don't directly install, so they're installed here.
echo "Installing Gentle dependencies..."
apt-get install libopenblas-dev libopenblas-base python2.7
echo "Gentle dependencies installed."

# Install Whisk dependencies
echo "Installing Whisk dependencies..."
apt-get install python3-tk python3-pip
pip3 install PySimpleGUI pydub pronouncing
echo "Whisk dependencies installed."

# Perform setup for Gentle
echo "Whisk is about to set up Gentle. This will probably take a while."
echo "Press any key to continue..."
read -n 1 -s
cd gentle && ./install.sh #> /dev/null 2>&1
echo "Gentle setup complete!"
