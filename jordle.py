import string
import re
from wordfreq import zipf_frequency

class Jordle:
    def __init__(self, answer, guess):
        self.answer = answer.upper()
        self.guess = guess.upper()
        self.letter_banks = []
        self.answer_contains = []
        self.answer_pool = AnswerPool()
        self.validity_pool = AnswerPool()
        self.guessed_letters = []
        self.final_guesses = []
        self.final_results = []

    def populate_banks(self):
        for i in range(5): 
            self.letter_banks.append(list(string.ascii_uppercase))

    def get_results(self):
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

    def update_letter_banks(self):
        previous_guess = self.final_guesses[-1]
        previous_guess_result = self.final_results[-1]
        for i in range(len(previous_guess_result)):
            if previous_guess_result[i] == 2:
                self.letter_banks[i] = [previous_guess[i]]
                self.answer_contains.append(previous_guess[i])
        
        # if it's a 1, remove letter from current slot bank.
        for i in range(len(previous_guess_result)):
            if previous_guess_result[i] == 1:
                if previous_guess[i] in self.letter_banks[i]:
                    self.letter_banks[i].remove(previous_guess[i])
                else:
                    print(f'cannot remove {previous_guess[i]} from letter bank {i}')

                if previous_guess[i] not in self.answer_contains:
                    self.answer_contains.append(previous_guess[i])

        # if it's a 0, remove letter from all letter banks...
        # unless the letter exists somewhere else in the guess and that value is a 2.
        for i in range(len(previous_guess_result)):
            if previous_guess_result[i] == 0:
                # regardless of whether or not this is the only instance of this letter, it should be removed from its bank.
                # if previous_guess[i] in letter_banks[i]:
                #     letter_banks[i].remove(previous_guess[i])

                # if this is the only count of this char in the guess, remove from all banks.
                if previous_guess.count(previous_guess[i]) == 1:
                    for j in range(len(previous_guess_result)):
                        if previous_guess[i] in self.letter_banks[j]:
                            self.letter_banks[j].remove(previous_guess[i])
                else:
                    # we have more than 1 instance of that letter in the guess. Go through each slot and check and remove.
                    for j in range(len(previous_guess_result)):
                        # if we have an instance where we have a reoccuring letter in the guess..
                        if previous_guess[j] == previous_guess[i]:
                            # if it isn't a correct value (2), remove it from that specific letter bank.
                            if previous_guess_result[j] != 2 and previous_guess[j] in self.letter_banks[j]:
                                self.letter_banks[j].remove(previous_guess[j])

    def update_guessed_letters(self):
        guess = self.final_guesses[-1]
        for i in range(len(guess)):
            if guess[i] not in self.guessed_letters:
                self.guessed_letters += guess[i]


    def choose_guess(self):
        # check if we even need to make a new guess.
        if self.guess == self.answer:
            exit()
        # Need to find the word with the highest amount of unguessed letters.
        # general information theory says this is the fastest way to narrow the
        # validity pool to a single answer, I think.

        # store words based on how many unguessed letters they contain.
        # index relates to the amount.
        rated_guesses = [[],[],[],[],[],[]]
        # separate words into groups of unguessed letters
        highest = 0
        for guess in self.answer_pool.pool:
            score = 0
            for i in range(len(guess)):
                if guess[i] not in self.guessed_letters and guess[i] not in guess[:i]:
                    score += 1
            rated_guesses[score].append(guess)

        # TODO: Should have a check here somewhere if the guessing list is empty.
        # we'll have to select the highest 'score' word list. can do this backwards.
        for i in range(len(rated_guesses)-1, -1, -1):
            if len(rated_guesses[i]) > 0:
                highest = i
                break
        
        # Select the most frequently occuring words (ex - DEALS is more likely
        # the wordle than, say, "DEGAS" or "DELFS", which are legitimate words, but 
        # less likely to be on Wordle to avoid upsetting players.
        # make a dictionary to sort all words by their frequency. will display top 10 choices
        # TODO: if there is 1 2-score word and 20+ 1-score words, we should try to show 10 combined
        # (2 score word, 9 1-score words). It can be misleading to only see '1' word to guess
        # and that not end up being the answer. NOTE: need to decide how to prioritize top 10.
        # a 0.0 frequency 3-score words gives us more info than a 4.2 frequency 2-score word, but
        # which one is more likely to be the wordle? should it be dependent on the number of turns
        # left (earlier turns: more info, later turns: more likely guesses)?
        frequencies = {}
        for i in range(len(rated_guesses[highest])):
            freq_word = rated_guesses[highest][i]
            freq = zipf_frequency(freq_word, 'en', wordlist='best')
            frequencies[freq_word] = freq
        
        # sort frequencies by key.
        # a list of (word, freq)s... key is tuple[0] and value is tuple[1]
        # NOTE: could potentially do (key, value, score)? use some aggregate value * score to assign
        # priority somewhat fairly? some deeper form of (value * score) / turn to make smarter decision based
        # on how far we are through a wordle cycle.
        sorted_frequencies = sorted(frequencies.items(), key= lambda x:x[1], reverse=True)
        
        # set guess to top word.
        self.guess = sorted_frequencies[0][0]
        


class AnswerPool:
    def __init__(self):
        self.pool = []
        pool_file = open('5_letter_dict.txt', 'r')
        answers = pool_file.readlines()
        count = 0

        for answer in answers:
            self.pool.append(answer.strip())
            count += 1
        
        pool_file.close()
    
    def update(self):
        # generate regex based off of current letter banks
        strings = []
        for bank in self.letter_banks:
            # Don't need brackets for single letters.
            if len(bank) == 1:
                strings.append(bank[0])
            else:
                result = "["
                for letter in bank:
                    result += letter
                result += "]"
                strings.append(result)
        
        regex = "".join(strings)

        count_before = len(self.pool)

        r = re.compile(regex)
        # filter out all options that don't match regex pattern.
        updated_list = list(filter(r.match, self.pool))
        # regex does not take into account the letters that exist in the word
        # but not in the correct spots. Correct regex string for that, the way
        # this has been implemented, would be a nightmare to write.
        # instead we will just remove any words from updated_list that do not contain
        # the letters from 'answer_contains'. Testing ensues. 
        check_b4 = len(updated_list)
        # separate list to ensure the loop does not get thrown by mid-iteration removal.
        updated_list_copy = updated_list[:]
        for guess in updated_list:
            remove = False
            for letter in self.answer_contains:
                # print(letter, guess, remove)
                if letter not in guess:
                    remove = True
            if remove:
                # print(f'removed {guess}')
                updated_list_copy.remove(guess)

        check_after = len(updated_list_copy)
        self.pool = updated_list_copy[:]


