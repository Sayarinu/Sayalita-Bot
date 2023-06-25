import discord
import asyncio
import json
import os

from Classes import Wagers
from discord.ext import commands

points_file = "points.json"
wagers_file = "wagers.json"

# Stores a dictionary of the user's who are streaming and the
streaming = {}
# Stores the list of viewers in each of the channels
viewers = {}
# Stores the list of text channels in the server
text_channels = []
# Stores the list of voice channels in the server
voice_channels = []
# Stores the points of each streamer
points = {}
# Stores the wagers for each streamer
wagers = {}

# Reads in the token for the bot hidden in a different file for specific reasons
with open('Bot/Scripts/token.txt', 'r') as file:
    token = file.read()
file.close()

# Gathers intents
intents = discord.Intents.all()

# Command prefix is set to ! and intents are read in
bot = commands.Bot(command_prefix='!', intents=intents)

# Posts to a channel when joining for debugging
@bot.event
async def on_ready():
    global points
    global wagers
    if os.path.getsize(points_file) != 0:
        points = initialize(points_file)
    if os.path.getsize(wagers_file) != 0:
        wagers = initialize(wagers_file)
    # when initialized gets a list of all channels and stores their ids
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channels.append(channel.id)
        for channel in guild.voice_channels:
            voice_channels.append(channel.id)

    channel = bot.get_channel(text_channels[0])
    # await channel.send(f'Logged in as {bot.user.name}')
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channels.append(channel.id)

    initialize_users()
    bot.loop.create_task(every_minute())
    print(points)

# Checks if someone joins the call, if they leave the call or if they start or stop streaming
@bot.event
async def on_voice_state_update(member, before, after):
    channel = bot.get_channel(text_channels[0])
    user = member.id
    # User either started or stopped streaming
    if before.channel is not None and after.channel is not None and before.self_stream != after.self_stream:
        if user not in streaming:
            streaming[user] = before.channel.id
            # await channel.send(f'{member.name} is now streaming in {after.channel.name}')
        else:
            streaming.pop(user)
            # await channel.send(f'{member.name} stopped streaming in {after.channel.name}')

    if before.channel is None and after.channel is not None:
        # Member joined a channel
        # await channel.send(f'{member.name} joined {after.channel.name}')
        if after.channel.id not in viewers:
            viewers[after.channel.id] = []
            viewers[after.channel.id].append(user)
        else:
            viewers[after.channel.id].append(user)
        if user not in points:
            points[user] = {}

    if before.channel is not None and after.channel is None:
        # Member left a channel
        # await channel.send(f'{member.name} left {before.channel.name}')
        viewers[before.channel.id].remove(user)
        if user in streaming:
            streaming.pop(user)

# Bot Commands
@bot.command()
async def wager(ctx, amount: int, user_handle: str): # !wager [int] [user_handle]
    if amount <= 0:
        raise commands.CommandError("Amount must be an integer greater than 0.")

    author = ctx.author
    user = get_user(user_handle)
    if isinstance(user, discord.user.User):
        if author.id == user.id:
            raise commands.CommandError("Cannot call wager on self.")

        if points[caller][member.id] < amount:
            raise commands.CommandError(f'Amount exceeds points you have for {user.global_name}')

@bot.command()
async def wagerStart(ctx, streamer: str, desc: str, one: str, two: str): # !wagerStart "Desc" "One" "Two"
    global wagers
    user = get_user(streamer)

    if user.id not in wagers:
        wagers[user.id] = {}

    newWager = Wagers(desc, len(wagers[user.id]), one, two, user.id)
    wagers[len(wagers[user.id])] = newWager

    print(wagers)


@bot.command()
async def balance(ctx, user_handle: str):
    author = ctx.author
    user = get_user(user_handle)
    if isinstance(user, discord.user.User):
        if user.id in points[author.id]:
            response = f'{author.global_name} have {points[author.id][user.id]} for {user.global_name}'
        elif user.id is author.id:
            response = "Cannot have points for yourself"
        else:
            response = f'You have no points for {user_handle}'
        await ctx.send(response)
    else:
        await ctx.send("User not found")

@bot.command()
async def save(ctx):
    save_points()

@wager.error
async def wager_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(str(error))

def initialize_users():
    '''
    Goes through all of the voice channels in the servers it is connected to and will then
    initialize all of the fields, called when the bot runs
    '''
    for i in range(len(voice_channels)):
        channel = bot.get_channel(voice_channels[i])
        members = channel.members
        member_names = [member.id for member in members]
        member_voices = [member.voice for member in members]

        if os.path.getsize(points_file) == 0:
            for j in range(len(member_names)):
                points[member_names[j]] = {}

        viewers[channel.id] = member_names
        for j in range(len(member_voices)):
            if member_voices[j].self_stream:
                streaming[member_names[j]] = channel.id

# Gets all of the people streaming in the given channel
def update_points():
    for streamer in streaming: # streamer is the name of the streamer ; streaming[streamer] is the channel
        for view in range(len(viewers[streaming[streamer]])):
            if viewers[streaming[streamer]][view] != streamer: # use the viewer and compares if they are the one streaming
                if streamer not in points[viewers[streaming[streamer]][view]]:
                    points[viewers[streaming[streamer]][view]][streamer] = 50 # Initially get 50 and then get 10 after
                else:
                    points[viewers[streaming[streamer]][view]][streamer] += 10

    save_points()
    print(points)

# Initializes the points when reading in from the file
def initialize(name):
    # Read the dictionary from the file
    with open(points_file, "r") as file:
        data = json.load(file)
    file.close()
    data = convert_keys_to_int(data)

    return data

# Converts keys to integers (used for IDs from reading in from file)
def convert_keys_to_int(diction):
    converted_dict = {}

    for key, value in diction.items():
        new_key = int(key.strip("'"))
        if isinstance(value, dict):
            value = convert_keys_to_int(value)
        converted_dict[new_key] = value

    return converted_dict

# Saves the points to the file
def save_points():
    with open(points_file, "w") as file:
        file.truncate()
        json.dump(points, file)
    file.close()

# Gets a user object from handle
def get_user(handle):
    user = discord.utils.get(bot.users, name=handle)
    if not isinstance(user, discord.user.User):
        name, discriminator = handle.split("#")
        user = discord.utils.get(bot.users, name=name, discriminator=discriminator)
    return user

# Called every minute
async def every_minute():
    while True:
        await asyncio.sleep(60)  # Wait for 1 minute
        update_points()

# Runs the bot with the token
bot.run(token)