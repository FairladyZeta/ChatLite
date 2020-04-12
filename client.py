import socket
import os
import time
import select
import pickle
import tkinter
import threading
import serial
import serial.tools.list_ports
import base64
from cryptography.fernet import Fernet

HEADERSIZE = 10

# Variables/objects/methods necessary for the program are via
# series of inputs at the start. A dictionary of [y/n] is often
# used for compact boolean arguments

username = input("Enter username: ")
ip = input("Enter server's ip address: ")
port = int(input("Enter number server port: "))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))

use_encryption = {
    "y": True,
    "n": False
}.get(input("Use encryption [y/n] ? ").lower(), "n")

# Setting up the crypto by padding the password in 'a's
# is not the safest idea. But it suffices for the purpose
# of demonstrating encrypted chat client

if use_encryption:
    password = input("Please enter the server password: ")
    if len(password) != 32:
        password += "a" * (32 - len(password))
    key = base64.urlsafe_b64encode(bytes(password, "utf-8"))
    obfuscator = Fernet(key)

arduino = {
    "y": True,
    "n": False
}.get(input("Arduino connected [y/n] ? ").lower(), "n")

# The user can select their arduino from a list of serial ports

if arduino:
    print(f"Enter device path of Arduino (serial ports listed below):")
    ports = list(serial.tools.list_ports.comports())
    dic = {i: j.device for i, j in enumerate(ports)}
    for k, v in dic.items():
        print(f"{k} |  {v}")
    arduino_connection = serial.Serial(dic.get(int(input("selection: ")), 0))

use_notifications = {
    "y": True,
    "n": False
}.get(input("Send desktop notifications [y/n] ? ").lower(), "n")

# send_desktop_notification is defined differently on windows
# or linux. If client.py is running on a windows computer
# win10toast is also imported
# The function does nothing if use_notifications is false

if use_notifications:
    if os.name == "nt":
        from win10toast import ToastNotifier

        global toaster
        toaster = ToastNotifier()

        def send_desktop_notification(text):
            toaster.show_toast("ChatLite", text)

    elif os.name == "posix":

        def send_desktop_notification(text):
            os.system(f"notify-send {text} 1> /dev/null")

else:

    def send_desktop_notification(text):
        pass


if arduino:

    def lcd_print(text):
        if arduino:
            arduino_connection.write(bytes(text, "utf-8"))
else:

    def lcd_print(text):
        pass


# Create/unwrap packet use a variable use_encryption.
# It will be used by default if using encryption is true
# But not used by default if using encryption is false
# BUT, it can still be overrided upon calling the function
def create_packet(metadata, data, use_encryption=use_encryption):
    if use_encryption:
        data = obfuscator.encrypt(bytes(data, "utf-8"))
    data = pickle.dumps((metadata, data, use_encryption))
    length = len(data)
    return bytes(f"{length:<{HEADERSIZE}}", "utf-8") + data


# unwrap packet will attempt to decrypt message if
# use_encryption=true
def unwrap_packet(packet):
    data = list(pickle.loads(packet))
    if data[2] and use_encryption:
        decrypted = obfuscator.decrypt(data[1]).decode('utf-8')
        data[1] = decrypted
    return data


def format_message(data):
    return f"{data[0]}@{time.strftime('%T')}>> {data[1]}"


# This method is called by tkinter when the
# button is pressed
def send_message():
    text = entry_field.get()
    entry_field.delete(0, "end")
    if len(text) != 0:
        if text == "/quit":
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
                message_list.insert(tkinter.END, format_message(message))
                # print(message)#DEBUG
                if message[0] != username:
                    lcd_print(f"{message[0]}: {message[1]}")
                    send_desktop_notification(f"{message[0]}: {message[1]}")

            except Exception as e:
                print(e)


def fin():
    send_packet("/quit")
    client_socket.close()
    exit(0)


def clear_messages():
    message_list.delete(0, "end")


if __name__ == '__main__':
    window = tkinter.Tk()
    window.title(f"Light Chat - {username}")
    messages_frame = tkinter.Frame(window)
    message_entry_box = tkinter.StringVar()
    message_entry_box.set("Type your messages here: ")
    scrollbar = tkinter.Scrollbar(messages_frame)

    message_list = tkinter.Listbox(messages_frame,
                                   height=20,
                                   width=60,
                                   yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    message_list.pack()
    messages_frame.pack()
    entry_field = tkinter.Entry(window,
                                textvariable=message_list,
                                width=55)
    entry_field.bind("<Return>", lambda _: send_message())
    entry_field.pack(side=tkinter.LEFT, fill=tkinter.X)
    send_button = tkinter.Button(window, text="Send", command=send_message)
    send_button.pack(side=tkinter.RIGHT)

    menubar = tkinter.Menu(window)
    menubar.add_command(label="quit", command=fin)
    # menubar.add_command(label='settings', command=settings_page)
    menubar.add_command(label="clear", command=clear_messages)
    window.config(menu=menubar)
    window.protocol("WM_DELETE_WINDOW", fin)
    # Send initial message to be read by server
    send_packet("")
    message_handler_thread = threading.Thread(target=message_handler,
                                              daemon=True)
    message_handler_thread.start()
    window.mainloop()
