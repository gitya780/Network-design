# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from socket import *
serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM) #define the socket with IP4 and UDP
message = input("send the data:")# get the data from the user
clientSocket.sendto(message.encode(),(serverName, serverPort)) #nessage is sending to the server ,IP address and port number variable
modifiedMessage, serverAddress = clientSocket.recvfrom(2048) # receiving the data from the server in the buffer
print(modifiedMessage.decode())# print data received from server
clientSocket.close()
