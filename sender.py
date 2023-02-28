import tkinter as tk  # import the module for GUI
from tkinter import ttk  # ttk  import for more advance theme widget in GUI
from tkinter import * 
import time
from PIL import Image, ImageTk  # loading python imaging library
import numpy as np
import socket
import math 
import random

randomvalue = -1

# The IP ADDRESS of localhost is 127.0.0.1
UDP_SERVER_IP_ADDRESS = "127.0.0.1"

# Randomly chose this port from the available list found on https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
UDP_PORT_NUMBER = 2000
UDP_PORT_NUMBERreturn = 2001

returnsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
returnsock.bind((UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBERreturn)) # bind to receiver socket and listening fron the receiver

# create socket for client
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

root = tk.Tk()
root.title('Image Transfer GUI')  # title of gui
root.iconbitmap('')
root.geometry("600x400")  # size of the gui box

# configuration of the gui box
Imagenametxt = Label(root, text="Image Name", font=('Calibri 15'))
Imagenametxt.pack()
textname = tk.Text(root, width=20, height=1)
textname.insert(END, "")
textname.pack()

# if progress button click start labeling
label = Label(root, text="", font=('Calibri 15'))
label.pack()
progresstick = 0

send_d = []  # empty list

emptypacket = ""

for i in range(0, 1000):
    emptypacket += str(random.randint(0, 9)) #generates a random number between a range and convert the random integer to the string
emptypacket = str.encode(emptypacket) # default encoding to utf-8

def step(): # function
    global progresstick
    global displayimage

    input_textname = textname.get(1.0, "end-1c")  # collecting image file name from textbox

    file = open(input_textname, 'rb')  # open the image in binary format for reading
    input_im = file.read()

    packet_amount = math.floor(len(input_im) / 1000)  # number of packets and round the numbers to the nearest integer

    # Creating the packets of data, each packet has 1000 bytes.
    for i in range(packet_amount):
        bytes_s = input_im[i * 1000:(i + 1) * 1000]
        send_d.append(bytes_s)  # adding a single item to the existing list

    # Creating final packet to send to server (this packet is always less than 1000 bytes)
    if (len(input_im) % 1000 != 0):
        bytes_s = input_im[len(send_d) * 1000:len(input_im)]
        send_d.append(bytes_s)
        packet_amount = packet_amount + 1

    msg = str(packet_amount)
    transmit = clientSocket.sendto(msg.encode(), (UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBER))  # sending data to server

    # GUI interface conditions
    if progresstick >= 100:
        label.config(text="Already Sent")
        root.update_idletasks()
    else:
        label.config(text="Sending")
        root.update_idletasks()
            # bulding checksum logic
        for i in range(len(send_d)): # set the range limit of for statement by length of the list
            progresstick += 100 / len(send_d)

            tick = 0
            tick1 = 0
            tick2 = 0
            tick3 = 0
            pos = 0

            for j in send_d[i]:
                if pos % 4 == 0:
                    tick += j
                if pos % 4 == 1:
                    tick1 += j
                if pos % 4 == 2:
                    tick2 += j
                if pos % 4 == 3:
                    tick3 += j
                pos += 1

            tick = tick / len(send_d[i]) * 4
            tick = str(int(tick))
            tick = str.encode(tick)
            tick1 = tick1 / len(send_d[i]) * 4
            tick1 = str(int(tick1))
            tick1 = str.encode(tick1)
            tick2 = tick2 / len(send_d[i]) * 4
            tick2 = str(int(tick2))
            tick2 = str.encode(tick2)
            tick3 = tick3 / len(send_d[i]) * 4
            tick3 = str(int(tick3))
            tick3 = str.encode(tick3)

            pcktnumber = i + 1 # define the packet number of packets for send in the header
            pcktnumber = str(pcktnumber)
            pcktnumber = str.encode(pcktnumber)

            numberofpkt = len(send_d) # get the length of the packet to send in the header
            numberofpkt = str(numberofpkt)
            numberofpkt = str.encode(numberofpkt)
            # sperate the data by "-" in the header which help easy to read on other side 
            while (len(tick) < 5):
                tick += str.encode("-")
            while (len(tick1) < 5):
                tick1 += str.encode("-")
            while (len(tick2) < 5):
                tick2 += str.encode("-")
            while (len(tick3) < 5):
                tick3 += str.encode("-")
            while (len(pcktnumber) < 4):
                pcktnumber += str.encode("-")
            while (len(numberofpkt) < 4):
                numberofpkt += str.encode("-")

            returned = -1

            # This checks if the value of returned matches the packet number,
            # if it does not then that means the packet number was corrupted in
            # transmission or bad data at client-side was received.

            while returned != (i + 1):
                try:
                    dropornot = random.randint(0, 100)
                    if dropornot <= randomvalue:
                        transmit = clientSocket.sendto(numberofpkt + pcktnumber + tick + tick1 + tick2 + tick3 + emptypacket,(UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBER))  # sending data to server
                    else:
                        transmit = clientSocket.sendto(numberofpkt + pcktnumber + tick + tick1 + tick2 + tick3 + send_d[i],(UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBER))  # sending data to server

                    returnsock.settimeout(.25) # set the timeout
                    data, addr = returnsock.recvfrom(1024)  # buffer size of data
                    returned = data.decode('utf8')
                    returned = int(returned) # we assign ack value come from the reciever

                except (socket.timeout): # all day + rtt time <= timeout
                    print("No client response within alloted time.")

            if progresstick > 100:  # prevents you from resending the information again
                progresstick = 100

            my_progress['value'] = progresstick
            root.update_idletasks()  # update all the texts to represent what is is now

        label.config(text="Sent")
        root.update_idletasks()


my_progress = ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')
my_progress.pack(pady=20)

my_button = Button(root, text="Progress", command=step)
my_button.pack(pady=20)

root.mainloop()