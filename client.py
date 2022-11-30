import tkinter as tk
from tkinter import messagebox
import socket
import threading
import winsound
import json
with open("config.json", "r+") as conf: # open in readmode and create the file if not exists
  config = json.load(conf)
  server_addr = config.get("ip")
  server_port = config.get("port")

window = tk.Tk()
window.config(background="#112637")
window.title("ChatApp - Client")
window.iconbitmap("icon.ico")
username = " "


topFrame = tk.Frame(window, background="#112637")
lblName = tk.Label(topFrame, text = "Username:", fg="white", background="#112637").pack(side=tk.LEFT)
entName = tk.Entry(topFrame, background="#27557b", fg="white")
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Connect", bg="#68697a", fg="white", command=lambda : connect())
btnConnect.pack(side=tk.LEFT, padx=5)
topFrame.pack(side=tk.TOP, pady=10)

displayFrame = tk.Frame(window, background="#112637")
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55, background="#214868", fg="white")
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="yellow")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, state="disabled")
displayFrame.pack(side=tk.TOP, pady=10, padx=10)


bottomFrame = tk.Frame(window, background="#112637")
tkMessage = tk.Text(bottomFrame, height=2, width=55, background="#214868", fg="white")
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)


def connect():
    global username, client
    if len(entName.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        username = entName.get()
        connect_to_server(username)


# network client
client = None
HOST_ADDR = server_addr
HOST_PORT = server_port

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Send name to server after connecting

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        threading._start_new_thread(receive_message_from_server, (client, "m"))
        winsound.PlaySound("audio/alert.wav", winsound.SND_ASYNC)
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: break

        # display message from server on the chat window
        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            # Other users sent message
            tkDisplay.insert(tk.END, "\n\n"+ from_server)
            winsound.PlaySound("audio/alert.wav", winsound.SND_ASYNC)

        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)

    sck.close()
    window.destroy()


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        # User's sent message
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)


def send_mssage_to_server(msg):
    client_msg = str(msg)
    client.send(client_msg.encode())
    if msg == "exit":
        client.close()
        window.destroy()
    print("Sending message")


window.mainloop()
