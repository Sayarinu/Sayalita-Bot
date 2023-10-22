import discord
import asyncio
import os
import Classes
import FileReader
import datetime as dt
from colorama import Fore, Back, Style, init

from discord.ext import commands, tasks
# Name of file containing the points
points_file = "points.json"
# Stores the number of wagers that have been created
wager_count = 0

# Initialize colorama
init(autoreset=True)

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
# Stores users reminders
reminders = {}

token, stopUser, notifications_channel = FileReader.read_files()

# Gathers intents
intents = discord.Intents.all()

# Command prefix is set to ! and intents are read in
bot = commands.Bot(command_prefix='!', intents=intents)

# Posts to a channel when joining for debugging
@bot.event
async def on_ready() -> None:
    global points
    if os.path.getsize(points_file) != 0:
        points = FileReader.initialize(points_file)
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
    global token, stopUser, notifications_channel
    bot.loop.create_task(everyMinute())
    await bot.change_presence(activity=discord.Game(name='Points Bot \ !commands'))
    print(f'{Fore.YELLOW}[LOG {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: Sayalita has connected to Discord!')

# Checks if someone joins the call, if they leave the call or if they start or stop streaming
@bot.event
async def on_voice_state_update(member, before, after) -> None:
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
async def commands(ctx) -> None:
    message = "```* COMMANDS *\n" \
              "!wStart discordHandle \"Description\" \"Outcome 1\" \"Outcome 2\"\n\t(Starts a wager on a streamer)\n" \
              "!wBet discordHandle amount ID outcome\n\t(Lets you place a bet on a streamer)\n" \
              "!wBalance\n\t(lists the balances of all streamers you have points for)\n" \
              "!wEnd ID outcome\n\t(Ends the wager with the given ID)\n\t(1 for outcome 1, 2 for outcome 2, 3 for cancel)\n" \
              "!wList\n\t(Lists all current wagers)" \
              "!wPayout discordHandle ID\n\t(Shows the payouts for the streamers bet with the existing ID)" \
              "```"
    await ctx.send(message)


@bot.command()
async def wBet(ctx, user_handle: str, amount: int, wager: int, option: int) -> None: # !wager [user_handle] [amount] [wagerID] [option]
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
async def wEnd(ctx, index: int, outcome: int) -> None:
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
            await ctx.send("The wager has been cancelled and points have been returned")
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
async def wStart(ctx, streamer: str, desc: str, one: str, two: str) -> None: # !wagerStart "streamer" "Desc" "One" "Two"
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

    newWager = Classes.Wagers(desc, wager_count, one, two, user.id)
    wagers[user.id][wager_count] = newWager

    await ctx.send(f'Wager started:\n{wagers[user.id][wager_count]}')
    wager_count += 1

@bot.command()
async def stopBot(ctx) -> None:
    if ctx.author.id == stopUser:
        await ctx.send("Stopping Bot")
        print(f'{Fore.RED}[LOG {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: Cancelling All Wagers')
        cancelAllWagers()
        print(f'{Fore.RED}[LOG {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: Wagers Cancelled\n[LOG {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: Saving Points')
        FileReader.savePoints(points)
        print(f'{Fore.RED}[LOG {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: Points Saved\n[LOG {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: Closing Bot')
        await bot.close()
    else:
        await ctx.send("Access Denied")

@bot.command()
async def wList(ctx) -> None:
    message = ""
    for streamer, wagersList in wagers.items():
        name = await bot.fetch_user(streamer)
        message += f'{name}\'s current wagers\n'
        for streamersWagers, description in wagers[streamer].items():
            message += f'* {description}\n'

    await ctx.send(f'```Ongoing Wagers\n {message}\n```')

@bot.command()
async def wBalance(ctx) -> None:
    message = ""
    for streamer, amount in points[ctx.author.id].items():
        name = await bot.fetch_user(streamer)
        message += f' - {name}: {amount}\n'
    await ctx.send(f'# {ctx.author.name}\'s Points\n```{message}\n```')

@bot.command()
async def wPayout(ctx, streamer: str, index: int) -> None:
    user = getUser(streamer)
    if isinstance(user, discord.user.User):
        if index in wagers[user.id]:
            if wagers[user.id][index].optionOneTotal != 0:
                payoutOne = max(1.2, wagers[user.id][index].optionTwoTotal / wagers[user.id][index].optionOneTotal)
            else:
                payoutOne = 1.2
            if wagers[user.id][index].optionTwoTotal != 0:
                payoutTwo = max(1.2, wagers[user.id][index].optionOneTotal / wagers[user.id][index].optionTwoTotal)
            else:
                payoutTwo = 1.2
            await ctx.send(f'Payouts: (1) - {payoutOne} \ (2) - {payoutTwo}')

@bot.command()
async def sReminder(ctx, message, date_time) -> None:
    try:
        date_time = dt.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        reminder = Classes.Reminder(message, date_time, ctx.author.id)
        if ctx.author.id in reminders:
            reminders[ctx.author.id].append(reminder)
        else:
            reminders[ctx.author.id] = [reminder]
        await ctx.send(f'Reminder set: {message} at {date_time.strftime("%Y-%m-%d %H:%M")}')
    except ValueError:
        await ctx.send('Invalid date and time format. Please use `YYYY-MM-DD HH:MM`.')

@bot.command()
async def sWipe(ctx, amount: int):
    # Check if the user has the "manage_messages" permission
    if ctx.message.author.guild_permissions.manage_messages:
        # Fetch the last `amount+1` messages in the channel (including the command message)
        messages = await ctx.channel.history(limit=amount + 1).flatten()
        # Delete the fetched messages
        await ctx.channel.delete_messages(messages)
        await ctx.send(f'Deleted {amount} messages.')
    else:
        await ctx.send("You don't have permission to manage messages.")

async def check_reminders() -> None:
    current_time = dt.datetime.now()
    for user in reminders:
        for event in reminders[user]:
            if event.is_due():
                channel = bot.get_channel(notifications_channel)
                await channel.send(f'<@{user}> you have the following reminder:\n{event}')
                del event

@bot.command()
async def save(ctx) -> None:
    if ctx.author.id == stopUser:
        FileReader.savePoints(points)
    else:
        await ctx.send("Access Denied")

def initializeUsers() -> None:
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
def updatePoints() -> None:
    for streamer in streaming: # streamer is the name of the streamer ; streaming[streamer] is the channel
        for view in range(len(viewers[streaming[streamer]])):
            if viewers[streaming[streamer]][view] != streamer: # use the viewer and compares if they are the one streaming
                if streamer not in points[viewers[streaming[streamer]][view]]:
                    points[viewers[streaming[streamer]][view]][streamer] = 50 # Initially get 50 and then get 10 after
                else:
                    points[viewers[streaming[streamer]][view]][streamer] += 10

    FileReader.savePoints(points)

def cancelAllWagers()-> None: # Gets called only when turning off the bot 
    for streamer, wager in wagers.items():
        for number, bet in wagers[streamer].items():
            cancelWager(streamer, number)

def cancelWager(streamer, number):
    for user, amount in wagers[streamer][number].optionOne.items():
        points[user][streamer] += amount
    for user, amount in wagers[streamer][number].optionTwo.items():
        points[user][streamer] += amount

def payWinners(outcome, streamer, index) -> tuple:
    maxPayout = 0
    maxWinner = 0
    if outcome == 1:
        if wagers[streamer][index].optionOneTotal != 0:
            payout = max(1.2, wagers[streamer][index].optionTwoTotal / wagers[streamer][index].optionOneTotal)
            for user, amount in wagers[streamer][index].optionOne.items():
                reward = int(payout * amount)
                points[user][streamer] += reward
                if reward > maxPayout:
                    maxPayout = reward
                    maxWinner = user
    else:
        if wagers[streamer][index].optionTwoTotal != 0:
            payout = max(1.2, wagers[streamer][index].optionOneTotal / wagers[streamer][index].optionTwoTotal)
            for user, amount in wagers[streamer][index].optionTwo.items():
                reward = int(payout * amount)
                points[user][streamer] += reward
                if reward > maxPayout:
                    maxPayout = reward
    del wagers[streamer][index]
    if len(wagers[streamer]) == 0:
        del wagers[streamer]

    return maxPayout, maxWinner

# Gets a user object from handle
def getUser(handle) -> discord.user.User:
    user = discord.utils.get(bot.users, name=handle)
    if not isinstance(user, discord.user.User):
        name, discriminator = handle.split("#")
        user = discord.utils.get(bot.users, name=name, discriminator=discriminator)
    return user

def updateWagerTimers() -> None:
    for streamer, wager in wagers.items():
        for number, bet in wagers[streamer].items():
            wagers[streamer][number].increaseTimer()

# Called every minute
async def everyMinute() -> None:
    while True:
        await asyncio.sleep(60)  # Wait for 1 minute
        print(f'{Fore.MAGENTA}[LOG {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: Running Minute Subroutine')
        updatePoints()
        updateWagerTimers()
        await check_reminders()


# Runs the bot with the token
bot.run(token)