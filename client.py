import socket
import time
import select
import pickle
import tkinter
import threading
import serial
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


HEADERSIZE = 10

username = input("Enter username: ")
ip = input("Enter server's ip address: ")
port = int(input("Enter number of server port: "))
arduino = {'y':True, 'n':False}.get(input("Arduino connected?").lower(), 'n')
use_encryption = {'y':True, 'n':False}.get(input("Use encryption [y/n] ? ").lower(), 'n')


if use_encryption:
    password = input("Please enter the server password: ")
    if len(password) != 32:
        password += 'a' * (32 - len(password))
    key = base64.urlsafe_b64encode(bytes(password, 'utf-8'))
    obfuscator = Fernet(key)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))
if arduino:
    arduino_connection = serial.Serial('/dev/ttyACM0')

def lcd_print(text):
    if arduino:
        arduino_connection.write(bytes(text, 'utf-8'))
    else:
        pass

def create_packet(metadata, data):
    data = pickle.dumps((metadata, data))
    if use_encryption:
        data = obfuscator.encrypt(data)
    length = len(data)
    return bytes(f"{length:<10}", 'utf-8') + data

def unwrap_packet(packet):
    if use_encryption:
        data = obfuscator.decrypt(packet)
        data = pickle.loads(data)
    else:
        data = pickle.loads(packet)
    return data

def format_message(data):
    return f"{data[0]}: {data[1]}"

def send_message():
    text = entry_field.get()
    entry_field.delete(0, 'end')
    if len(text) != 0:
        if text == '/quit':
            fin()
        else:
            send_packet(text)

def send_packet(text):
    packet = create_packet(username, text)
    try:
        client_socket.send(packet)
    except Exception as e:
        print(f"Failed to send message: {e}")
        client_socket.close()
        exit(0)

def message_handler():
    while True:
        to_read, to_write, error = select.select([client_socket], [], [])
        for s in to_read:
            try:
                try:
                    length = int(s.recv(HEADERSIZE))
                except Exception as e:
                    print(e)
                    fin()
                data = s.recv(length)
                message = unwrap_packet(data)
                msg_list.insert(tkinter.END, format_message(message))
                print(message)
                if message[0] != username:
                    lcd_print(f"{message[0]}: {message[1]}")

            except Exception as e:
                print(e)

def fin():
    send_packet('/quit')
    client_socket.close()
    exit(0)

def settings_page():
    swindow = tkinter.Toplevel()
    swindow.wm_title('settings')
    close_button = tkinter.Button(swindow, text='Close', command=swindow.destroy)
    close_button.pack()

if __name__ == '__main__':
    window = tkinter.Tk()
    window.title("Light Chat")
    messages_frame = tkinter.Frame(window)
    msg_box = tkinter.StringVar()
    msg_box.set("Type your messages here: ")
    scrollbar = tkinter.Scrollbar(messages_frame)
    
    msg_list = tkinter.Listbox(messages_frame, height=15, width=50,
            yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msg_list.pack()
    messages_frame.pack()
    entry_field = tkinter.Entry(window, textvariable=msg_list)
    entry_field.bind("<Return>", send_message())
    entry_field.pack()
    send_button = tkinter.Button(window, text="Send", command=send_message)
    send_button.pack()

    menubar = tkinter.Menu(window)
    menubar.add_command(label='quit', command=fin)
    menubar.add_command(label='settings', command=settings_page)
    menubar.add_command(label='connect')
    window.config(menu=menubar)
    window.protocol("WM_DELETE_WINDOW", fin)
    send_packet('')
    message_handler_thread = threading.Thread(target=message_handler, daemon=True)
    message_handler_thread.start()
    window.mainloop()
