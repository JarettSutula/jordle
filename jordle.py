import string

class Jordle:
    def __init__(self, answer, guess):
        self.answer = answer.upper()
        self.guess = guess
        self.letter_banks = []
        self.answer_contains = []
        self.answer_pool = []
        self.validity_pool = []
        self.guessed_letters = []
        self.final_guesses = []
        self.final_results = []

    def populate_banks(self):
        for i in range(5): 
            self.letter_banks.append(list(string.ascii_uppercase))

    def check_guess(self):
        result = [0, 0, 0, 0, 0]
        answer_mod = list(self.answer)

        for i in range(len(self.answer)):
            char = self.guess[i]
            if self.answer[i] == char:
                result[i] = 2
                answer_mod[i] = "-"

        for i in range(len(self.answer)):
            char = self.guess[i]
            if char in answer_mod and result[i] != 2:
                result[i] = 1
                # get first instance of said element
                index = answer_mod.index(char)
                answer_mod[index] = '-'

        # add guess and result to lists for output
        self.final_guesses.append(self.guess)
        self.final_results.append(result)

