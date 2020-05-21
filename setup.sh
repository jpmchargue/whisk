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

# Perform setup for Gentle
echo "Setting up Gentle. This will probably take a while."
cd gentle && ./install.sh #> /dev/null 2>&1
echo "Gentle setup complete!"

# Install Whisk dependencies
echo "Installing Whisk dependencies..."
pip3 install python3-tk pysimplegui pydub pronouncing
echo "Whisk dependencies installed."
