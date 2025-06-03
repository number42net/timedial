<!-- ```
  _____  _                   ____   _         _                      
 |_   _|(_) _ __ ___    ___ |  _ \ (_)  __ _ | |    ___   _ __  __ _ 
   | |  | || '_ ` _ \  / _ \| | | || | / _` || |   / _ \ | '__|/ _` |
   | |  | || | | | | ||  __/| |_| || || (_| || | _| (_) || |  | (_| |
   |_|  |_||_| |_| |_| \___||____/ |_| \__,_||_|(_)\___/ |_|   \__, |
                                                               |___/ 
``` -->
<center><img src="/static/banner.gif" alt="Banner"></center>

**TimeDial.org** is a public [BBS](https://en.wikipedia.org/wiki/Bulletin_board_system)-style system that you can access through a browser (coming soon), SSH, Telnet, or a raw TCP socket.

Whether you're logging in with a modern terminal or a real vintage setup, TimeDial lets you explore a shell environment, play classic games, and even run authentic vintage software on simulated machines like the PDP-11 and VAX.

TimeDial is built with true vintage compatibility in mind. The interface dynamically adapts to both 40- and 80-column displays, meaning it works just as well on a real terminal as on a modern terminal emulator. It's also optimized for slow connections and remains usable even at 1200 baud.

# How to Connect

Connect using any of the following ports with the username `guest` and the password `guest`. The system will guide you through creating a new account. Once that's done, simply log in again using your personal username and password.

- **Web SSH** Connect directly using your browser through our [WebSSH](/webssh/) client 
- **22 - SSH** (recommended; use with [PuTTY](https://www.putty.org/) or similar)
- **23 - Telnet**
- **24 - Raw TCP** (least ideal, but useful for serial-to-TCP bridges or vintage terminals)

In addition, for those seeking an authentic vintage experience, you can even slow down your connection:

- **1223 - Telnet** Emulates a 1200 baud connection
- **2423 - Telnet** Emulates a 2400 baud connection
- **9623 - Telnet** Emulates a 9600 baud connection

**Privacy Note:** While passwords are encrypted on the server, Telnet and raw TCP connections transmit credentials in plain text. Don't store anything important on the server and use a unique password you don't use elsewhere.

# What You'll Find Inside

The platform is still in its early stages, but already offers:

## Classic Simulated Hardware

Run real software on simulated vintage systems. Always wanted to try out BSD UNIX but don't have a PDP-11 lying around? Now's your chance!

Each simulator runs as a private instance, with disk images and configuration files stored in your personal home directory. That means full control - modify your setup, log in from multiple terminals, and pick up right where you left off.

- **Altair 8800** (8800) with BASIC 3.2
- **Altair 8800** (Z80) with CP/M 3.0 and 8 drives full of vintage software
- **Data General Nova** with RDOS 7.5
- **PDP-11/70** with 2.11BSD
- **PDP-11/45** with Version 7 UNIX
- **VAX 8600** with OpenVMS 7.1  
- Want something else? Just ask or build it your self! 

[More information about the simulators](simulators.md)

## Interactive Shells: Bash and C-Shell

Access your own home directory, manage files, create scripts - the power of Unix is at your fingertips.

Currently available shells:

- **Bash**
- **C Shell (csh)**
- More on the way - request your favorite!

## Classic Games

Step into the world of early interactive entertainment with text-based adventures and dungeon crawlers that helped define entire genres.

- **Rogue** - The dungeon crawler that started it all.  
- **Zork (Original Epic)** - The complete, uncut version from the late 1970s.  
- **Zork I: The Great Underground Empire (1980)** - Begin your quest for fame and fortune.  
- **Zork II: The Wizard of Frobozz (1981)** - Face the cunning wizard and descend deeper.  
- **Zork III: The Dungeon Master (1982)** - Confront fate and face your ultimate test.
- **Classic BSD games** - All of the classic games from 2BSD and 4BSD

## Tools

Communicate with others or explore the web - all from the command line.

- **Mail** - Traditional Unix mail client (limited to internal messaging)  
- **Lynx** - A text-based web browser that lets you explore the modern web from a vintage terminal

## Media and demo's

See what your terminal can really do! 

- **ASCII Star Wars** - Watch the original Star Wars in the best possible way
- **VT100 player** - A large collection of VT100 animations, most of which also work on newer terminals
- And many more! 

# Rules

This is a shared space - treat it like your favorite old machine: with curiosity and care!

- Be respectful to others  
- Don't break things that aren't yours

## Source code
All of the source code for TimeDial.org can be found on [GitHub](https://github.com/number42net/timedial)
