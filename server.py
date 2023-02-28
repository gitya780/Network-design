# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 09:01:47 2022

@author: Geetesh
"""

import tkinter as tk # import the module for GUI
from tkinter import ttk # ttk  import for more advance theme widget in GUI
from tkinter import *
import time 
import cv2  # import the libary of openCV
from PIL import Image, ImageTk  # loading python imaging library
import numpy as np 
import socket
import math

#The IP ADDRESS of localhost is 127.0.0.1
UDP_SERVER_IP_ADDRESS = "127.0.0.1"

#Randomly chose this port from the available list found on https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
UDP_PORT_NUMBER = 2000

#create socket for client
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

root = tk.Tk() #label the widget
root.title('Image Transfer GUI')
root.iconbitmap('')
root.geometry("600x400") #size of the gui box

Imagenametxt=Label(root, text="Image Name", font=('Calibri 15'))
Imagenametxt.pack()
textname=tk.Text(root,width=20,height=1)
textname.insert(END,"")
textname.pack()

#if progress button click start labeling
label=Label(root, text="", font=('Calibri 15'))
label.pack()
progresstick = 0

send_d = []

def step():
	global progresstick
	global displayimage

	input_textname = textname.get(1.0, "end-1c") #collecting image file name from textbox

	file = open(input_textname, 'rb')
	input_im = file.read()

	packet_amount = math.floor(len(input_im)/1024)

	#Creating the packets of data
	for i in range(packet_amount):
		bytes_s = input_im[i*1024:(i+1)*1024]
		send_d.append(bytes_s)

	if (len(input_im) % 1024 != 0):
		bytes_s = input_im[len(send_d)*1024:len(input_im)]
		send_d.append(bytes_s)
		packet_amount = packet_amount + 1

	msg = str(packet_amount)
	transmit = clientSocket.sendto(msg.encode(), (UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBER))	#sending data to server

	if progresstick >= 100:
		label.config(text="Already Sent")
		root.update_idletasks()
	else:
		label.config(text="Sending")
		root.update_idletasks()
		for i in range(len(send_d)):
			progresstick += 100/len(send_d)

			###########################################################################################
			transmit = clientSocket.sendto(send_d[i], (UDP_SERVER_IP_ADDRESS, UDP_PORT_NUMBER))	#sending data to server
			############################################################################################

			if progresstick > 100:  #prevents you from resending the information again
				progresstick = 100

			my_progress['value'] = progresstick
			root.update_idletasks() #update all the texts to represent what is is now

		label.config(text="Sent")
		root.update_idletasks()

my_progress = ttk.Progressbar(root,orient=HORIZONTAL,length=300,mode='determinate')
my_progress.pack(pady=20)

my_button = Button(root,text="Progress",command=step)
my_button.pack(pady=20)

root.mainloop()