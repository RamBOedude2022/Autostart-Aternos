import asyncio
import json
import tkinter as tk
from typing import Dict, Tuple

from bs4 import BeautifulSoup
from pyppeteer import launch

from account import Account
from gui import ErrorPopup, ServerPopup


def retrieve_account() -> Tuple[str, str]:
    """
    Retrieve an account.
    :return: The username and password of the account.
    """

    account = Account()
    account.login()

    return account.username, account.password


class Browser:
    def __init__(self) -> None:
        """
        This function retrieves the username and password from the user's account.
        """
        self.username, self.password = retrieve_account()

    async def create_account(self) -> bool:
        """
        It creates an account on aternos.org.
        :return: the value of the variable "data"
        """
        # Open file that contains login credentials
        with open("login.json", "r") as read:
            data: Dict = json.load(read)

            if data.get("created"):
                return True

        # Checks if credentials were generated
        if data.get("premade", False) is True:
            while True:

                # Redirects to signup page to create account
                await self.page.reload()
                await self.page.goto("https://aternos.org/signup/")

                await self.page.type("#user", data["username"])

                accept_terms = "body > div.go-wrapper > div > div > div.create-server > div.signup-account > div.legal-toggle.accept-terms > div.toggle.toggle-inverted > label"
                privacy_consent = "body > div.go-wrapper > div > div > div.create-server > div.signup-account > div.legal-toggle.prvcy-cnsnt > div.toggle.toggle-inverted > label"

                # Checks agreement of ToS and privacy consent

                await self.page.click(accept_terms)
                await self.page.click(privacy_consent)
                await self.page.click("#create-next")

                # Waits for password fields to be present
                while True:
                    input_pass = await self.page.querySelectorAll("#password")
                    input_pass_retype = await self.page.querySelectorAll(
                        "#password-retype"
                    )

                    # Ends loop when both password fields are present/accessible
                    if input_pass and input_pass_retype:
                        break

                # Inputs password in both password fields
                await self.page.type("#password", data["password"])
                await self.page.type("#password-retype", data["password"])
                await self.page.click("#signup")

                # Waits for redirection before continuing
                await self.page.waitForNavigation()

                data["created"] = True
                with open("login.json", "w") as write:
                    json.dump(data, write, indent=4)
                    return True

        return False

    async def attempt_login(self) -> bool:
        """
        It attempts to login to the website, and if it fails, it reloads the page and tries again.
        If login fails after second attempt then program ends.
        :return: The return value is a boolean.
        """

        await self.page.goto(url="https://aternos.org/create")
        if self.page.url != "https://aternos.org/create":

            await self.page.type("#user", self.username)
            await self.page.type("#password", self.password)
            await self.page.click("#login")

            await asyncio.sleep(2)

        login_failed_icon = (
            "body > div.go-wrapper > div > div > div.login > div.login-error > i"
        )
        login_failed = await self.page.querySelector(login_failed_icon)
        if login_failed:
            return False

        return False if self.page.url == "https://aternos.org/go" else True

    async def open_server(self) -> None:
        """
        Attempts to create a server, otherwise opens existing server.
        :return: Nothing
        """

        try:

            await self.page.click("#create-server")

        except:

            existing_server = "body > div > main > section > div.page-content.page-servers > div.servers.single > div > div.server-body"

            await self.page.goto(
                url="https://aternos.org/server", waitUntil="domcontentloaded"
            )
            await self.page.click(existing_server)

        return

    async def keep_alive(self):
        """
        It checks if the server is online, if it is, it will display a popup with the IP and version of
        the server. If the server is offline, it will check if the server is in a queue, if it is, it
        will wait until the server is out of the queue. If the server is offline and not in a queue, it
        will restart the server.
        """

        ip_popup = False  # Popup to notify of server IP/version when online
        while True:
            await asyncio.sleep(5)

            tos_button = "#read-our-tos > main > div > div > div > main > div > div > a.btn.btn-green"
            # Agrees to term of service when server starts up
            tos_agreement = await self.page.querySelector(tos_button)
            if tos_agreement and await tos_agreement.isIntersectingViewport():
                await tos_agreement.click()

            notify_button = "#read-our-tos > main > div > div > div > main > div > div > a.btn.btn-green"
            # Selects an option when asked for in-site notifications
            notify_prompt = await self.page.querySelector(notify_button)
            if notify_prompt and await notify_prompt.isIntersectingViewport():
                await self.page.reload()

            # Retrieves html of the website
            content = await self.page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Gets current status of the server
            server_status = soup.find("span", class_="statuslabel-label")
            self.status = server_status.text.strip()

            # Starts server if offline
            if self.status.lower() == "offline":
                try:
                    await self.page.click("#start")
                except Exception:
                    pass

                continue

            # Retrieves the countdown timer while server is active
            offline_countdown = soup.find(
                "span", class_="server-status-label-left queue-time hidden"
            ) or soup.find("span", class_="server-status-label-left queue-time")

            # Retrieves the server IP
            server_ip = soup.find("span", id="ip")
            self.ip = server_ip.text

            # Retrieves the current server version
            server_version = soup.find("span", id="version")

            # Checks if user has been notified and show popup if not
            if self.status.lower() == "online" and ip_popup is False:
                ip_popup = True

                popup = tk.Tk()
                prompt = ServerPopup(popup, self.ip, server_version.text)
                prompt.run()

            # Monitors countdown timer to keep server active
            if offline_countdown and offline_countdown.text:
                mins, secs = offline_countdown.text.split(":")
                seconds = int(mins) * 60 + int(secs)

                # Restarts server instance if 30 seconds remaining from shutdown
                if seconds <= 30:
                    await self.page.click("#restart")

    async def open_browser(self) -> None:
        """
        It opens a browser, creates an account, logs in, opens a server, and keeps it alive.
        :return: Nothing
        """

        # Creates instance of Chromium browser
        self.browser = await launch(
            args=[
                "--mute-audio",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            ],
            headless=True,
            slowMo=15,
            defaultViewport={"height": 1080, "width": 1920},
        )

        # Retrieves open tab and redirects to website
        pages = await self.browser.pages()
        self.page = pages[0]
        await self.page.goto("https://aternos.org/go")

        await self.create_account()

        logged_in = await self.attempt_login()

        # Display error popup due to login failure and end program
        if logged_in is False:

            await self.browser.close()
            popup = tk.Tk()
            prompt = ErrorPopup(popup)
            prompt.run()

            return

        await self.open_server()
        await self.keep_alive()


browser = Browser()
asyncio.run(browser.open_browser())
