import socket
import threading
import time
import select
import errno
import pickle
import base64

HEADERSIZE = 10

port = int(input("Enter port number: "))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', port))
server_socket.listen(1)
socket_connections = [server_socket]
user_list = []
dictionary_of_clients = {}


def create_packet(metadata, data, use_encryption=False):
    data = pickle.dumps((metadata, data, use_encryption))
    return data


def unwrap_packet(packet):
    data = pickle.loads(packet)
    return data


def broadcast(packet):
    length = len(packet)
    packet = bytes(f"{length:<10}", 'utf-8') + packet
    for client in socket_connections[1::]:
        client.send(packet)


while True:
    to_read, to_write, errors = select.select(socket_connections, [], [])
    for s in to_read:
        if s == server_socket:
            sockfd, addr = s.accept()
            socket_connections.append(sockfd)
            #print(f":::::: New connection on {addr} ::::::")#DEBUG
        else:
            try:
                #print("Attempted receive")#DEBUG
                incoming_size = int(s.recv(HEADERSIZE))
                packet = s.recv(incoming_size)
                if len(packet) == incoming_size:
                    try:
                        data = unwrap_packet(packet)
                        if data[0] not in user_list:
                            broadcast(
                                create_packet(
                                    'server',
                                    f"{data[0]} has joined. Welcome!"))
                            user_list.append(data[0])
                            dictionary_of_clients[str(s)] = data[0]
                            #print(dictionary_of_clients)#DEBUG
                        else:
                            broadcast(packet)
                    except Exception as e:
                        print(f"I have failed {e}")
            except Exception as e:
                print(f"Error handling message: {e}")
                s.close()
                socket_connections.remove(s)
