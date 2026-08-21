# Overview

A basic falling sand game written in python using pygame that supports local area networked multiplayer. 'fsg.py' is the game script itself, while 'fsgserver.py' is the script to run the server. If connected to the server, a player's actions are repeated across all connected clients, resulting in synchronous gameplay. The game can also be ran without server connectivity.

This software was made primarily to improve my programming and computer networking skills, but also for fun!

![screenshot of the game](https://github.com/jake-u/network-py-fsg/blob/master/readme_assets/fsg1.png?raw=true)

# Network Communication

This uses a client/server model, where the server simply relays updates from each of the clients to all connected clients.

For connecting, the client initiates a connection with the server, and from then on the server relays any updates from other connected clients to the newly connected client.
Each action a connected client causes is in the form of an eight byte block of data. This contains information about what the action was, and how to interpret it.
A client disconnection (unexpected or expected) is easily detected from the server when there is no response from a TCP keep-alive ping. Similarly, a client automatically disconnects from a server failure if it receives no response.

# Installation & Usage
Simply run the script(s) using Python.

The Python modules 'pygame' and 'numpy' are required to run the client.

You will need to configure the 'IP' constant in fsg.py to the ip address of the device that is running the server script in order for it to connect. The fsgserver.py script should be ran before the clients' scripts.

The mouse is used to draw elements into the simulation. These can be selected from the menu at the top.
The mouse wheel is used to change the brush size.
"c" attempts to connect or disconnect from the server.
"r" resets the simulation.
"h" toggles the drawing of most on-screen text
Space pauses/unpauses the simulation. 

# Future Work

* Synchronize world state upon connection
* Better synchronized path drawing
