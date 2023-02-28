#this one sends the image

import tkinter as tk  # import the module for GUI
from tkinter import ttk  # ttk  import for more advance theme widget in GUI
from tkinter import *


import socket #importing network library
import time #importing time library
import threading
from threading import Lock
import math
import random
import numpy as np
import sys

mutex = Lock()
washout = 0

randomvalue = sys.argv[1] # get the input by the user from the commandline
barriervalue = sys.argv[2]
windowvalue = sys.argv[3]
randomvalue = int(float(randomvalue)) # typecasting the value from float to integer
barriervalue = int(float(barriervalue))
windowvalue = int(float(windowvalue))

root = tk.Tk()
root.title('Image Transfer GUI')  # title of gui
root.iconbitmap('')
root.geometry("600x400")  # size of the gui box

Imagenametxt = Label(root, text="Image Name", font=('Calibri 15'))
Imagenametxt.pack()
textname = tk.Text(root, width=20, height=1)
textname.insert(END, "")
textname.pack()

# if progress button click start labeling
label = Label(root, text="", font=('Calibri 15'))
label.pack()
progresstick = 0


######### Addition of file-opening (currently hard coded to one specific image #############


datalist = [] # list that will be used to send data to client
packet_number = 0



############################################################################################

packet_addition = 0
sendlist = []
returnlist = []
window = windowvalue
def sender():
    global sendlist
    global returnlist
    global datalist
    global washout
    global packet_addition
    global packet_amount
    global barriervalue
    global randomvalue
    
    UDP_IP = "127.0.0.1"#IP address UDP is occuring at
    UDP_PORT = 5005#port this program will output over

    iteration = 0;
    packet_number = 0;

    emptypacket = ""
    for i in range(0, 1000):
        emptypacket += str(random.randint(0, 9))
    emptypacket = str.encode(emptypacket)
    
    while len(datalist) > 0:
        #while (len(sendlist) < window and len(datalist) >= window) or (len(sendlist) < len(datalist) and len(datalist) < window) and int(packet_number) <= packet_amount and washout == 0:
        while ((len(sendlist) < window and len(datalist) >= window) or (len(sendlist) < len(datalist) and len(datalist) < window) and int(packet_number) <= packet_amount) and washout == 0:
        #while ((len(sendlist) < window and len(datalist) >= window) or (len(sendlist) < len(datalist) and len(datalist) < window)) and washout == 0:

          ########################### Create the checksum for the packet that will be sent ###############################

            # Initialize the check_sum field
            check_sum = []
            for k in range(4):
                check_sum.append(0)

            i = len(sendlist) # Collect

            pos = 0
            for j in datalist[i]:
                if pos % 4 == 0:
                    check_sum[0] += j
                if pos % 4 == 1:
                    check_sum[1] += j
                if pos % 4 == 2:
                    check_sum[2] += j
                if pos % 4 == 3:
                    check_sum[3] += j
                pos += 1

            for k in range(len(check_sum)):
                check_sum[k] = str.encode(str(int(check_sum[k] / len(datalist[i]) * 4)))

            packet_number = str(len(sendlist) + packet_addition + 1)
            #print("___________________________________")
            #print("PACKET NUMBER ", packet_number)
            pcktnumber = str.encode(packet_number)
            numberofpkt = str.encode(str(packet_amount))

            while (len(check_sum[0]) < 5):
                check_sum[0] += str.encode("-")
            while (len(check_sum[1]) < 5):
                check_sum[1] += str.encode("-")
            while (len(check_sum[2]) < 5):
                check_sum[2] += str.encode("-")
            while (len(check_sum[3]) < 5):
                check_sum[3] += str.encode("-")
            while (len(pcktnumber) < 4):
                pcktnumber += str.encode("-")
            while (len(numberofpkt) < 4):
                numberofpkt += str.encode("-")

            completed_Checksum = numberofpkt + pcktnumber + check_sum[0] + check_sum[1] + check_sum[2] + check_sum[3]
            #print("Completed Checksum", completed_Checksum)
            #print("Data List", datalist[len(sendlist)])

            #enable_loss_error = 1
            #total_packets = packet_amount
            #for i in range(51):
            #    enable_loss_error = enable_loss_error and (int(packet_number) != total_packets - i)
            #print("THis is enable loss", enable_loss_error)

            ##################################### Implementing Packet Error/Drop ##########################################

            drop_packet = 0

            if random.randint(0, 100) < barriervalue:
                drop_packet = 1
                sendlist.append("")
                #print("---------DROP PACKET DATA----------")
            elif random.randint(0, 100) < randomvalue:
                MESSAGE = completed_Checksum + emptypacket  # Append the checksum to the image bytes here
                sendlist.append(str(packet_number))
                #print("---------SEND PACKET ERROR---------")
                # else (int(packet_number) <= packet_amount):
            else:
                MESSAGE = completed_Checksum + datalist[len(sendlist)]  # Append the checksum to the image bytes here
                sendlist.append(str(packet_number))
                #print("+++++++++SEND PACKET DATA++++++++++")

            if (drop_packet == 0):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

            l = 0 # Used to prevent washout operation to go on idefinetly

        while len(returnlist) > 0 and washout == 0:
            l = l + 1
            mutex.acquire()
            #print("Server-Sender: Packet Acks Received ",returnlist)
            #print("Server-Sender: Packets sent ",sendlist)
            i = returnlist[0]
            if len(sendlist) > 0:
                if i == sendlist[0]:
                    packet_addition = packet_addition + 1
                    datalist.pop(0)
                    sendlist.pop(0)
                    returnlist.pop(0)
                else:
                    washout = len(sendlist) - len(returnlist)
                    #print("+++++++++++++",i," ",sendlist[0])
                    #print("wash: ",washout)
                    sendlist = []
                    returnlist = []
                    mutex.release()
                    break
            mutex.release()
            if (l > 15):
                l = 0
                break
        while washout > 0 and len(returnlist) > 0:
            returnlist.pop(0)
            washout -= 1

def reciever():
    global sendlist
    global returnlist
    global datalist
    global washout
    current = 0
    UDP_IP = "127.0.0.1" #IP address UDP is occuring at
    UDP_PORT = 5006 #port from initial sender

    #settup to recieve from socket over port 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    
    data = "fail"
    while len(datalist) != 0:
        try:

            sock.settimeout(0.06) #update timeout value here
            data, addr = sock.recvfrom(1024) # buffer size of data
            #print("Received ACK: ", data.decode())
            #print("This is sendlist, and washout value",sendlist, washout)
            if len(sendlist) > 0:

                if (sendlist[0] == ''):  # This is the value when there is a packet loss
                    pass
                elif int(data.decode()) > int(sendlist[0]):
                    for i in range(int(sendlist[0]) - int(data.decode())):
                        returnlist.append("0")
            else:
                pass
            
            if washout == 0:
                mutex.acquire()
                returnlist.append(str(data.decode()))
                mutex.release()
            else:
                washout -= 1
                #print("wash drop: ",washout)
                if (washout < 0):
                    washout = 0
        except (socket.timeout):
            #print("fail")
            #print("timeout fail")
            if washout == 0:
                mutex.acquire()
                returnlist.append(0)
                mutex.release()
            else:
                washout -= 1
                #print("wash drop: ",washout)
                if (washout < 0):
                    washout = 0

datasize = len(datalist)

def progress_send():
    global datasize
    global datalist
    global packet_amount
    
    
    input_textname = textname.get(1.0, "end-1c")  # collecting image file name from textbox

    file = open(input_textname, 'rb')  # open the image in binary format for reading
    input_im = file.read()
    
    packet_amount = math.floor(len(input_im) / 1024)  # number of packets

    # Creating the packets of data, each packet has 1024 bytes.
    for i in range(packet_amount):
        bytes_s = input_im[i * 1024:(i + 1) * 1024]
        datalist.append(bytes_s)  # adding a single packet to the existing list

    # Creating final packet to send to server (this packet is always less than 1024 bytes)
    if (len(input_im) % 1024 != 0):
        bytes_s = input_im[len(datalist) * 1024:len(input_im)]
        datalist.append(bytes_s)
        packet_amount = packet_amount + 1
    datasize = len(datalist)
    totalsize = datasize
    send = threading.Thread(target = sender,args=())
    rec = threading.Thread(target = reciever,args=())
    rec.start()
    send.start()
    
    
    while len(datalist) != 0:
        my_progress['value'] = 100 * (totalsize - len(datalist))/totalsize
        root.update_idletasks()  # update all the texts to represent what is is now
        #print("=================update==================")
        #print("datalist: ",len(datalist))
        #print("progress value: ",100 * (totalsize - len(datalist))/totalsize)
        time.sleep(.1)
    
    my_progress['value'] = 300
    root.update_idletasks()  # update all the texts to represent what is is now
    

    




my_progress = ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')
my_progress.pack(pady=20)


my_button = Button(root, text="Progress", command=progress_send)
my_button.pack(pady=20)
#time.sleep(5)
root.mainloop()

#rec.join()
#send.join()