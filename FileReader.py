import json

from colorama import Fore, Back, Style, init
from datetime import datetime as dt
# Initialize colorama
init(autoreset=True)
points_file = "points.json"

# Converts keys to integers (used for IDs from reading in from file)
def convertKeysToInt(diction) -> dict:
    converted_dict = {}

    for key, value in diction.items():
        new_key = int(key.strip("'"))
        if isinstance(value, dict):
            value = convertKeysToInt(value)
        converted_dict[new_key] = value

    return converted_dict

# Reads in our API Keys, stopUser and ChannelID from a text file
def read_files() -> list:
    # Reads in the token for the bot hidden in a different file for specific reasons
    with open('token.txt', 'r') as file:
        token = file.read()
    file.close()
    print(f'{Fore.BLUE}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Token Read')
    with open('stop.txt', 'r') as file:
        stopUser = int(file.read())
    file.close()
    print(f'{Fore.BLUE}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Stop User Read')
    with open('notifications_channel.txt', 'r') as file:
        notifications_channel = int(file.read())
    file.close()
    print(f'{Fore.BLUE}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Notifications Channel Read')
    return [token, stopUser, notifications_channel]

# Initializes the points when reading in from the file
def initialize(name) -> dict:
    # Read the dictionary from the file
    with open(points_file, "r") as file:
        data = json.load(file)
    file.close()
    data = convertKeysToInt(data)
    print(f'{Fore.RED}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Initialized Channel Points')
    return data

# Saves the points to the file
def savePoints(points: dict) -> None:
    with open(points_file, "w") as file:
        file.truncate()
        json.dump(points, file)
    file.close()