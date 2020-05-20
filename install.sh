#!/bin/bash

set -e

git submodule init
git submodule update

# Install Gentle's missing dependencies.
# There's a few packages which Gentle / Kaldi depend on but don't directly install, so they're installed here.
echo "Installing Gentle dependencies..."
apt-get install libopenblas-dev libopenblas-base python2.7
echo "Gentle dependencies installed."

echo "Setting up Gentle. This will probably take a while."
cd gentle && ./install.sh #> /dev/null 2>&1

