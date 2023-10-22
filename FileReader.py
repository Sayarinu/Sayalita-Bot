import json
import pickle

from colorama import Fore, Back, Style, init
from datetime import datetime as dt
# Initialize colorama
init(autoreset=True)

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
def initialize() -> dict:
    # Read the dictionary from the file
    with open("points.json", "r") as file:
        points = json.load(file)
    file.close()
    points = convertKeysToInt(points)
    print(f'{Fore.RED}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Initialized Channel Points')
    
    return points

# Saves the points to the file
def save(points: dict) -> None:
    with open("points.json", "w") as file:
        file.truncate()
        json.dump(points, file)
    file.close()