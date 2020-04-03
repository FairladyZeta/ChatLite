import socket
import threading
import time
import select
import errno
import pickle

HEADERSIZE = 10
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 1234))
server_socket.listen(1)
socket_connections = [server_socket]


def create_packet(metadata, data):
    data = pickle.dumps((metadata, data))
    return data

def unwrap_packet(packet):
    return pickle.loads(packet)

def broadcast(packet):
    length = len(packet)
    packet = bytes(f"{length:<10}", 'utf-8') + packet
    for client in socket_connections[1::]:
        client.send(packet)

def process_message(data):
    if data[1] == '':
        print("huh")
        smsg = create_packet('server', f"{data[0]} has joined! Welcome!")
    elif data[1] == '/quit':
        smsg = create_packet('server', f"{data[0]} has quit.")
        broadcast(smsg)
        return 0
    else:
        smsg = create_packet(*data)
    broadcast(smsg)
    return 1

while True:
    to_read, to_write, errors = select.select(socket_connections, [], [])
    for s in to_read:
        if s == server_socket:
            sockfd, addr = s.accept()
            socket_connections.append(sockfd)
            print(f":::::: New connection on {addr} ::::::")
        else:
            try:
                print("Attempted receive")
                incoming_size = int(s.recv(HEADERSIZE))
                data = s.recv(incoming_size)
                if len(data) == incoming_size:
                    if not process_message(unwrap_packet(data)):
                        s.close()
                        socket_connections.remove(s)
                    print(data)
            except Exception as e:
                print(f"Error handling message: {e}")
                s.close()
                socket_connections.remove(s)