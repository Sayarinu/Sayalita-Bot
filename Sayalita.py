import discord
from discord.ext import commands

# Stores the status of each member (if they are streaming or not)
status = {}
# Stores the list of viewers in each of the channels
viewers = {}
# Stores the list of text channels in the server
channels = []

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
            channels.append(channel.id)

    channel = bot.get_channel(channels[0])
    await channel.send(f'Logged in as {bot.user.name}')
    viewers[channel] = []
    for guild in bot.guilds:
        for channel in guild.text_channels:
            channels.append(channel.id)

# Checks if someone joins the call, if they leave the call or if they start or stop streaming
@bot.event
async def on_voice_state_update(member, before, after):
    channel = bot.get_channel(channels[0])
    if before.channel is None and after.channel is not None:
        # Member joined a channel
        await channel.send(f'{member.name} joined {after.channel.name}')
        viewers[channel].append(member.id)
        status[member.id] = False

    elif before.channel is not None and after.channel is None:
        await channel.send(f'{member.name} left {before.channel.name}')
        viewers[channel].remove(member.id)

    elif before.channel is not None and after.channel is not None and before.self_stream != after.self_stream:
        status[member.id] = not status[member.id]
        if status[member.id]:
            await channel.send(f'{member.name} is now streaming in {after.channel.name}')
        else:
            await channel.send(f'{member.name} stopped streaming in {after.channel.name}')

# Runs the bot with the token
bot.run(token)
