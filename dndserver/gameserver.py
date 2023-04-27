from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import binascii
import struct


class dungeonserver(DatagramProtocol):
    def __init__(self):
        self.clients = set()

    def datagramReceived(self, data, address):  
        if len(data) < 24:
            print("Received non-UE5 packet from {}: {}".format(address, data))
            return

        header = struct.unpack_from("<QIIBBBI", data, 0)

        packet_size = header[0]  # Size of the entire packet, including header
        packet_seq = header[1]   # Sequence number of the packet
        packet_ack = header[2]   # Acknowledgement number of the packet
        packet_flags = header[3] # Packet flags
        packet_channel = header[4] # Channel index
        packet_chSequence = header[5] # Channel sequence number
        packet_messageType = header[6] # Message type

        payload = data[24:]
        print(data)
        print("Received UE5 packet from {}: size={}, seq={}, ack={}, flags={}, channel={}, chSequence={}, messageType={}, payload={}".format(address, packet_size, packet_seq, packet_ack, packet_flags, packet_channel, packet_chSequence, packet_messageType, binascii.hexlify(payload)))

if __name__ == "__main__":
  
    port = 7777

    dungeonserver = dungeonserver()

    reactor.listenUDP(port, dungeonserver)
    
    reactor.run()