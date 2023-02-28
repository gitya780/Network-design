#this one recieves the image
import socket #importing network library
import time #importing time library
import threading
from threading import Lock
import math
import random
import numpy as np
from PIL import Image, ImageTk
import numpy as np
import io
import sys


randomvalue = sys.argv[1] # get the input by the user from the commandline
barriervalue = sys.argv[2]
randomvalue = int(float(randomvalue)) # typecasting the value from float to integer
barriervalue = int(float(barriervalue))

mutex = Lock()

recieved_packets = []
sendflag = 0
message = ""
totaltick = 0
messagelist = []
def sender():
    global sendflag
    global message
    UDP_IP = "127.0.0.1"#IP address UDP is occuring at
    UDP_PORT = 5006#port this program will output over

    check_MESSAGE  = -10

    #while check_MESSAGE != total_packets:
    while True:
        while len(messagelist) > 0:
            MESSAGE = str(messagelist[0])
            #print("Client-Sender: Sending Back Ack: ", MESSAGE)
            MESSAGE = MESSAGE.encode() #turn string to bytes-like object
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
            if (len(messagelist) > 0):
                messagelist.pop(0)
            check_MESSAGE = MESSAGE.decode()
            check_MESSAGE = int(check_MESSAGE)
            #print("Check Message Versus Total_Packets", check_MESSAGE, total_packets)

def reciever():
    global sendflag
    global message
    global totaltick
    global packet_number
    global total_packets
    global _start_time
    global barriervalue
    global randomvalue

    UDP_IP = "127.0.0.1" #IP address UDP is occuring at
    UDP_PORT = 5005 #port from initial sender

    #settup to recieve from socket over port 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    recieved_message = []
    duplicate_finder = []
    previous_goodPacket = str(0)
    
    while True:

        #print("____________________________")
        #print("Total Packets: ", total_packets)
        #print("Packet Number: ", packet_number)
        data, addr = sock.recvfrom(1060) # buffer size of data
        message = data
        unformatted_header_data = message[0:27]

        header_data = []
        duplicate = 0
        reconstruction = ""

        #print("Client-Receiver: newdata", unformatted_header_data)
        for j in range(len(unformatted_header_data)):
            if str(chr(int(unformatted_header_data[j]))) != "-":
                reconstruction += str(chr(int(unformatted_header_data[j])))
            if str(chr(int(unformatted_header_data[j]))) == "-":
                if len(reconstruction) > 0:
                    header_data.append(reconstruction)
                    reconstruction = ""

        #print("Client-Receiver: header_data", header_data)
        message = message[28:]

        ####################### Rebuilding Checksum on receiving end to make sure data is correct ######################

        total_packets = int(header_data[0]) # Collect the total number of pkts that will be received
        packet_number = header_data[1] # Collect the pkt number of the pkt being received

        # Initializing check_sum array
        check_sum = []
        for k in range(4):
            check_sum.append(0)

        ack = 0
        pos = 0

        for j in message:
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
            check_sum[k] = str(int(check_sum[k] / len(message) * 4))

        if header_data[2] != check_sum[0]:
            ack += 0
        else:
            ack += 1

        if header_data[3] != check_sum[1]:
            ack += 0
        else:
            ack += 1

        if header_data[4] != check_sum[2]:
            ack += 0
        else:
            ack += 1

        if header_data[5] != check_sum[3]:
            ack += 0
        else:
            ack += 1

        check_sum_approval = ack/len(check_sum) # Equal to 1 when chksum matches header chksum or < 1 for corrupted pkts
        #print("Client-Receiver: CHECK SUM APPROVAL VALUE ", check_sum_approval)

        ##################################### Checking for Duplicate Packets ###########################################

        for k in duplicate_finder:
            if (str(k) == header_data[1]):
                #print("Received Duplicate")
                duplicate = 1

        #enable_loss_error = 1
        #for i in range(51):
        #    enable_loss_error = enable_loss_error and (int(packet_number) != total_packets - i)
        # print("THis is enable loss", enable_loss_error)

        ############################### Implementation of ACK Loss/Error Based on Sequence Number ######################
        enable_loss = 0

        if (check_sum_approval == 1):

            if duplicate == 0 and int(packet_number) == len(recieved_message) + 1:
                sendflag = 1
                totaltick += 1
                #print("Adding to Image Packet Number: ", packet_number)
                recieved_message.append(message)
                duplicate_finder.append(packet_number)
                messagelist.append(packet_number)
            elif (int(packet_number) > len(recieved_message) + 1 and duplicate == 0):
                messagelist.append(previous_goodPacket) # Send the previous good packet if dropped along transmission from sender
            else:
                messagelist.append(packet_number) # Send back the corresponding ack for any duplicate packets

        else:
            messagelist.append(previous_goodPacket) # Send the previous good packet ACK if the packet data is corrupted

        if random.randint(0, 100) < barriervalue:
            sendflag = 0
            totaltick += 1
            mutex.acquire()
            messagelist.clear()
            mutex.release()
            #print("---------DROP ACK VALUE---------")
        elif random.randint(0, 100) < randomvalue:
            sendflag = 1
            totaltick += 1
            enable_loss = 1
            mutex.acquire()
            messagelist.clear()
            messagelist.append(str(random.randint(1000,6000)))
            mutex.release()
            #print("---------SEND ACK ERROR---------")
        else:
            if (enable_loss == 0 and check_sum_approval == 1): # If the packet ACK undergoes error do not update the previous_goodPacket to that value
                previous_goodPacket = packet_number
            #print("+++++++++SEND ACK VALUE++++++++")

        ################################################################################################################
        
        # If you have received all required packets recreate the image
        if (int(packet_number) == 1):
            _start_time = time.perf_counter()

        if (len(recieved_message) == total_packets):
            _end_time = time.perf_counter()
            print("total time = ", _end_time - _start_time)
            image = recieved_message[0]
            for i in range(1, total_packets):
                image = image + recieved_message[i]
            # Take the image and convert to a byte stream, to save as a seperate file
            save_image = Image.open(io.BytesIO(image))
            # Save the sent image in the same directory named DecodedImage.bmp
            save_image.save("DecodedImage.bmp")
            #print("This is message list", len(messagelist))
            break
 

send = threading.Thread(target = sender,args=())
rec = threading.Thread(target = reciever,args=())
total_packets = -50
packet_number = -20
print("Server ready to receive: ")

rec.start()
send.start()
rec.join()
send.join()