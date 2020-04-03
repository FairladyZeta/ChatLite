import socket
import threading
import time
import select
import errno
import pickle
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

HEADERSIZE = 10

port = int(input("Enter port number: "))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', port))
server_socket.listen(1)
socket_connections = [server_socket]
user_list = []
#use_encryption = {'y':True, 'n':False}.get(input("Use encryption [y/n] ? ").lower(), 'n')

#if use_encryption:
#    password = input("Please enter the server password: ")
#    if len(password) != 32:
#        password += 'a' * (32 - len(password))
#    key = base64.urlsafe_b64encode(bytes(password, 'utf-8'))
#    obfuscator = Fernet(key)


def create_packet(metadata, data):
    data = pickle.dumps((metadata, data))
    return data

def unwrap_packet(packet):
    data = pickle.loads(packet)
    return data

def broadcast(packet):
    length = len(packet)
    packet = bytes(f"{length:<10}", 'utf-8') + packet
    for client in socket_connections[1::]:
        client.send(packet)

def process_message(data):
    if data[0] not in user_list:
        user_list.append(data[0])
        smsg = create_packet('server', f"{data[0]} has joined. Welcome!")
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
