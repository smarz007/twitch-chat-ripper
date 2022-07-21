import os
import socket
import time
from datetime import datetime

import pandas as pd
from tqdm import tqdm

# basic data
# server info
server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'chat_scrapper'

done_scraping = False
done = False
counter = 0
token, channel, points, csv_name, ready = "", "", "", "", ""
username, message = "", ""
users = []
messages = []
times = []

sock = socket.socket()
now = datetime.now()


def clear():
    os.system("cls")


def find_username(resp):
    """ this separates the username from the garbage were given """
    global username
    x = 0
    for i in resp:
        x += 1
        if i == "!":
            username = resp[:x - 1]
            break

    return username[1:]


def connect():
    """connect to the server and authenticate"""
    sock.connect((server, port))
    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))


def find_message(resp):
    """ gets the message the person sent"""
    location = resp.find(channel)

    no_front = resp[location + len(channel):]
    end = no_front.find('\r\n')

    trimmed_message = no_front[:end]
    return trimmed_message[2:]


# main event loop to get the data

while not done:
    #
    token = input("token: ")
    channel = input("channel: ")
    points = int(input("points: "))
    csv_name = input("csv name: ") + ".csv"
    clear()
    while not ready == "ready" or ready == "r":

        print(f"""
                     ▄▄·  ▄ .▄ ▄▄▄· ▄▄▄▄▄    ▄▄▄  ▪   ▄▄▄· ▄▄▄·▄▄▄ .▄▄▄  
                    ▐█ ▌▪██▪▐█▐█ ▀█ •██      ▀▄ █·██ ▐█ ▄█▐█ ▄█▀▄.▀·▀▄ █·
                    ██ ▄▄██▀▐█▄█▀▀█  ▐█.▪    ▐▀▀▄ ▐█· ██▀· ██▀·▐▀▀▪▄▐▀▀▄ 
                    ▐███▌██▌▐▀▐█ ▪▐▌ ▐█▌·    ▐█•█▌▐█▌▐█▪·•▐█▪·•▐█▄▄▌▐█•█▌
                    ·▀▀▀ ▀▀▀ · ▀  ▀  ▀▀▀     .▀  ▀▀▀▀.▀   .▀    ▀▀▀ .▀  ▀
                                                                by smarz

                                    1. token: {token}
                                    ----------------------
                                    2. channel: {channel}
                                    ----------------------
                                    3. data points: {points}
                                    ----------------------
                                    4. name of csv:{csv_name}
                                    ----------------------
                                    type "ready" to start
                                    ----------------------      
        """)

        ready = input("enter number to change or type ready to start: ")

        if ready == "1":
            token = input("token:")
            clear()
        elif ready == "2":
            channel = input("channel:")
            clear()
        elif ready == "3":
            points = int(input("# of points:"))
            clear()
        elif ready == "4":
            csv_name = input("csv name:")

            clear()

    channel = "#" + channel
    # initialize the socket
    connect()

    for i in tqdm(range(points + 2)):
        time.sleep(0.1)
        counter += 1

        # response from twitch chat
        resp = sock.recv(2048).decode("utf-8", "ignore")

        # check if the message received is the ping response.
        if resp[:4] == "PING":
            sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))

        username = find_username(resp)
        message = find_message(resp)
        current_time = now.strftime("%H:%M:%S")

        # this gets rid of the hello message twitch sends at the start
        if counter > 2:
            users.append(username)
            messages.append(message)
            times.append(current_time)
            print(username)

    done_scraping = True

    if done_scraping:
        time_series = pd.Series(times, name="times")
        users_series = pd.Series(users, name="username")
        messages_series = pd.Series(messages, name="message")
        df = pd.concat([time_series, users_series, messages_series], axis=1)

        df.to_csv(csv_name, encoding="utf-8")

        done = True
sock.shutdown(socket.SHUT_RDWR)
sock.close()
print("done")
