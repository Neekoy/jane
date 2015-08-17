#!/usr/bin/python3

import socket
import sys

domain = sys.argv[1]

class colours:
    yellow = '\033[1;93m'
    red = '\033[1;91m'
    endc = '\033[0m'
    blue = '\033[1;96m'

ip = socket.gethostbyname(domain)
host = socket.getfqdn(ip)

print()
print (colours.yellow + "Server IP: " + colours.endc + ip)
print (colours.yellow + "Hostname: " + colours.endc + host)
