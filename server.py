# The main purpose of server.py is to play "hot potato" with messages.
# It receives packets and passes them on. Minimal reading or interpretation
# of the data is done by design to minimize complexity.

import socket
import time
import select
import errno
import pickle
import base64

HEADERSIZE = 10

port = int(input("Enter port number: "))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", port))
server_socket.listen(1)
socket_connections = [server_socket]
user_list = []
# dictionary_of_clients = {}

# create and unwrap packet are wrappers of pickle.dumps/loads.
# The format of a packet is (metadata, data, use_encryption) where
# metadata is always a string of the username and data is a string
# of the message being send. use_encryption is a boolean and denotes
# wether the packet is encrypted or not.


def create_packet(metadata, data, use_encryption=False):
    data = pickle.dumps((metadata, data, use_encryption))
    return data


def unwrap_packet(packet):
    data = pickle.loads(packet)
    return data


def broadcast(packet):
    """
    wrap the packet in the header (just the number of bytes padded up to 10chars)
    and send the wrapped packet to all connected clients
    """
    length = len(packet)
    packet = bytes(f"{length:<10}", "utf-8") + packet
    for client in socket_connections[1::]:
        client.send(packet)


# This is the main loop of the server. It blocks until there is data
# to be read on a socket if the socket to be read is the server_socket,
# a new client is trying to connect. Otherwise a new message is ready
# to be unwrapped and broadcasted to the other clients.

if __name__ == "__main__":
    while True:
        to_read, to_write, errors = select.select(socket_connections, [], [])
        for s in to_read:
            if s == server_socket:
                sockfd, addr = s.accept()
                socket_connections.append(sockfd)
                # print(f":::::: New connection on {addr} ::::::")#DEBUG
                # Note broadcasting the new username to other clients
                # is not possible until the server actually receives the
                # username. It is handled on receiving first actual message
            else:
                try:
                    # print("Attempted receive")#DEBUG
                    incoming_size = int(s.recv(HEADERSIZE))
                    packet = s.recv(incoming_size)
                    if len(packet) == incoming_size:
                        try:
                            data = unwrap_packet(packet)
                            if data[0] not in user_list:
                                broadcast(
                                    create_packet(
                                        "server",
                                        f"{data[0]} has joined. Welcome!"))
                                user_list.append(data[0])
                                # dictionary_of_clients[str(s)] = data[0]
                                # print(dictionary_of_clients)#DEBUG
                            else:
                                broadcast(packet)
                        except Exception as e:
                            print(f"I have failed {e}")
                except Exception as e:
                    print(f"Error handling message: {e}")
                    s.close()
                    socket_connections.remove(s)
