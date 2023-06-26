class Wagers:
    def __init__(self, desc: str, wager: int, option_one: str, option_two: str, owner: int):
        self.desc = desc
        self.wagerID = wager
        self.optionOneDesc = option_one
        self.optionTwoDesc = option_two
        self.ownerID = owner
        self.optionOne = {}
        self.optionTwo = {}
        self.timer = 0

    def __str__(self):
        return f"wagerID: {self.wagerID}\nStreamerID: {self.ownerID}\nDescription: {self.desc}\n" \
               f"Options: (1) - {self.optionOneDesc} / (2) - {self.optionTwoDesc}"

    def addWager(self, user, amount, option):
        if option == 1:
            if user not in self.optionOne:
                self.optionOne[user] = amount
            else:
                self.optionOne[user] += amount
        elif option == 2:
            if user not in self.optionTwo:
                self.optionTwo[user] = amount
            else:
                self.optionTwo[user] += amount
        return option == 1 or option == 2

    def increaseTimer(self):
        if self.timer < 3:
            self.timer += 1
