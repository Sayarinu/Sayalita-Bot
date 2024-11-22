# Sayalita Bot

Discord Bot that allows you and your friends to make wagers on each other and collect points to use.

Features:

- Channel Points System like twitch
  - Can generate points by being in the same call as your friends
  - Use those points to bet on your friends games
  - Winners on the bet will be get rewarded back points
  - Build up the amount of points you can

Getting Started:

1. Install Python
2. Clone Repository
3. Setup .env in directory
4. Fill out the following .env fields as such:

```dotenv
TOKEN={YOUR BOT TOKEN}
STOP={YOUR DISCORD USER ID}
NOTIFICATIONS={DISCORD DEBUG CHANNEL ID}
RIOT_TOKEN={RIOT API KEY}
RIOT_GAMETAG={RIOT USERNAME}
RIOT_GAMENAME={RIOT TAG}
```

5. Install requirements using the script

```bash
pip install -r requirements.txt
```

6. Maintain File Structure as follows:

```
Sayalita-Bot
├── Scripts/
│ ├── Script Files
├── TextFiles/
│ ├── points.json
```

7. CD into the Scripts directory and run the following command:

```bash
python3 Sayalita.py
```

Coming Soon:

- OP.GG League of Legends interfacing - WIP
  - Allows the win-loss streak for the day to be listed by using a command
  - Will be implemented with the channel points system to automatically update certain bets
