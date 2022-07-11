import socket
import time
import pandas as pd
import logging
from datetime import datetime
from tqdm import tqdm
import os

clear = lambda: os.system("cls")

# basic data
server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'my_wicked_bot'
done_scraping = False
df = pd.DataFrame()
first_run = True
done = False
data = []
conter = 0
token, channel, points, csv_name, ready = "", "", "", "", ""
username, message = "", ""
sock = socket.socket()
# get current time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# start the logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('chat.log', encoding='utf-8')])


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


def find_message(resp):
    """ gets the message the person sent"""
    location = resp.find(channel)

    no_front = resp[location + len(channel):]
    end = no_front.find('\r\n')

    trimed_message = no_front[:end]
    return trimed_message[2:]


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

while not done:
    #
    token = input("token: ")
    channel = input("channel: ")
    points = int(input("points: "))
    csv_name = input("csv name: ")
    clear()
    while not ready == "ready":

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
                            4. name of csv:{csv_name}.csv
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

    sock.connect((server, port))

    # connect to the server by sending the user and password
    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

    for i in tqdm(range(points + 2)):
        time.sleep(0.1)

        resp = sock.recv(2048).decode("utf-8", "ignore")

        # check if the message received is the ping response. if it is reply
        if resp[:4] == "PING":
            sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))

        username = find_username(resp)
        message = find_message(resp)

        if username == "" or username is None:
            print("a connection error has occurred. disconnecting and reconnecting...")
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            time.sleep(30)
            sock.connect((server, port))
            sock.send(f"PASS {token}\n".encode('utf-8'))
            sock.send(f"NICK {nickname}\n".encode('utf-8'))
            sock.send(f"JOIN {channel}\n".encode('utf-8'))
            time.sleep(1)

        if conter > 2:
            df = return_data("chat.log")


    done_scraping = True



    csv_name += ".csv"
    if done_scraping:
        df.to_csv(csv_name, encoding='utf-8')
        done = True
sock.close()
print("done")

# add a random message to the front page # gonna kill myself trying to add this
