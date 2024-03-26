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
        # show letter banks updating and removing based on guess.
        self.bank_debug = False
        # shows answer at the start.
        self.guess_debug = False
        # shows the resulting 0, 1, 2 list for each guess against the answer (RECOMMENDED)
        self.results_debug = True
        # shows guessed letters so far for information theory approach.
        self.current_letters_debug = False
        # at the end, shows all guesses and their resulting [0,1,2] lists.
        self.summary_debug = True
        # shows all answers in updated pool, scored by how many new letters are in them. 0-5.
        self.scored_guesses_debug = False
        # show top 10 (sorted) options for next guess based on highest score + most frequent in English
        self.frequency_debug = True

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

        if self.results_debug:
            print(result)


    def debug_banks(self, i):
        if i == -1:
            for bank in self.letter_banks:
                print(bank)
        elif 0 <= bank <= 4:
            print(f'bank slot {i}: {self.letter_banks[i]}')
        else:
            print("something is wrong, invalid input for debug_banks")


    def update_letter_banks(self):
        if self.bank_debug:
            two_count = self.final_results[-1].count(2)
            print(f'\nGoing through correct values: should be {two_count}.')

        previous_guess = self.final_guesses[-1]
        previous_guess_result = self.final_results[-1]
        for i in range(len(previous_guess_result)):
            if previous_guess_result[i] == 2:
                if self.bank_debug:
                    print(f"before correct char in slot {i}:")
                    self.debug_banks(i)
                self.letter_banks[i] = [previous_guess[i]]
                self.answer_contains.append(previous_guess[i])
                if self.bank_debug:
                    print(f"after correct char in slot {i}:")
                    self.debug_banks(-1)
        
        if self.bank_debug:
            one_count = self.final_results[-1].count(1)
            print(f'\nGoing through correct but misplaced values: should be {one_count}.')
        # if it's a 1, remove letter from current slot bank.
        for i in range(len(previous_guess_result)):
            if previous_guess_result[i] == 1:
                if previous_guess[i] in self.letter_banks[i]:
                    self.letter_banks[i].remove(previous_guess[i])
                else:
                    print(f'cannot remove {previous_guess[i]} from letter bank {i}')

                if previous_guess[i] not in self.answer_contains:
                    self.answer_contains.append(previous_guess[i])
                if self.bank_debug: 
                    print(f"removing letter '{previous_guess[i]}' from bank {i}")
                    self.debug_banks(i)

        # if it's a 0, remove letter from all letter banks...
        # unless the letter exists somewhere else in the guess and that value is a 2.
        if self.bank_debug:
            zero_count = self.final_results[-1].count(0)
            print(f'\nGoing through incorrect values: should be {zero_count}.')
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
                            if self.bank_debug:
                                print(f'removed {previous_guess[i]} from letter bank {j}')
                                self.debug_banks(j)
                    if self.bank_debug: 
                        print(f"removed letter '{previous_guess[i]}' from all banks")
                        self.debug_banks(-1)
                else:
                    # we have more than 1 instance of that letter in the guess. Go through each slot and check and remove.
                    for j in range(len(previous_guess_result)):
                        # if we have an instance where we have a reoccuring letter in the guess..
                        if previous_guess[j] == previous_guess[i]:
                            # if it isn't a correct value (2), remove it from that specific letter bank.
                            if previous_guess_result[j] != 2 and previous_guess[j] in self.letter_banks[j]:
                                self.letter_banks[j].remove(previous_guess[j])
                                if self.bank_debug:
                                    print(f'removing {previous_guess[i]} from letter bank {j} code=003')
                                    self.debug_banks(j)

    def update_guessed_letters(self):
        guess = self.final_guesses[-1]
        for i in range(len(guess)):
            if guess[i] not in self.guessed_letters:
                self.guessed_letters += guess[i]
        
        if self.current_letters_debug:
            print(f'current guess: {guess} letters so far: {self.guessed_letters}')


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

        if self.scored_guesses_debug:
            for i in range(len(rated_guesses)):
                if len(rated_guesses[i]) > 0:
                    print(f'{i} score guesses:')
                    print(rated_guesses[i])

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
        
        if self.frequency_debug:
            for i in range(len(sorted_frequencies)):
                # only want the first 10!
                if i > 9:
                    break
                else:
                    print(f' {i+1}. {sorted_frequencies[i][0]}: {sorted_frequencies[i][1]}')

        # set guess to top word.
        self.guess = sorted_frequencies[0][0]


class AnswerPool:
    def __init__(self):
        self.pool = []
        # shows first 10 answers in pool (alphabetical, mostly useless now)
        self.pool_snapshot = True
        # shows counts of before/after filling answer pool, regex adjustment, answer_contains.
        self.answer_pool_debug = True
        # shows regex string after updating banks and answer_contains
        self.regex_debug = False

        pool_file = open('5_letter_dict.txt', 'r')
        answers = pool_file.readlines()
        count = 0

        for answer in answers:
            self.pool.append(answer.strip())
            count += 1
        
        pool_file.close()

        if self.answer_pool_debug:
            print(f'added {count} words to answer pool.')
            print(f'first word is {self.pool[0]} and last word is {self.pool[-1]}')
    
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
        if self.regex_debug:
            print(f'combined strings: {strings}')
            print(f'regex string: {regex}')

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

        if self.answer_pool_debug:
            print(f'before regex: {count_before} words after: {check_b4} words')
            print(f'before answer_contains logic: {check_b4} words after: {check_after} words')

        if self.pool_snapshot:
            print(self.pool[:9])


