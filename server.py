# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 20:16:41 2022

@author: Geetesh
"""
from socket import * #import the socket module
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)# create the udp socket
serverSocket.bind(('', 12000))# udp server socket assignment to specific port number
print("The server is ready to receive")
while True: # program goes to the infinite loop and wait for the data from client
    message, clientAddress = serverSocket.recvfrom(2048)# receive the data from client in the server buffer
    modifiedMessage = message.decode() # decode the data
    serverSocket.sendto(modifiedMessage.encode(), clientAddress) # sever send the data back to the client
