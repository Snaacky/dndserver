import socket
import time
import random

# You can create multiple instances of this client to simulate different clients sending packets simultaneously. 
# To test edge cases, you can modify the send_packet_segments function to send segments out of order, or adjust the delay between segments.

# Packet data
packet_data = b'\x1e\x00\x00\x00\x0c\x00\x00\x00'

def send_packet_segments(client_socket, packet_data, delay):
    segment_size = random.randint(1, len(packet_data) - 1)
    for i in range(0, len(packet_data), segment_size):
        segment = packet_data[i:i + segment_size]
        client_socket.send(segment)
        time.sleep(delay)

def main():
    server_address = ('localhost', 13337)  # Replace with your server's address and port

    # Create a client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    # Send packet segments with delay
    send_packet_segments(client_socket, packet_data, delay=0.5)

    # Close the client socket
    client_socket.close()

if __name__ == '__main__':
    main()