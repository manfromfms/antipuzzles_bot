"""
This module extends existing daily challenges module by refining different types of challenges then to be used in the app. 

Module requirements:
- daily
- translation
"""

import time
import math
import random

from ..translation import Translation
from ..daily import Daily as Daily_base

class Daily(Daily_base):
    def __init__(self):
        super().__init__()

        """
        # Intro

        The aim of daily challenges is to encourage users to solve puzzles every day by keeping their streak. To get the streak going at least the first level challenge should be completed. Difficulty of challenges grow exponentially (e.g. 10-20-40). Each level challenge should be designed to encourage users to solve at least X amount of puzzles (on average). This is achieved through probability calculations.

        # Types of challenges

        ## Gain XP:
        XP value raises after each puzzles is attempted giving 1xp for a wrong solution and (elogain / 2)xp for a correct solution. If the puzzle of the same raiting is solved, elochange will always be around 10. This means that X amount of puzzles will require users to get (3*X)xp.

        ## Attempt puzzles:
        This value is the same as X.

        ## Correctly solve puzzles:
        Due to how puzzles are selected, there is 50/50 chance of solving the puzzle. This means that X/2 puzzles have to be requested to solve correctly.

        ## Solve puzzles in a row:
        This problem doesn't have a solution. To get something reasonable we'll introduce the probability of solving N puzzles from X in a row. For this project this number will be 75%. The value should be checked in the look-up table.
        
        # Difficulty aim

        The bigger your streak is, the harder daily challenges you should get. The next formula is suggested: X=5+log2(streak+1). This means that there is no upper limit, but the growth is very slow after a few days.

        # Future

        The list of challenges is to be expanded with themes-related, openings-related and difficulty-related challenges.
        """

        self.types = [
            Translation('Gain XP'), 
            Translation('Attempt puzzles'), 
            Translation('Correctly solve puzzles'), 
            Translation('Solve puzzles in a row'),
        ]

        self.rowLookup = [0, # 0 puzzles
            0, 1, 1, 1, 2, 2, 2, 2, 2, 2, #  1-10 puzzles
            2, 2, 3, 3, 3, 3, 3, 3, 3, 3, # 11-20 puzzles
            3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 
            4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
            5, 5, 5, 6, 6, 6, 6, 6, 6
        ]

    
    @staticmethod
    def searchByUserId(userId):
        base = Daily_base().searchByUserId(userId)
        daily = Daily()

        daily.id = base.id
        daily.userId = base.userId
        daily.streak = base.streak
        daily.xp = base.xp
        daily.currentDayFinishTimestamp = base.currentDayFinishTimestamp
        daily.firstTaskType = base.firstTaskType
        daily.firstTaskMax = base.firstTaskMax
        daily.firstTaskProgress = base.firstTaskProgress
        daily.secondTaskType = base.secondTaskType
        daily.secondTaskMax = base.secondTaskMax
        daily.secondTaskProgress = base.secondTaskProgress
        daily.thirdTaskType = base.thirdTaskType
        daily.thirdTaskMax = base.thirdTaskMax
        daily.thirdTaskProgress = base.thirdTaskProgress
        daily.doneForToday = base.doneForToday

        daily.update_database_entry()

        return daily


    def compile(self) -> Translation:
        s = Translation('Only') + f' {round((self.currentDayFinishTimestamp - time.time()) / 60 / 60 * 10)/10} ' + Translation('hours left!') + '\n\n'

        s = s + '🕯️ ' + self.types[self.firstTaskType] + f': {self.firstTaskMax}\n' + Translation('Progress') + f': {self.firstTaskProgress}/{self.firstTaskMax}{' ✅' if self.firstTaskMax == self.firstTaskProgress else ''}\n\n'

        s = s + '🔦 ' + self.types[self.secondTaskType] + f': {self.secondTaskMax}\n' + Translation('Progress') + f': {self.secondTaskProgress}/{self.secondTaskMax}{' ✅' if self.secondTaskMax == self.secondTaskProgress else ''}\n\n'

        s = s + '🏮 ' + self.types[self.thirdTaskType] + f': {self.thirdTaskMax}\n' + Translation('Progress') + f': {self.thirdTaskProgress}/{self.thirdTaskMax}{' ✅' if self.thirdTaskMax == self.thirdTaskProgress else ''}\n\n'

        return s


    def generateGoal(self, t, X):
        if t == 0:
            return int(math.ceil(3*X))
        
        if t == 1:
            return int(math.ceil(X))
        
        if t == 2:
            return int(math.ceil(X/2))
        
        if t == 3:
            return int(self.rowLookup[int(X)])
        
        return -1


    def update_general(self):
        """This function checks if challenges have expired and by how much handling possibilities accordingly."""

        if time.time() > self.currentDayFinishTimestamp:
            if time.time() - self.currentDayFinishTimestamp > (60*60*24):
                # A day was skipped
                self.streak = 0

            if not self.doneForToday:
                # No challenges were completed
                self.streak = 0

            self.currentDayFinishTimestamp = math.ceil(time.time() / (60*60*24)) * (60*60*24)

            X = math.floor(5. + math.log2(self.streak + 1))

            self.firstTaskType = math.floor(random.random() * len(self.types))
            self.firstTaskMax = self.generateGoal(self.firstTaskType, X)
            self.firstTaskProgress = 0

            self.secondTaskType = math.floor(random.random() * len(self.types))
            self.secondTaskMax = self.generateGoal(self.secondTaskType, X*2.5)
            self.secondTaskProgress = 0

            self.thirdTaskType = math.floor(random.random() * len(self.types))
            self.thirdTaskMax = self.generateGoal(self.thirdTaskType, X*6.25)
            self.thirdTaskProgress = 0

            self.doneForToday = False

            self.update_database_entry()

    
    def update_state(self, elochange: float):
        if elochange > 0:
            self.xp += int(elochange) // 2

            # First task
            if self.firstTaskType == 0:
                self.firstTaskProgress += int(elochange) // 2

            elif self.firstTaskType == 1:
                self.firstTaskProgress += 1

            elif self.firstTaskType == 2:
                self.firstTaskProgress += 1

            elif self.firstTaskType == 3:
                self.firstTaskProgress += 1


            # Second task
            if self.secondTaskType == 0:
                self.secondTaskProgress += int(elochange) // 2

            elif self.secondTaskType == 1:
                self.secondTaskProgress += 1

            elif self.secondTaskType == 2:
                self.secondTaskProgress += 1

            elif self.secondTaskType == 3:
                self.secondTaskProgress += 1


            # Third task
            if self.thirdTaskType == 0:
                self.thirdTaskProgress += int(elochange) // 2

            elif self.thirdTaskType == 1:
                self.thirdTaskProgress += 1

            elif self.thirdTaskType == 2:
                self.thirdTaskProgress += 1

            elif self.thirdTaskType == 3:
                self.thirdTaskProgress += 1

        else:
            self.xp += 1

            # First task
            if self.firstTaskType == 0:
                self.firstTaskProgress += 1

            elif self.firstTaskType == 1:
                self.firstTaskProgress += 1

            elif self.firstTaskType == 3:
                if self.firstTaskProgress < self.firstTaskMax:
                    self.firstTaskProgress = 0


            # Second task
            if self.secondTaskType == 0:
                self.secondTaskProgress += 1

            elif self.secondTaskType == 1:
                self.secondTaskProgress += 1

            elif self.secondTaskType == 3:
                if self.secondTaskProgress < self.secondTaskMax:
                    self.secondTaskProgress = 0


            # Third task
            if self.thirdTaskType == 0:
                self.thirdTaskProgress += 1

            elif self.thirdTaskType == 1:
                self.thirdTaskProgress += 1

            elif self.thirdTaskType == 3:
                if self.thirdTaskProgress < self.thirdTaskMax:
                    self.thirdTaskProgress = 0

            self.update_database_entry()


        self.firstTaskProgress = min(self.firstTaskMax, self.firstTaskProgress)
        if self.firstTaskProgress >= self.firstTaskMax and self.doneForToday == 0:
            self.streak += 1
            self.doneForToday = 1


        self.secondTaskProgress = min(self.secondTaskMax, self.secondTaskProgress)
        if self.secondTaskProgress >= self.secondTaskMax and self.doneForToday == 0:
            self.streak += 1
            self.doneForToday = 1


        self.thirdTaskProgress = min(self.thirdTaskMax, self.thirdTaskProgress)
        if self.thirdTaskProgress >= self.thirdTaskMax and self.doneForToday == 0:
            self.streak += 1
            self.doneForToday = 1

        self.update_database_entry()
