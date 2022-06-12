import socket
import time
import pandas as pd
import logging
from datetime import datetime

# basic data
server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'smarz'
token = 'put token here'
channel = '#atrioc'
df = pd.DataFrame
done = False
data = []

# get current time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# start the logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('chat.txt', encoding='utf-8')])


# initialize the socket and connect to the IRC
sock = socket.socket()
sock.connect((server, port))

# connect to the server by sending the user and password
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))

# connect to the server
sock.send(f"JOIN {channel}\n".encode('utf-8'))


def find_username(resp):
    """ this separates the username from the garbage were given """
    x = 0
    for i in resp:
        x += 1
        if i == "!":
            username = resp[:x-1]
            break

    return username[1:]


def find_message(resp):
    """ gets the message the person sent"""
    location = resp.find(channel)

    no_front = resp[location + len(channel):]
    end = no_front.find('\r\n')

    trimed_message = no_front[:end]
    return trimed_message[1:]


def return_data(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n\n\n')

        for line in lines:
            try:

                d = {
                    'dt': current_time,
                    'channel': channel,
                    'username': username,
                    'message': message
                }

                data.append(d)

            except Exception:
                pass

    return pd.DataFrame().from_records(data)


# main event loop to get the data

for i in range(50):
    # receive a response from the server and sleep to avoid rate-limit
    # we can make this faster if I do math lul
    resp = sock.recv(2048).decode('utf-8')
    time.sleep(2)

    # find the username then the password from our response
    username = find_username(resp)
    message = find_message(resp)

    # create the dataframe from our data and show shape just in case
    df = return_data("chat.log")
    print(df.shape)


# at the end, save the data to a csv
df.to_csv('raw messages.csv', encoding='utf-8')
