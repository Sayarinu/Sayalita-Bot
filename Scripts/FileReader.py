import json
import pickle
import os
from dotenv import load_dotenv

from colorama import Fore, Back, Style, init
from datetime import datetime as dt
# Initialize colorama
init(autoreset=True)

load_dotenv()

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
  token = os.getenv("TOKEN")
  print(f'{Fore.BLUE}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Token Read')
  stopUser = int(os.getenv("STOP"))
  print(f'{Fore.MAGENTA}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Stop User Read')
  notifications_channel = int(os.getenv("NOTIFICATIONS"))
  print(f'{Fore.GREEN}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Notifications Channel Read')
  riotAPIKey = os.getenv("RIOT_TOKEN")
  print(f'{Fore.CYAN}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Riot API Key Read')
  gameName = os.getenv("RIOT_GAMENAME")
  gameTag = os.getenv("RIOT_GAMETAG")
  print(f'{Fore.YELLOW}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Riot Account Loaded: {gameName}#{gameTag}')
  
  return [token, stopUser, notifications_channel, riotAPIKey, gameName, gameTag]

# Initializes the points when reading in from the file
def initialize() -> dict:
  # Read the dictionary from the file
  with open("../TextFiles/points.json", "r") as file:
    points = json.load(file)
  file.close()
  points = convertKeysToInt(points)
  print(f'{Fore.RED}[LOG {dt.now().strftime("%Y-%m-%d %H:%M:%S")}]: Initialized Channel Points')
  
  return points

# Saves the points to the file
def save(points: dict) -> None:
  with open("../TextFiles/points.json", "w") as file:
    file.truncate()
    json.dump(points, file)
  file.close()