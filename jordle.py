"""
Author: Jarett Sutula
Version: 1.01
This file contains class modules for both a wordle-guessing bot
and a dynamic answer pool that pulls from a list of 5-letter words
from the Scrabble dictionary.

TODO: Implement a website / DB connection that can grab the daily
Jordle run from my Pi.

TODO: Make smarter guesses by considering more than just highest
scoring list of guesses. An equation might find a usage for
score and frequency to eliminate single element lists with
infrequent/unrealistic answers for a Wordle.

V1.01 performance for "crane":
{'1': 1, '2': 79, '3': 320, '4': 355, '5': 165, '6': 65, 'X': 29}
AVG: 3.902
V1.02 performance for "crane":
{'1': 1, '2': 84, '3': 325, '4': 332, '5': 164, '6': 67, 'X': 41}
AVG: 3.926
"""
import string
import re
from wordfreq import zipf_frequency

class Jordle:
    """
    A Jordle object takes in the current Wordle answer and a starting 
    word guess. It contains various methods to update letter banks, 
    make a guess based on analysis, check results, update answer pools,
    and display results.
    """
    def __init__(self, answer, guess):
        """
        A Jordle is given an answer and a starting guess. Letter banks
        are stored here and answer pools are of the AnswerPool class.
        As each guess and corresponding result is generated, they are
        stored for future display and eventual DB implementation.

        :param answer: A string of the current Wordle answer from API
        :param guess: A string of the opening 5-letter word guess.
        """
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
        self.results_debug = False
        # shows guessed letters so far for information theory approach.
        self.current_letters_debug = False
        # shows all answers in updated pool, scored by how many new letters are in them. 0-5.
        self.scored_guesses_debug = False
        # show top 10 (sorted) options for next guess based on highest score + most frequent in English
        self.frequency_debug = False
        # shows first 10 answers in pool (alphabetical, mostly useless now)
        self.pool_snapshot = False
        # shows regex string after updating banks and answer_contains
        self.regex_debug = False
        # shows counts of before/after filling answer pool, regex adjustment, answer_contains.
        self.answer_pool_debug = False

    def populate_banks(self):
        """Fills each letter bank with every letter of the alphabet."""
        for i in range(5): 
            self.letter_banks.append(list(string.ascii_uppercase))

    def get_results(self):
        """Compares a guess to the answer and return a resulting list
        of 0s, 1s, and 2s. 0s represent letters that do not appear
        at all (or, if a letter is guessed twice in the same word
        but it only appears once), 1s represent letters that exist in
        the word but are not in the correct position, and 2s represent
        letters that exist in the word are in the correct position.
        """
        result = [0, 0, 0, 0, 0]
        answer_mod = list(self.answer)

        # Priority has to be 2s > 1s> 0s
        # 2s can override everything since same letter guesses will stay 0s.
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
        """Prints out a letter bank from position i.
        :param i: An integer that denotes the index of a letter bank.
        """
        if i == -1:
            for bank in self.letter_banks:
                print(bank)
        elif 0 <= i <= 4:
            print(f'bank slot {i}: {self.letter_banks[i]}')
        else:
            print("something is wrong, invalid input for debug_banks")


    def update_letter_banks(self):
        """Updates the jordle's letter banks based on current guess."""
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
                if self.letter_banks[i] == [previous_guess[i]]:
                    # we already added the value in. don't re-add to answer_contains
                    pass
                else:
                    # set that bank to the letter, and add to answer_contains
                    self.letter_banks[i] = [previous_guess[i]]
                    if previous_guess[i] not in self.answer_contains:
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
                letter = previous_guess[i]
                if previous_guess[i] in self.letter_banks[i]:
                    self.letter_banks[i].remove(letter)
                    # we should only add this to answer_contains if we are guessing
                    # more than we know exists in answers_contains.
                    # otherwise, if 'E' exists once at pos 0, and we guess two different
                    # words with 'E's at pos 1 and pos 2, answer_contains tells us we have
                    # at least two 'E's in the final result which may not be true.
                    if previous_guess.count(letter) > self.answer_contains.count(letter):
                        count_misplaced = 0
                        for j in range(len(previous_guess_result)):
                            if previous_guess[j] == letter and previous_guess_result[j] == 1:
                                count_misplaced += 1
                        if count_misplaced > self.answer_contains.count(letter):
                            for k in range(count_misplaced - self.answer_contains.count(letter)):
                                self.answer_contains.append(letter)
                else:
                    print(f'cannot remove {previous_guess[i]} from letter bank {i}')

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
        """Updates the guessed_letters variable from recent guess."""
        guess = self.final_guesses[-1]
        for i in range(len(guess)):
            if guess[i] not in self.guessed_letters:
                self.guessed_letters += guess[i]
        
        if self.current_letters_debug:
            print(f'current guess: {guess} letters so far: {self.guessed_letters}')


    def choose_guess(self):
        """Chooses a guess for the next turn based on the new answer pool.
        Prioritizes higher 'score' guesses - those that put new letters in
        to the pool of guessed letters. The highest scored guesses get
        sorted by their frequency in the english language to higher emulate
        a real wordle guess, which are more common words.
        """
        # check if we even need to make a new guess.
        if self.guess == self.answer:
            # add final guess and result to lists.
            exit()
        # Need to find the word with the highest amount of unguessed letters.
        # general information theory says this is the fastest way to narrow the
        # validity pool to a single answer, I think.

        # V1.00 approach -------------------------------------------------------------
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

    
    def choose_guess_v2(self):
        """Chooses a guess for the next turn using a combination of score and frequency."""
        # check if we even need to make a new guess.
        if self.guess == self.answer:
            # add final guess and result to lists.
            exit()
        # Need to find the word with the highest amount of unguessed letters.
        # general information theory says this is the fastest way to narrow the
        # validity pool to a single answer, I think.

        # V1.01 approach -------------------------------------------------------------
        # score words based on how many unguessed letters they contain
        rated_guesses = []

        for guess in self.answer_pool.pool:
            score = 0
            for i in range(len(guess)):
                if guess[i] not in self.guessed_letters and guess[i] not in guess[:i]:
                    score += 1
            freq = zipf_frequency(guess, 'en', wordlist='best')
            # calculate a total score to make guesses off of.
            turn = len(self.final_guesses)
            total_score = ((score * turn) + (freq * (freq - turn))) / 30
            rated_guesses.append((guess, score, freq, total_score))

        rated_guesses.sort(key = lambda tup: tup[3], reverse=True)
        
        if self.scored_guesses_debug:
            print(f'Word   Score  Frequency  Total Score')
            print("-------------------------------------")
            for i in range(len(rated_guesses)):
                if i < 20:
                    g = rated_guesses[i]
                    print(f'{g[0]}:   {g[1]}     {g[2]:.3f}       {g[3]:.3f}')

        # set guess to top word.
        self.guess = rated_guesses[0][0]


    def update_answer_pool(self):
        """Using Regex, sifts out the answers in the answer pool
        that don't match the pattern given from updated letter banks
        and known letters in the answer so far.
        """
        accounted_for = []
        strings = []
        # add (?=.*x) lookup for character x in answer_contains.
        # removes need for old answer_contains checking that was
        # a band-aid fix and missed certain information.
        for i in range(len(self.answer_contains)):
            if self.answer_contains[i] not in accounted_for:
                lookup = "(?="
                accounted_for.append(self.answer_contains[i])
                for j in range(self.answer_contains.count(self.answer_contains[i])):
                    lookup += f'.*{self.answer_contains[i]}'
                lookup += ")"
                strings.append(lookup)

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

        count_before = len(self.answer_pool.pool)

        r = re.compile(regex)
        # filter out all options that don't match regex pattern.
        updated_list = list(filter(r.match, self.answer_pool.pool))
        

        check_after = len(updated_list)
        self.answer_pool.pool = updated_list[:]

        if self.answer_pool_debug:
            print(f'before regex: {count_before} words after: {check_after} words')

        if self.pool_snapshot:
            print(self.answer_pool.pool[:9])


    def output(self):
        """Prints all guesses Jordle made and their corresponding results."""
        print(f"The Wordle Answer was {self.answer}. Jordle's guesses:")
        for i in range(len(self.final_guesses)):
            print(f'guess {i + 1}: {self.final_guesses[i]} - {self.final_results[i]}')


class AnswerPool:
    """
    An AnswerPool object exists with a list of every 5 letter possible answer
    in the Scrabble dictionary. It gets updated through update_answer_pool() 
    from the Jordle class.
    """
    def __init__(self):
        """Fills the pool with the 5-letter Scrabble dictionary words."""
        self.pool = []
        # shows counts of before/after filling answer pool, regex adjustment, answer_contains.
        self.answer_pool_debug = False

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
    