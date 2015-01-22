Plugable PS-BTAPS1 Library and CLI
==================================

Description
___________
This project is a library and command-line interface for communicating with and programming a Plugable PS-BTAPS1 Bluetooth Home Automation Switch.

libbtaps.py 
    Serves as a python implementation of the BTAPS protocol, either to be used directly in your programs, or to be used as a reference in developing your own implementation in a different language.
btaps.py 
    A simple command-line UI that implements all of the features exposed by libbtaps.py

Implemented Functionality
_________________________
The following functions of the Plugable PS-BTAPS1 are currently present in the library:
 - Setting Switch On/Off
 - Reading current status of switch(name, on/off, timer settings)
 - Creating, modifying and deleting timers
 - Changing the device's name
 - Updating the device's date and time to your PC's current date and time.
 
TO DO
_____
The following features are not currently supported:
 - NFControl (Device proximity on/off functionality)
 - Security PIN

OS Support
__________
Due to PyBluez limitations, this library will currently only work on Linux and Windows systems.

Dependencies
____________

 - Python 2.7.x
 - PyBluez aka python-bluez
 
Windows
    Download PyBluez from: https://code.google.com/p/pybluez 
Ubuntu/Debian
    sudo apt-get install python-bluez
Fedora
    sudo yum install pybluez
Arch
    sudo pacman -S python2-pybluez

Installation
____________
Coming soon to a pip repository near you!