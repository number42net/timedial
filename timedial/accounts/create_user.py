"""TimeDial project.

Copyright (c) Martin Miedema
Repository: https://github.com/number42net/timedial

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import getpass
import os
import pwd
import smtplib
import time
from email.message import EmailMessage

import bcrypt

from timedial.accounts import account

SSH = any(var in os.environ for var in ["SSH_CONNECTION", "SSH_CLIENT", "SSH_TTY"])

WELCOME = (
    "Welcome to TimeDial.org\n\n"
    "You're now connected to a public service that offers access to classic computer "
    "systems, retro games, shell environments, and a window into computing history. "
    "Whether you're here to explore, learn, or just have fun - we're glad you're dialing in.\n\n"
    "Please follow these guidelines:\n"
    "+ Be respectful to others\n"
    "+ Don't break stuff that isn't yours\n"
    "+ Ask questions, share knowledge, enjoy the ride\n\n"
    "This is a shared space - treat it like your favorite old machine: with curiosity and care.\n\n"
    "Happy hacking!\n"
)


def create_user() -> None:
    """Interactively create a new user account for the TimeDial system.

    This function prompts the administrator to input details for a new user,
    including a username, password (with confirmation), optional real name,
    optional email address, and an optional SSH public key if run in an SSH session.

    The function performs validation to ensure:
    - The username contains only alphanumeric characters.
    - The username does not already exist in the account database.
    - The password and its confirmation match.

    Once all inputs are collected and validated:
    - The password is securely hashed using SHA-512.
    - A UserModel instance is created and saved using `account.write()`.
    - The function waits for the system user to be recognized via `pwd.getpwnam()`.

    On successful creation, the user is notified and prompted to log in.

    Raises:
        None directly, but will print error messages for input validation failures.

    """
    print()
    # Username
    username = ""
    while not username:
        username = input("New username (a-z / 0-9 only): ").strip()
        if username == "root":
            print("Haha, nice try...")
            exit(1)

        if not account.validate_username(username):
            print("Error: Username must contain only letters and numbers.\n")
            username = ""
        try:
            account.read(username)
            print("Error, username already exists\n")
        except FileNotFoundError:
            # User doesn't exist, so we can continue
            break

    # Real name:
    realname: str | None = input("Realname (optional): ").strip()
    if not realname:
        realname = None

    # Password
    password = ""
    while not password:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm Password: ")
        if password != confirm:
            print("Error: Passwords do not match.\n")
            password = ""

    # Email
    email: str | None = input("Email address (optional): ").strip()
    if not email:
        email = None

    # Pubkeys
    pubkeys: list[str] = []
    if SSH:
        key = input("Public SSH key (optional): ").strip()
        if key:
            pubkeys.append(key)

    # Put it all together:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    model = account.UserModel(
        username=username,
        password_hash=hashed.decode("utf-8"),
        email=email,
        pubkeys=pubkeys,
        realname=realname,
    )
    model.write()

    time.sleep(1)
    while True:
        try:
            pwd.getpwnam(username)
            break
        except KeyError:
            print("Waiting for user to be created, this should only take a few seconds...")
            time.sleep(5)

    msg = EmailMessage()
    msg.set_content(WELCOME)
    msg["Subject"] = "Welcome to timedial"
    msg["From"] = "toor@timedial.org"
    msg["To"] = username
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)

    print()
    print(f"Your new user is ready for use. You'll be logged out and can log back in with: {username}")
    print()
