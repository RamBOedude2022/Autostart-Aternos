import json
import os
import tkinter as tk
from typing import Dict, Union

from gui import Interface


class Account:
    def __init__(self, username: str = None, password: str = None) -> None:
        """
        This function takes in a username and password and sets the username and password to the
        username and password that was passed in

        :param username: The username of the account you want to log in with
        :type username: str
        :param password: The password for the user
        :type password: str
        """
        self.username = username
        self.password = password

    def login(self) -> None:
        """
        If the user has already logged in, do nothing. Otherwise, create a new window and run the
        Interface class.
        :return: The username, password, and premade are being returned.
        """

        # Checks if login.json exists or not
        if self.existing_login():
            return

        # Creates prompt to enter credentials
        root = tk.Tk()
        app = Interface(root)
        app.run()

        self.username = app.username
        self.password = app.password
        self.premade = app.premade

        return

    def existing_login(self) -> Union[bool, None]:
        """
        If there is a login.json file in the current directory, then open it and assign the username and
        password to the variables self.username and self.password.
        :return: True
        """

        # Checks for login.json location
        if "login.json" in os.listdir("./"):
            self.exists = os.getcwd() + "\login.json"

        else:
            self.exists = None

        # Updates login.json with inputted credentials
        if self.exists:
            with open(self.exists) as file:
                data: Dict = json.load(file)

                self.username = data["username"]
                self.password = data["password"]

            return True

        return
