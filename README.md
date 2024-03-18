# Overview

A basic falling sand game written with pygame that supports networked multiplayer. 'fsg.py' is the game itself, while 'fsgserver.py' is the script to run the server. You will need to configure the 'IP' constant in fsg.py to the ip address of the device that is running the server script in order for it to connect. The game can be ran without the server.

I wrote this software to get a better understanding on computer networking.

[Software Demo Video](http://youtube.link.goes.here)

# Network Communication

This uses a client/server model, where the server simply relays updates from each of the clients to all connected clients.

This uses TCP, and the server's port defaults to 40999. For clients, the ports numbers are dynamically assigned depending on what python's socket library does.

For connecting, the socket library handles the TCP protocol, so what that looks like is unknown to me. 
For playing, each action a connected client causes takes the form of a seven byte block of data. This contains information about what the action was, and how to interpret it.
A disconnection is easily detected from the server when there is no response.

# Development Environment

Visual Studio Code

Various Python libraries

pygame and numpy are required

# Useful Websites

* [struct - Python documentation](https://docs.python.org/3/library/struct.html)
* [pygame documentation](https://www.pygame.org/docs/)

# Future Work

* Have simulations synchronize world state
* Add ability to clear screen
