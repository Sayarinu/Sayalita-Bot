import discord
import asyncio
from discord.ext import commands


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

# Reads in the token for the bot hidden in a different file for specific reasons
with open('Bot/Scripts/token.txt', 'r') as file:
    token = file.read()

# Gathers intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Command prefix is set to ! and intents are read in
bot = commands.Bot(command_prefix='!', intents=intents)

# Posts to a channel when joining for debugging
@bot.event
async def on_ready():
    # when initialized gets a list of all channels and stores their ids
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channels.append(channel.id)
        for channel in guild.voice_channels:
            voice_channels.append(channel.id)

    channel = bot.get_channel(text_channels[0])
    await channel.send(f'Logged in as {bot.user.name}')
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channels.append(channel.id)

    initialize_users()
    bot.loop.create_task(every_minute())

async def every_minute():
    while True:
        await asyncio.sleep(60)  # Wait for 1 minute
        update_points()

# Checks if someone joins the call, if they leave the call or if they start or stop streaming
@bot.event
async def on_voice_state_update(member, before, after):
    channel = bot.get_channel(text_channels[0])
    user = member.id
    # User either started or stopped streaming
    if before.channel is not None and after.channel is not None and before.self_stream != after.self_stream:
        if user not in streaming:
            streaming[user] = before.channel.id
            await channel.send(f'{member.name} is now streaming in {after.channel.name}')
        else:
            streaming.pop(user)
            await channel.send(f'{member.name} stopped streaming in {after.channel.name}')

    if before.channel is None and after.channel is not None:
        # Member joined a channel
        await channel.send(f'{member.name} joined {after.channel.name}')
        if after.channel.id not in viewers:
            viewers[after.channel.id] = []
            viewers[after.channel.id].append(user)
        else:
            viewers[after.channel.id].append(user)
        if user not in points:
            points[user] = {}

    if before.channel is not None and after.channel is None:
        # Member left a channel
        await channel.send(f'{member.name} left {before.channel.name}')
        viewers[before.channel.id].remove(user)
        if user in streaming:
            streaming.pop(user)

def initialize_users():
    for i in range(len(voice_channels)):
        channel = bot.get_channel(voice_channels[i])
        members = channel.members
        member_names = [member.id for member in members]
        member_voices = [member.voice for member in members]
        for i in range(len(member_names)):
            points[member_names[i]] = {}
        viewers[channel.id] = member_names
        for i in range(len(member_voices)):
            if member_voices[i].self_stream:
                streaming[member_names[i]] = channel.id



# Gets all of the people streaming in the given channel
def update_points():
    for streamer in streaming: # streamer is the name of the streamer ; streaming[streamer] is the channel
        for view in range(len(viewers[streaming[streamer]])):
            if viewers[streaming[streamer]][view] != streamer: # use the viewer and compares if they are the one streaming
                if streamer not in points[viewers[streaming[streamer]][view]]:
                    points[viewers[streaming[streamer]][view]][streamer] = 50 # Initially get 50 and then get 10 after
                else:
                    points[viewers[streaming[streamer]][view]][streamer] += 10

    print(points)

# Runs the bot with the token
bot.run(token)
