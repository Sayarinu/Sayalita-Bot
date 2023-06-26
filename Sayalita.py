import discord
import asyncio
import json
import os

from Classes import Wagers
from discord.ext import commands

points_file = "points.json"
wager_count = 0

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
with open('Bot/Scripts/stop.txt', 'r') as file:
    stopUser = int(file.read())
file.close()

# Gathers intents
intents = discord.Intents.all()

# Command prefix is set to ! and intents are read in
bot = commands.Bot(command_prefix='!', intents=intents)

# Posts to a channel when joining for debugging
@bot.event
async def on_ready():
    global points
    if os.path.getsize(points_file) != 0:
        points = initialize(points_file)
    # when initialized gets a list of all channels and stores their ids
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channels.append(channel.id)
        for channel in guild.voice_channels:
            voice_channels.append(channel.id)

    # await channel.send(f'Logged in as {bot.user.name}')
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channels.append(channel.id)

    initializeUsers()
    bot.loop.create_task(everyMinute())
    await bot.change_presence(activity=discord.Game(name='Points Bot \ !commands'))

# Checks if someone joins the call, if they leave the call or if they start or stop streaming
@bot.event
async def on_voice_state_update(member, before, after):
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
async def commands(ctx):
    message = "```* COMMANDS *\n" \
              "!wStart discordHandle \"Description\" \"Outcome 1\" \"Outcome 2\"\n\t(Starts a wager on a streamer)\n" \
              "!wBet discordHandle amount ID outcome\n\t(Lets you place a bet on a streamer)\n" \
              "!wBalance\n\t(lists the balances of all streamers you have points for)\n" \
              "!wEnd ID outcome\n\t(Ends the wager with the given ID)\n\t(1 for outcome 1, 2 for outcome 2, 3 for cancel)\n" \
              "!wList\n\t(Lists all current wagers)" \
              "```"
    await ctx.send(message)


@bot.command()
async def wBet(ctx, user_handle: str, amount: int, wager: int, option: int): # !wager [user_handle] [amount] [wagerID] [option]
    if amount <= 0:
        raise commands.CommandError("Amount must be an integer greater than 0.")

    author = ctx.author
    user = getUser(user_handle)
    if isinstance(user, discord.user.User):
        if author.id == user.id:
            await ctx.send("Cannot call wager on self.")
            return

        if points[author.id][user.id] < amount:
            await ctx.send(f'Amount exceeds points you have for {user.global_name}')
            return

        if option != 1 and option != 2:
            await ctx.send("Invalid side, please choose 1 or 2")
            return

        if wager not in wagers[user.id]:
            await ctx.send("Invalid wagerID, please input correct wager ID")
            return

        if wagers[user.id][wager].timer == 3:
            await ctx.send("The time to place a bet has closed")
            return

        if option == 1:
            if author.id in wagers[user.id][wager].optionTwo:
                await ctx.send("Cannot bet on both sides")
                return
        elif option == 2:
            if author.id in wagers[user.id][wager].optionOne:
                await ctx.send("Cannot bet on both sides")
                return
        wagers[user.id][wager].addWager(author.id, amount, option)
        points[author.id][user.id] -= amount

        if option == 1:
            await ctx.send(f'Wager placed on {user.global_name} for a total of {wagers[user.id][wager].optionOne[author.id]}')
        elif option == 2:
            await ctx.send(f'Wager placed on {user.global_name} for a total of {wagers[user.id][wager].optionTwo[author.id]}')

@bot.command()
async def wEnd(ctx, index: int, outcome: int):
    if len(wagers[ctx.author.id]) == 0:
        await ctx.send("You have no wagers to end")
        return

    elif index not in wagers[ctx.author.id]:
        await ctx.send("Invalid wager ID")
        return

    if outcome == 1 or outcome == 2 or outcome == 3:
        if outcome == 3:
            cancelWager(ctx.author.id, index)
            del wagers[ctx.author.id][index]
            if len(wagers[ctx.author.id]) == 0:
                del wagers[ctx.author.id]
        else:
            winner = payWinners(outcome, ctx.author.id, index)
            if winner[1] != 0:
                name = await bot.fetch_user(winner[1])
                await ctx.send(f'Payouts Complete: {name} had the largest payout with a total of {winner[0]} points!')
            else:
                await ctx.send("Payout Complete")
    else:
        await ctx.send("Invalid outcome, please enter outcome: 1, 2 or 3 for cancel wager")
        return


@bot.command()
async def wStart(ctx, streamer: str, desc: str, one: str, two: str): # !wagerStart "streamer" "Desc" "One" "Two"
    global wagers
    global wager_count
    user = getUser(streamer)

    if user.id not in streaming:
        await ctx.send(f'{user.global_name} is not streaming')
        return

    if user.id not in wagers:
        wagers[user.id] = {}

    if len(wagers[user.id]) > 2:
        await ctx.send("Cannot start another wager for this streamer, please wait for other wagers to close")

    newWager = Wagers(desc, wager_count, one, two, user.id)
    wagers[user.id][wager_count] = newWager

    await ctx.send(f'Wager started:\n{wagers[user.id][wager_count]}')
    wager_count += 1

@bot.command()
async def stopBot(ctx):
    if ctx.author.id == stopUser:
        cancelAllWagers()
        savePoints()
        await bot.close()
    else:
        await ctx.send("Access Denied")

@bot.command()
async def wList(ctx):
    message = ""
    for streamer, wagersList in wagers.items():
        name = await bot.fetch_user(streamer)
        message += f'{name}\'s current wagers\n'
        for streamersWagers, description in wagers[streamer].items():
            message += f'* {description}\n'

    await ctx.send(f'```Ongoing Wagers\n {message}\n```')

@bot.command()
async def wBalance(ctx):
    message = ""
    for streamer, amount in points[ctx.author.id].items():
        name = await bot.fetch_user(streamer)
        message += f' - {name}: {amount}\n'
    await ctx.send(f'# {ctx.author.name}\'s Points\n```{message}\n```')

@bot.command()
async def save(ctx):
    if ctx.author.id == stopUser:
        savePoints()
    else:
        await ctx.send("Access Denied")

def initializeUsers():
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

        else:
            for j in range(len(member_names)):
                if member_names[j] not in points:
                    points[member_names[j]] = {}

        viewers[channel.id] = member_names
        for j in range(len(member_voices)):
            if member_voices[j].self_stream:
                streaming[member_names[j]] = channel.id

# Gets all of the people streaming in the given channel
def updatePoints():
    for streamer in streaming: # streamer is the name of the streamer ; streaming[streamer] is the channel
        for view in range(len(viewers[streaming[streamer]])):
            if viewers[streaming[streamer]][view] != streamer: # use the viewer and compares if they are the one streaming
                if streamer not in points[viewers[streaming[streamer]][view]]:
                    points[viewers[streaming[streamer]][view]][streamer] = 50 # Initially get 50 and then get 10 after
                else:
                    points[viewers[streaming[streamer]][view]][streamer] += 10

    savePoints()

# Initializes the points when reading in from the file
def initialize(name):
    # Read the dictionary from the file
    with open(points_file, "r") as file:
        data = json.load(file)
    file.close()
    data = convertKeysToInt(data)

    return data

def cancelAllWagers(): # Gets called only when turning off the bot
    for streamer, wager in wagers.items():
        for number, bet in wagers[streamer].items():
            cancelWager(streamer, number)

def cancelWager(streamer, number):
    for user, amount in wagers[streamer][number].optionOne.items():
        points[user][streamer] += amount
    for user, amount in wagers[streamer][number].optionTwo.items():
        points[user][streamer] += amount

def payWinners(outcome, streamer, index):
    totalOne, totalTwo = 0, 0
    maxPayout = 0
    maxWinner = 0
    for user, amount in wagers[streamer][index].optionOne.items():
        totalOne += amount
    for user, amount in wagers[streamer][index].optionTwo.items():
        totalTwo += amount
    if outcome == 1:
        if totalOne != 0:
            payout = 1.2
            if totalTwo > .2 * totalOne:
                payout = 1 + totalTwo / totalOne
            for user, amount in wagers[streamer][index].optionOne.items():
                reward = int(payout * amount)
                points[user][streamer] += reward
                if reward > maxPayout:
                    maxPayout = reward
                    maxWinner = user
    else:
        if totalTwo != 0:
            payout = 1.2
            if totalOne > .2 * totalTwo:
                payout = 1 + totalOne / totalTwo
            for user, amount in wagers[streamer][wager].optionTwo.items():
                reward = int(payout * amount)
                points[user][streamer] += reward
                if reward > maxPayout:
                    maxPayout = reward
    del wagers[streamer][index]
    if len(wagers[streamer]) == 0:
        del wagers[streamer]

    return maxPayout, maxWinner

# Converts keys to integers (used for IDs from reading in from file)
def convertKeysToInt(diction):
    converted_dict = {}

    for key, value in diction.items():
        new_key = int(key.strip("'"))
        if isinstance(value, dict):
            value = convertKeysToInt(value)
        converted_dict[new_key] = value

    return converted_dict

# Saves the points to the file
def savePoints():
    with open(points_file, "w") as file:
        file.truncate()
        json.dump(points, file)
    file.close()

# Gets a user object from handle
def getUser(handle):
    user = discord.utils.get(bot.users, name=handle)
    if not isinstance(user, discord.user.User):
        name, discriminator = handle.split("#")
        user = discord.utils.get(bot.users, name=name, discriminator=discriminator)
    return user

def updateWagerTimers():
    for streamer, wager in wagers.items():
        for number, bet in wagers[streamer].items():
            wagers[streamer][number].increaseTimer()

# Called every minute
async def everyMinute():
    while True:
        await asyncio.sleep(60)  # Wait for 1 minute
        updatePoints()
        updateWagerTimers()


# Runs the bot with the token
bot.run(token)