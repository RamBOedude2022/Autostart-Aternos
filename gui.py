import json
import os
import tkinter as tk
import uuid
from tkinter import ttk


def edit_window(app: tk.Tk) -> None:
    """
    It brings the window to the front and changes icon

    :param app: tk.Tk()
    :type app: tk.Tk
    """
    app.attributes("-topmost", True)
    app.attributes("-topmost", False)

    # app.iconbitmap("./assets/icon.ico")


class Interface:
    def __init__(self, master: tk.Tk) -> None:
        """
        This function is used to set the title of the window, and the size of the window.

        :param master: tk.Tk = The window that the class is being called from
        :type master: tk.Tk
        """
        self.master = master
        self.master.title("Aternos | Login Info")
        self.master.resizable(width=False, height=False)
        self.master.minsize(width=250, height=100)

    def create_labels(self) -> None:
        """
        It creates the labels and entry boxes for the user to input their login info.
        """
        user_label = tk.Label(self.master, text="Username: ")
        pass_label = tk.Label(self.master, text="Password: ")

        user_label.grid(row=0)
        pass_label.grid(row=1)

        self.username = tk.Entry(self.master)
        self.password = tk.Entry(self.master)

        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)

        self.submit = ttk.Button(self.master, text="Submit", command=self.create_login)

        self.submit.grid(row=2, column=1)

        disclaimer = tk.Label(
            self.master,
            text="Important: If using own login info, disable 2FA.\nNot inputting any info will create an account for you.",
        )
        disclaimer.grid(row=3, column=1)

    def create_login(self) -> None:
        """
        If the username and password are not at least 4 and 6 characters long, respectively, then the
        function will create a random username and password and save it to a json file
        """

        # Generates a uuid string
        auto_creds = str(uuid.uuid4()).replace("-", "")

        # Checks if input is invalid to generate credentials
        premade = (
            True
            if not (
                (self.username.get() and len(self.username.get()) >= 4)
                and (self.password.get() and len(self.password.get()) >= 6)
            )
            else False
        )

        # Randomly generate username
        username: str = (
            self.username.get()
            if len(self.username.get()) >= 4
            else auto_creds[: (len(auto_creds) // 2)]
        )

        # Randomly generate password
        password: str = (
            self.password.get()
            if len(self.password.get()) >= 6
            else auto_creds[(len(auto_creds) // 2) :]
        )

        # Store data in a dictionary
        data = {
            "username": username,
            "password": password,
            "premade": premade,
        }

        # Make data accessible elsewhere
        self.username: str = data["username"]
        self.password: str = data["password"]
        self.premade: bool = premade

        # Update login.json and close prompt
        with open("login.json", "w") as output:
            json.dump(data, output, indent=4)

        self.master.destroy()

    def run(self) -> None:
        """
        It creates the labels and then runs the mainloop
        """
        self.create_labels()

        edit_window(self.master)
        self.master.mainloop()


class ErrorPopup:
    def __init__(self, master: tk.Tk) -> None:
        """
        This function creates a window with a title, a minimum size, and a non-resizable window.

        :param master: tk.Tk = The master window
        :type master: tk.Tk
        """
        self.master = master
        self.master.title("Aternos | Login Failure")
        self.master.resizable(width=False, height=False)
        self.master.minsize(width=250, height=100)

    def create_prompt(self) -> None:
        """
        If the login attempt fails, display a label that says "Login attempt failed. Please try again."
        and a button that says "Exit" that will exit the program.
        """
        failure_label = tk.Label(
            self.master, text="Login attempt failed. Please try again."
        )
        failure_label.grid(row=1, column=1)

        self.submit = ttk.Button(self.master, text="Exit", command=self.reset)
        self.submit.grid(row=2, column=1)

    def reset(self) -> None:
        """
        It removes the login.json file and destroys the master window
        """

        # Remove login.json due to login failure
        os.remove("login.json")
        self.master.destroy()

    def run(self) -> None:
        """
        It creates a prompt for the user to enter a command
        """
        self.create_prompt()

        edit_window(self.master)
        self.master.mainloop()


class ServerPopup:
    def __init__(self, master: tk.Tk, ip: str, version: str) -> None:
        """
        This function is used to set the title of the window, and the size of the window.

        :param master: tk.Tk = The window that the widget is in
        :type master: tk.Tk
        :param ip: The IP of the server
        :type ip: str
        :param version: The version of the program
        :type version: str
        """
        self.master = master
        self.ip = ip
        self.version = version

        self.master.title("Aternos | Server IP")
        self.master.resizable(width=False, height=False)
        self.master.minsize(width=250, height=100)

    def create_prompt(self) -> None:
        """
        It creates a prompt that displays the server's IP address and version, and then copies the IP
        address to the clipboard
        """
        ip_label = tk.Label(self.master, text=f"Server IP: {self.ip}")
        ip_label.grid(row=1, column=1)

        version_label = tk.Label(self.master, text=f"Server Version: {self.version}")
        version_label.grid(row=2, column=1)

        clipboard_label = tk.Label(self.master, text="IP has been copied to clipboard.")
        clipboard_label.grid(row=3, column=1)

        # Clears clipboard and updates with server IP
        self.master.clipboard_clear()
        self.master.clipboard_append(self.ip)
        self.master.update()

        self.exit = ttk.Button(self.master, text="Exit", command=self.master.destroy)
        self.exit.grid(row=4, column=1)

    def run(self) -> None:
        """
        It creates a prompt with the server information.
        """
        self.create_prompt()

        edit_window(self.master)
        self.master.mainloop()
