# client_class.py
# UDP client using Selective Repeat
import socket
import time
import os
import numpy as np

import server_class
from server_class import ServerClass
from socket import *
from threading import Thread
import pickle
import random


class ClientClass(Thread):
    def __init__(self, fileName, server_ip, server_port, transfer_option):
        Thread.__init__(self)
        self.bufferSize = ServerClass.bufferSize  # 1024 bytes
        self.fileName = fileName  # name of input file to send
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)  # Create the UDP socket
        self.nPackets = 0
        self.seq_num = 0
        self.index = 0
        self.corruptAck = False
        self.AckLoss = False

        # Get server info from Server class
        self.serverAdr = server_ip
        self.serverPort = server_port

        # Store option, desired percent_err/loss, timeout_time, and debug mode
        self.option = transfer_option[0]
        self.percent_err = transfer_option[1] / 100
        self.milli_seconds = transfer_option[2] / 1000  # timeout
        self.debug = transfer_option[3]

        # GBN Timer vars
        self.timer_start = None
        self.timeout_time = self.milli_seconds
        self.window_size = transfer_option[4]  # window_size from GUI
        self.stop_timer = 0

        # Track completion time for data collection
        self.start_time = time.time()
        self.completion_time = None

        if self.option == 2:
            self.corruptAck = True
        elif self.option == 4:
            self.AckLoss = True

    def make_packet(self, file):
        """Parse image file and split it into packets of fixed size"""
        try:
            fileLength = os.path.getsize(file)  # Get the size of the file so we know when to stop parsing
        except:
            print(f"ERROR (Client): Could not find/open the requested file: '{self.fileName}'.")
            os._exit(1)

        # Open and read the file to be transferred
        with open(file, "rb") as image:
            packets = []
            self.nPackets = (
                fileLength // self.bufferSize + 2
            )  # Get total number of packets needed, will need one extra to fit all data
            # Store each bufferSize portion of the file into a list of packets
            for _ in range(0, self.nPackets):
                packets.append(image.read(self.bufferSize))

        return packets

    def udt_send(self, data):
        """Send a packet using the UDP socket"""
        self.clientSocket.sendto(data, (self.serverAdr, self.serverPort))  # Send msg to server

    def start_timer(self):
        """Start a running timer"""
        self.timer_start = time.time()
        self.stop_timer = 0

    def check_timeout(self, start_time, stop_timer):
        """Check if individual packet timer has timedout"""
        if not stop_timer and time.time() - start_time >= self.timeout_time:
            return True
        else:
            return False

    def send_pkt(self, pkt, seq):
        """Assemble a packet for sending, includes checksum, seq, and data"""
        cheksm = server_class.ServerClass.checksum(pkt)  # Calc checksum
        data = server_class.buildPacket(cheksm, seq, pkt)  # assemble pkt
        data_str = pickle.dumps(data)
        return data_str

    def rdt_send(self):
        """Reliable data transfer 1.0: Pass on the data to the receiving side (Server)"""
        packets = self.make_packet(self.fileName)
        print(f"Client: Sending a total of {self.nPackets - 1} packets.")

        # Init window vars
        next_seq_num = 0
        base = 0
        ack_sequence = 0
        self.clientSocket.settimeout(0)  # Non-blocking

        pkt_window = []  # Stores all packets added to the window
        unacked = []  # Running list of packets that have been sent but not been acked yet
        next = [
            *range(0, len(packets))
        ]  # List of all seq numbers for all packets, used to remove acked and sent packets one by one

        # Main loop
        while True:

            # Check if we finished, no unacked packets left and we sent the last packet
            if next_seq_num >= len(packets) - 1 and not unacked:
                break

            # Timeout part of SR protocl, check for individal packet timeout
            # Send individal packets if they have timedout, rather than the whole window(GBN)
            for x in unacked:
                if self.check_timeout(pkt_window[x][1], pkt_window[x][2]):
                    if self.debug:
                        print(f"\t***{x} TIMEOUT***")
                        print(f"\tClient RE-Sending: {x}")
                    data_str = self.send_pkt(pkt_window[x][0], x)
                    self.udt_send(data_str)
                    # Restart the packets time since we just sent it again!
                    pkt_window[x][1] = time.time()

            # Data received from above part of SR
            # Check if we are within the window still and packetize/send it.
            # Pass on data outside the window
            if next_seq_num < base + self.window_size and next_seq_num < len(packets):
                # For SR, append the packet and the current time and if it's clock is stopped
                pkt_window.append([packets[next_seq_num], time.time(), False])
                unacked.append(next_seq_num)
                data = self.send_pkt(packets[next_seq_num], next_seq_num)
                if self.debug:
                    print(f"Client Sending: {next_seq_num}")
                    print(f"Base: {base}, Next_Seq: {next_seq_num}")
                self.udt_send(data)
                next_seq_num += 1
            else:
                # Refuse data...
                pass

            # Get response from the server
            try:
                """Get ACK from Server"""
                message, serverAddress = self.clientSocket.recvfrom(self.bufferSize)
                message = message.decode()
            except Exception as e:
                continue

            """ Option#4, Drop the ACK packet at client side based on input percent"""
            if self.AckLoss and random.random() < self.percent_err:
                # Drop the received ack packet
                if self.debug:
                    print("\tDropping the ACK packet!")
                    print(f"Client: Got NONE")
                continue

            """ Option#2 Corrupt ACK randomly if transfer_option is 2"""
            if self.corruptAck and random.random() < self.percent_err:
                message += "-1"  # Corrupted ACK value!

            # Parse response message
            ack_sequence = message[8:]
            cheksm = message[:5]

            if self.debug:
                print(f"Client: Got ACK{ack_sequence}")

            # Check if: received an ACK packet and it is not corrupt
            if server_class.ServerClass.checksum(message[5:].encode()) == int(cheksm):
                # Check if ack is inside the window
                if int(ack_sequence) in range(base, base + self.window_size):
                    # STOP the packet's timer, it was received correctly.
                    pkt_window[int(ack_sequence)][2] = True

                    # Remove the packet from our helper lists that keep track of sent but unacked packets
                    if int(ack_sequence) in unacked:
                        unacked.remove(int(ack_sequence))
                    if int(ack_sequence) in next:
                        next.remove(int(ack_sequence))

                # Slide the window forward
                if int(ack_sequence) == base:
                    if not next:
                        break
                    # Move base to the smallest unacked packet
                    base = min(min(next), base + self.window_size)

            else:
                if self.debug:
                    print("\tACK packet bit-error!")
                pass
            if self.debug:
                print("Client Window:", np.arange(base, base + self.window_size, 1))

        # Send a done packet instead of the number of expected packets
        final_packet = "done".encode()
        data_str = pickle.dumps(
            server_class.buildPacket(server_class.ServerClass.checksum(final_packet), next_seq_num + 1, final_packet)
        )
        self.udt_send(data_str)

        self.clientSocket.close()  # Close UDP socket
        self.completion_time = time.time() - self.start_time  # Get the duration to transfer the file
        print(
            f"Completion time = {self.completion_time}s for {self.percent_err*100}% loss/error using option {self.option}"
        )

    def run(self):
        """Start the client"""
        self.rdt_send()