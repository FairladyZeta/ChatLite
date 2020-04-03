import socket
import time
import select
import pickle
import tkinter
import threading
import serial


HEADERSIZE = 10

username = input("Enter username: ")
ip = '127.0.0.1'
port = 1234
arduino = True
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
    length = len(data)
    return bytes(f"{length:<10}", 'utf-8') + data

def unwrap_packet(packet):
    return pickle.loads(packet)

def format_message(data):
    return f"{data[0]}: {data[1]}"

def send_message():
    text = entry_field.get()
    if len(text) != 0:
        if text == '/quit':
            entry_field.delete(0, 'end')
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
                length = int(s.recv(HEADERSIZE))
                data = s.recv(length)
                message = unwrap_packet(data)
                msg_list.insert(tkinter.END, format_message(message))
                print(message)
                lcd_print(message[1])

            except Exception as e:
                print(e)

def fin():
    send_packet('/quit')
    client_socket.close()
    exit(0)

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
window.protocol("WM_DELETE_WINDOW", fin)


send_packet('')
message_handler_thread = threading.Thread(target=message_handler, daemon=True)
message_handler_thread.start()
window.mainloop()
