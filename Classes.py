class Wagers:
    def __init__(self, desc: str, wager: int, option_one: str, option_two: str, owner: int):
        self.desc = desc
        self.wagerID = wager
        self.optionOneDesc = option_one
        self.optionTwoDesc = option_two
        self.ownerID = owner
        self.optionOne = {}
        self.optionTwo = {}

    def addWager(self, user, amount, option):
        if option == 1:
            if user not in self.optionOne:
                self.optionOne[user] = amount
            else:
                self.optioNTwo[user] += amount
        elif option == 2:
            if user not in self.optionTwo:
                self.optionTwo[user] = amount
            else:
                self.optionTwo[user] += amount
        return option == 1 or option == 2
