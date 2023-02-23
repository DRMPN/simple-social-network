import logging
import sys

import requests

from src.helpers import random_gen

logging.basicConfig(level=logging.INFO)

if len(sys.argv) != 4:
    print("usage: checker.py [ip] [port] [command]")
    exit(1)

IP = sys.argv[1]
PORT = sys.argv[2]
COMMAND = sys.argv[3]

URL = f"http://{IP}:{PORT}/"

logging.info(f"Recieved: IP - {IP}; PORT - {PORT}; COMMAND - {COMMAND}; URL - {URL}")

session = requests.Session()
respone = session.get(URL)

if COMMAND == "check":

    username_1 = random_gen()
    password_1 = random_gen()
    message_1 = random_gen(50)
    username_2 = random_gen()
    password_2 = random_gen()

    respone = session.post(
        URL + "register",
        data=dict(
            username=username_1,
            password=password_1,
            confirmation=password_1,
        ),
    )
    if "Apology" in respone.text:
        print("ERROR: cannot register 1")
        exit(102)
    logging.info("Registered 1")

    respone = session.post(
        URL + "register",
        data=dict(
            username=username_2,
            password=password_2,
            confirmation=password_2,
        ),
    )
    if "Apology" in respone.text:
        print("ERROR: cannot register 2")
        exit(102)
    logging.info("Registered 2")

    respone = session.post(
        URL + "login", data=dict(username=username_1, password=password_1)
    )
    if "Apology" in respone.text:
        print("ERROR: cannot log in 1")
        exit(102)
    logging.info("Login 1")

    respone = session.post(
        URL + "message", data=dict(username=username_2, text=message_1)
    )
    if "Apology" in respone.text:
        print("ERROR: cannot send message 1")
        exit(102)
    logging.info("1 send message to 2")

    respone = session.get(URL + "logout")
    if "Apology" in respone.text:
        print("ERROR: cannot log out 1")
        exit(102)
    logging.info("Logout 1")

    respone = session.post(
        URL + "login", data=dict(username=username_2, password=password_2)
    )
    if "Apology" in respone.text:
        print("ERROR: cannot log in 2")
        exit(102)
    logging.info("Login 2")

    respone = session.get(URL + "history")
    if message_1 not in respone.text:
        print("ERROR: cannot get sent message")
        exit(102)
    logging.info("Message from 1 recieved")

    logging.info("Check complete!")
    print("OK")
    exit(101)
