# Whisk 
Whisk is an automatic, lightweight sentence mixer built on Gentle and Pydub, written primarily in Python.
It can be used both as an application and a library (via whisk.py).

## Quick Setup
The setup below has been tested on a fresh install of Ubuntu 20.04.
*I haven't been able to thoroughly test the setup process yet, so this process may not work universally!*
1. Save the Whisk repository to your device using *git clone*:
	* Navigate to the folder where you'd like to build Whisk.
	* Start a terminal window in that folder.
	* If you haven't already, install **git** with the command *sudo apt-get install git*.
	* Run the command *git clone https://github.com/jpmchargue/whisk.git*
1. Open the root directory of the repository (whisk) in a terminal.
1. Run *sudo ./setup.sh*. This will install Gentle and its dependencies.
1. Once that completes, run *python3 launch.py* to launch Whisk.
