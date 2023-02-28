import tkinter as tk
from tkinter import ttk
from tkinter import *
import time
from PIL import Image, ImageTk
import numpy as np
import socket
import math
import io 
import random

# The IP ADDRESS of localhost is 127.0.0.1
UDP_SERVER_IP_ADDRESS = "127.0.0.1"

# Randomly chose this port from the available list found on https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
UDP_PORT_NUMBER = 2000
UDP_PORT_NUMBERreturn = 2001

# createsocket for server and bind to IP_ADDRESS & PORT_NUMBER
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBER))
print("The server is ready to receive:")

message, client_addr = serverSocket.recvfrom(1030)
msg = message.decode()
num_of_pkts = int(msg)

returnsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

receive = []  # empty list for where packets will be recieved
duplicate_finder = []
corruptornot_randomvalue = -1
dropornot_randomvalue = -1

i = 0
data = ""
_start_time = time.perf_counter() # return the float value of time seconds and start the counter
while True:
    # receive message from client, then decode to print in server side
    message, client_addr = serverSocket.recvfrom(1030)
    newdata = message[0:27] # first take the information of the data and checksum from the client
    datalist = [] #
    duplicate = 0
    data = ""
    # decode the data part by part then put in the list 
    for j in range(len(newdata)):
        if str(chr(int(newdata[j]))) != "-": 
            data += str(chr(int(newdata[j])))
        if str(chr(int(newdata[j]))) == "-":
            if len(data) > 0:
                datalist.append(data)
                data = ""

    message = message[28:]

    # Rebuilding Checksum on receiving end to make sure data is correct
    ack = 0
    pos = 0
    tick = 0
    tick1 = 0
    tick2 = 0
    tick3 = 0

    for j in message:
        if pos % 4 == 0:
            tick += j
        if pos % 4 == 1:
            tick1 += j
        if pos % 4 == 2:
            tick2 += j
        if pos % 4 == 3:
            tick3 += j
        pos += 1

    tick = tick / len(message) * 4
    tick = str(int(tick))
    tick1 = tick1 / len(message) * 4
    tick1 = str(int(tick1))
    tick2 = tick2 / len(message) * 4
    tick2 = str(int(tick2))
    tick3 = tick3 / len(message) * 4
    tick3 = str(int(tick3))
    # compare the checksum which recieve from the client
    if datalist[2] != tick: 
        ack += 0
    else:
        ack += 1

    if datalist[3] != tick1:
        ack += 0
    else:
        ack += 1

    if datalist[4] != tick2:
        ack += 0
    else:
        ack += 1

    if datalist[5] != tick3:
        ack += 0
    else:
        ack += 1

    ack = ack / 4
    ackint = ack # every ack is 1 make the overall ack 1

    for k in duplicate_finder: # check the duplicate that we receive the packet earlier
        if (str(k) == datalist[1]):
            print("Received Duplicate")
            duplicate = 1

    corruptornot = random.randint(0, 100)
    dropornot = random.randint(0, 100)

    # If the checksum is valid then append to the image. And send the packetnumber received back to the sender.
    if ackint == 1 and duplicate == 0:
            # corrupting the packets
        if corruptornot <= corruptornot_randomvalue:
            print("Sending back bad ack packet")
            pkt_send_back = str(-500) # send back bad ack 
            pkt_send_back = pkt_send_back.encode()
            returnsock.sendto(pkt_send_back, (UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBERreturn))
        elif dropornot <= dropornot_randomvalue:
            print("Not sending the packet at all")
        else:
            i = i + 1
            duplicate_finder.append(int(datalist[1])) # save the packet number in duplicate finder , so I means we get the packet successfully
            receive.append(message)
            print("Sending back good ack packet", datalist[1])
            pkt_send_back = datalist[1] # send the packet number
            pkt_send_back = pkt_send_back.encode()
            returnsock.sendto(pkt_send_back, (UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBERreturn))
    else: # ack= 0 or dulicate = 1
        if corruptornot <= corruptornot_randomvalue:
            print("Sending back bad ack packet")
            pkt_send_back = str(-500)
            pkt_send_back = pkt_send_back.encode()
            returnsock.sendto(pkt_send_back, (UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBERreturn))
        else:
            print("Bad Data, send back the previous good packet received")
            pkt_send_back = str(i - 1) # send back the number of the good packet received previously
            pkt_send_back = pkt_send_back.encode()
            returnsock.sendto(pkt_send_back, (UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBERreturn))

    if (i == num_of_pkts):
        break

image = receive[0]
for i in range(1, num_of_pkts):
    image = image + receive[i]

_end_time = time.perf_counter()
print("total time = ", _end_time - _start_time)

# Take the image and convert to a byte stream, to save as a seperate file
save_image = Image.open(io.BytesIO(image))

# Save the sent image in the same directory named DecodedImage.bmp
save_image.save("DecodedImage.bmp")

# Technically we do not need OpenCV anymore
#########################################################################################
### Deprecated the code below as the image is being saved as a seperate file ############
#########################################################################################
#image = np.asarray(bytearray(image), dtype="uint8")
#image = cv2.imdecode(image, cv2.IMREAD_COLOR)
#cv2.imshow('img_decode',image)
#cv2.waitKey()
#########################################################################################