import threading
from socket import *
from customtkinter import *


class ChatApp(CTk):
    def __init__(self):
        super().__init__()

        self.title("LogiTalk")
        self.geometry("400x500")
        self.configure(fg_color="#0f1a12")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = CTkFrame(self, height=50, fg_color="#1a2e1f", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")

        self.username_entry = CTkEntry(
            self.header,
            width=120,
            height=28,
            placeholder_text="Нікнейм",
            fg_color="#14231a",
            border_color="#4a7c59",
            text_color="#c8e6c0"
        )
        self.username_entry.insert(0, "Username")
        self.username_entry.pack(side="left", padx=10, pady=10)

        self.chat_display = CTkTextbox(
            self,
            state="disabled",
            fg_color="#14231a",
            text_color="#c8e6c0",
            border_color="#4a7c59",
            border_width=1,
            font=("Trebuchet MS", 13)
        )
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)

        self.input_frame = CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.msg_entry = CTkEntry(
            self.input_frame,
            placeholder_text="Повідомлення...",
            fg_color="#1a2e1f",
            border_color="#4a7c59",
            text_color="#c8e6c0"
        )
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = CTkButton(
            self.input_frame,
            text="➤",
            width=40,
            fg_color="#2d6640",
            hover_color="#3d8a55",
            command=self.send_message
        )
        self.send_btn.grid(row=0, column=1)

        self.username = "Username"
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('5.tcp.eu.ngrok.io', 13440))

            self.username = self.username_entry.get() or "User"
            hello = f"TEXT@{self.username}@{self.username} приєднався(лась)!\n"
            self.sock.send(hello.encode('utf-8'))

            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Система: Помилка підключення {e}")

    def add_message(self, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text + "\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def send_message(self):
        message = self.msg_entry.get()
        self.username = self.username_entry.get() or "User"

        if message:
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode('utf-8'))
                self.add_message(f"Ви: {message}")
                self.msg_entry.delete(0, "end")
            except:
                self.add_message("Система: Помилка відправки")

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096).decode('utf-8')
                if not chunk:
                    break
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    parts = line.split("@", 2)
                    if len(parts) >= 3 and parts[0] == "TEXT":
                        if parts[1] != self.username:
                            self.add_message(f"{parts[1]}: {parts[2]}")
            except:
                break


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()