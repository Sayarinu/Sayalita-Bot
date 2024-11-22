import datetime
import time

class Wagers:
  def __init__(self, desc: str, wager: int, option_one: str, option_two: str, owner: int):
    self.desc = desc
    self.wagerID = wager
    self.optionOneDesc = option_one
    self.optionTwoDesc = option_two
    self.ownerID = owner
    self.optionOne = {}
    self.optionOneTotal = 0
    self.optionTwo = {}
    self.optionTwoTotal = 0
    self.timer = 0

  def __str__(self):
    return f"wagerID: {self.wagerID}\nStreamerID: {self.ownerID}\nDescription: {self.desc}\n" \
      f"Options: (1) - {self.optionOneDesc} / (2) - {self.optionTwoDesc}"

  def addWager(self, user, amount, option):
    if option == 1:
      self.optionOneTotal += amount
      if user not in self.optionOne:
        self.optionOne[user] = amount
      else:
        self.optionOne[user] += amount
    elif option == 2:
      self.optionTwoTotal += amount
      if user not in self.optionTwo:
        self.optionTwo[user] = amount
      else:
        self.optionTwo[user] += amount
    return option == 1 or option == 2

  def increaseTimer(self):
    if self.timer < 3:
      self.timer += 1

class Reminder:
  def __init__(self, message, date_time, user_id):
    self.message = message
    self.date_time = date_time
    self.user_id = user_id

  def __str__(self) -> str:
    return f"Reminder for {self.date_time}: {self.message}"


  def is_due(self):
    current_time = datetime.datetime.now()
    return current_time >= self.date_time