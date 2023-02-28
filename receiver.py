# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 09:03:18 2022

@author: Geetesh
"""

import tkinter as tk
from tkinter import ttk
from tkinter import *
import time
import cv2
from PIL import Image, ImageTk
import numpy as np
import socket

#The IP ADDRESS of localhost is 127.0.0.1
UDP_SERVER_IP_ADDRESS = "127.0.0.1"

#Randomly chose this port from the available list found on https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
UDP_PORT_NUMBER = 2000

#createsocket for server and bind to IP_ADDRESS & PORT_NUMBER
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBER))
print("The server is ready to receive:")

message, client_addr = serverSocket.recvfrom(1024)
msg = message.decode()
num_of_pkts = int(msg)

receive = []
i = 0

while True:
    #receive message from client, then decode to print in server side
    message, client_addr = serverSocket.recvfrom(1024)
    receive.append(message)
    i = i + 1

    if (i == num_of_pkts):
        break

image = receive[0]

for i in range(1, num_of_pkts):
    image = image + receive[i]

image = np.asarray(bytearray(image), dtype="uint8")
image = cv2.imdecode(image, cv2.IMREAD_COLOR)
cv2.imshow('img_decode',image)
cv2.waitKey()