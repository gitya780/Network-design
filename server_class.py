# server_class.py
# UDP server using Selective Repeat
import random
from socket import *
from threading import Thread
from array import array
import pickle
import time
import numpy as np


class buildPacket:
    def __init__(self, checksum, seq, image_bytes):
        self._checksum = checksum
        self._seq = seq
        self._image_bytes = image_bytes


class ServerClass(Thread):
    # Init server address and port
    serverAdr = None
    serverPort = None
    bufferSize = 1024  # 1024B

    def __init__(self, fileName, server_ip, server_port, transfer_option, gui_window):
        Thread.__init__(self)
        self.clientAddress = None
        self.fileName = fileName  # Output file name
        self.serverAdr = server_ip
        self.serverPort = server_port
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)  # Create the socket
        self.serverSocket.bind((self.serverAdr, self.serverPort))  # Bind socket to server port
        self.seq_num = 0
        self.gui_window = gui_window  # For refreshing the gui
        self.corruptData = False
        self.dataLoss = False

        # Store option, desired percent_err/loss, and debug mode
        self.option = transfer_option[0]
        self.percent_err = transfer_option[1] / 100
        self.debug = transfer_option[3]
        self.window_size = transfer_option[4]  # window_size from GUI

        if self.option == 3:
            self.corruptData = True
        elif self.option == 5:
            self.dataLoss = True

    @staticmethod
    def checksum(packet):
        if len(packet) % 2 != 0:
            packet += b"\0"

        result = sum(array("H", packet))
        result = (result >> 16) + (result & 0xFFFF)
        result += result >> 16
        return (~result) & 0xFFFF

    def extract(self, pkt):
        """Extract data from the received packet"""
        data, self.clientAddress = pkt
        return data

    """ Option#3 """

    def corrupt(self, data):
        """Tweak data bits to corrupt the packet"""
        if self.corruptData and random.random() < self.percent_err:
            if self.debug:
                print("\tData packet bit-error!")
            data = 0

        return bytes(data)

    def verifyChecksum(self, data, checksum):
        """Validate the checksum"""
        return self.checksum(data) == checksum

    def deliver_data(self, data, image):
        """Deliver data to the upper layer"""
        image.write(bytearray(data))  # Convert list of bytes to bytearray for writing

    def udt_send(self, packet):
        """Send a packet using the UDP socket"""
        self.serverSocket.sendto(packet.encode(), self.clientAddress)  # Send ECHO msg back to client

    def make_pkt(self, expectedseqnum):
        """Assemble the ACK packet to send back to the client"""
        ack = "ACK" + str(expectedseqnum)
        return str(self.checksum(ack.encode())) + ack

    def rdt_rcv(self):
        """Reliable Data Rransfer 2.2: Receive packets from the sending side (Client)"""
        print("Server: Ready to receive!")

        packets = []  # Image data list
        resp = self.make_pkt(-1)  # On FSM entry

        # SR variables
        base = 0
        recv_packets = []
        buffer = []

        while True:
            pkt = self.serverSocket.recvfrom(2048)  # Read data from UDP socket
            packet = pickle.loads(self.extract(pkt))

            checksum = packet._checksum
            seq_num = packet._seq
            image_data = packet._image_bytes

            # Init the window:
            window = np.arange(base, base + self.window_size, 1)

            if self.debug:
                print("Server Window:", window)
            # Rather than wait to reach for the expected packet, check if we got the last packet from the client
            try:
                if image_data.decode().find("done") != -1:
                    print(
                        (
                            f"Done receiving image! Recieved {len(recv_packets)} packets from the client.\n\tSaved as '{self.fileName}'."
                        )
                    )
                    break
            except:
                pass

            """Option 5. Drop the data received from client random loss (input)"""
            if self.dataLoss and random.random() < self.percent_err:
                if self.debug:
                    print("\tDropping the DATA packet!")
                continue

            """Option 3. Corrupt the data packet given loss percentage from GUI"""
            image_data = self.corrupt(bytearray(image_data))

            "Check if: received pkt is not corrupt and it is within the window"
            if self.verifyChecksum(image_data, checksum) and int(seq_num) in window:

                """Send ACK + seq_num"""
                if self.debug:
                    print(f"Server: ACK{seq_num}")
                resp = self.make_pkt(int(seq_num))
                self.udt_send(resp)

                # Check if we have received the pkt before, if not add it to the list
                if seq_num not in recv_packets:
                    recv_packets.append(int(seq_num))
                    buffer.append([image_data, int(seq_num)])  # Add pkt to running buffer to send later

                # If the seq num equals the base, deliver the sequential packets
                if seq_num == base:
                    buffer.sort(key=lambda x: x[1])  # Sort for determining sequential pkts

                    # First packet is always OK to deliver
                    packets.append(buffer[0][0])
                    n = 1
                    # Check if we have the n+1 packet
                    for i in range(1, len(buffer)):
                        # If we do, then increment n
                        if buffer[i - 1][1] + 1 == buffer[i][1]:
                            packets.append(buffer[i][0])  # Deliver the sequential packets
                            n += 1
                        else:
                            # Otherwise keep the last value of n
                            break
                    # Move the window by the number of sequential packets in the buffer (n)
                    base += n
                    del buffer[0:n]  # Remove the packets since we delivered them already

            # The data is valid, but it's from the previous window, just ACK it.
            elif self.verifyChecksum(image_data, checksum) and int(seq_num) in np.arange(
                base - self.window_size, base, 1
            ):
                """Send ACK + seq_num"""
                if self.debug:
                    print(f"Server: ACK{seq_num}")
                resp = self.make_pkt(seq_num)
                self.udt_send(resp)
            else:
                pass

        # Open and close the output image file just to reset it
        with open(self.fileName, "wb") as _:
            pass
        image = open(self.fileName, "ab")
        for pkt in packets:
            self.deliver_data(pkt, image)  # Assemble the transfer file
            try:
                self.gui_window.update_received_img()
            except:
                pass
        image.close()
        try:
            self.gui_window.update_received_img()
        except:
            pass
        print("Completed! You can close the GUI...")

    def run(self):
        """Start the server"""
        self.rdt_rcv()