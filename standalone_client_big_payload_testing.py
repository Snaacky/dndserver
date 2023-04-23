import socket
import struct

# Packet command enums
C2S_ALIVE_REQ = 2

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(("127.0.0.1", 13337))

# Prepare a large C2S_ALIVE_REQ packet
packet_command = C2S_ALIVE_REQ
payload = b"A" * 3000  # Change the payload size to simulate a large packet
packet_data = struct.pack("<I", packet_command) + payload

# Send the packet
packet_length = len(packet_data)
client_socket.send(struct.pack("<I", packet_length) + packet_data)

# Close the socket
client_socket.close()