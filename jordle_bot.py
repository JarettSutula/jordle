# V1 is aiming to build out the baseline functions to take in guesses and elimate words from the word pool
# based on the wordle's results. 
# 
# eventually, future versions should make more educated guesses and maybe even work directly from wordle's
# website and no longer require manual intervention. not sure if feasible yet.
import string
import re
import random
from wordfreq import zipf_frequency

# test values
answer = ""
# this will contain letters that we know are in the answer.
# will bridge gap of my regex knowledge.
answer_contains = []

# the current pool of answers left to guess.
answer_pool = []
# the overarching pool of answers valid to guess regardless of knowledge.
validity_pool = []
# what letters have been guessed for information theory approach.
guessed_letters = []

# for later (eventual) web implementation. store guesses and results for display.
final_guesses = []
final_results = []

# DEBUG STATEMENTS
# show letter banks updating and removing based on guess.
bank_debug = False
# shows answer at the start.
guess_debug = False
# shows the resulting 0, 1, 2 list for each guess against the answer (RECOMMENDED)
results_debug = True
# shows counts of before/after filling answer pool, regex adjustment, answer_contains.
answer_pool_debug = True
# shows regex string after updating banks and answer_contains
regex_debug = True
# shows first 10 answers in pool (alphabetical, mostly useless now)
pool_snapshot = False
# shows guessed letters so far for information theory approach.
current_letters_debug = False
# at the end, shows all guesses and their resulting [0,1,2] lists.
summary_debug = True
# shows all answers in updated pool, scored by how many new letters are in them. 0-5.
scored_guesses_debug = False
# show top 10 (sorted) options for next guess based on highest score + most frequent in English
frequency_debug = True
# show answer contains list to ensure tracking correctly.
answer_contains_debug = True

# letter banks will keep track of chars viable for each slot in the wordle. 1 for each slot.
letter_banks = []
for i in range(5): letter_banks.append(list(string.ascii_uppercase))

if guess_debug:
    print(f'wordle answer is {answer}')


def check_guess(previous_guess, answer):
    result = [0, 0, 0, 0, 0]
    # need to go through and mark every correct slot with a "-"
    # example - the guess 'level' into 'baker' should NOT show a 1 for the first e since there is only 1 e and it
    # is in the correct place for slot 4/5. priority --> fill 2s, fill 1s, fill 0s
    answer_mod = list(answer)

    for i in range(len(answer)):
        char = previous_guess[i]
        if answer[i] == char:
            result[i] = 2
            answer_mod[i] = '-'

    # now that correct ones are done, do the same with one that are misplaced.
    for i in range(len(answer)):
        char = previous_guess[i]
        if char in answer_mod and result[i] != 2:
            result[i] = 1
            # get first instance of said element.
            index = answer_mod.index(char)
            answer_mod[index] = '-'

    # add guess and result to overall lists.
    final_guesses.append(previous_guess)
    final_results.append(result)

    # print result after each guess (like wordle does)
    if results_debug:
        print(result)
    return result


def update_letter_banks(banks, previous_guess, values):
    # go through every matching letters and update banks.
    if bank_debug:
        two_count = values.count(2)
        print(f'\nGoing through correct values: should be {two_count}.')
    for i in range(len(values)):
        if values[i] == 2:
            if bank_debug:
                print(f"before correct char in slot {i}:")
                debug_banks(i)
            if letter_banks[i] == [previous_guess[i]]:
                # we already added the value in. don't re-add to answer_contains
                pass
            else:
                # set that bank to the letter, and add to answer_contains
                letter_banks[i] = [previous_guess[i]]
                if previous_guess[i] not in answer_contains:
                    answer_contains.append(previous_guess[i])
            if bank_debug:
                print(f"after correct char in slot {i}:")
                debug_banks(-1)
    
    if bank_debug:
        one_count = values.count(1)
        print(f'\nGoing through correct but misplaced values: should be {one_count}.')
    # if it's a 1, remove letter from current slot bank.
    for i in range(len(values)):
        if values[i] == 1:
            letter = previous_guess[i]
            if letter in letter_banks[i]:
                letter_banks[i].remove(letter)
                # we should only add this to answer_contains if we are guessing
                # more than we know exists in answers_contains.
                # otherwise, if 'E' exists once at pos 0, and we guess two different
                # words with 'E's at pos 1 and pos 2, answer_contains tells us we have
                # at least two 'E's in the final result which may not be true.
                #NOTE: have to make sure that VICHY > CIRCA for MIMIC does not give
                # two C's in append. If the count > contains, we need to make sure the
                # amount of 1's in results are from the same letter.
                if previous_guess.count(letter) > answer_contains.count(letter):
                    indices_misplaced = 0
                    for j in range(len(previous_guess)):
                        if previous_guess[j] == letter and values[j] == 1:
                            indices_misplaced += 1
                    print(f'indices = {indices_misplaced}, count in AC = {answer_contains.count(letter)}')
                    if indices_misplaced > answer_contains.count(letter):
                        # if there are more 1s for the letter than there are in answer_contains
                        # add the difference (in most cases 1, in rare cases 2)
                        for k in range(indices_misplaced - answer_contains.count(letter)):
                            answer_contains.append(letter)
            else:
                print(f'cannot remove {letter} from letter bank {i}')

            # if previous_guess[i] not in answer_contains:
            #     answer_contains.append(previous_guess[i])
            if bank_debug: 
                print(f"removing letter '{letter}' from bank {i}")
                debug_banks(i)

    # if it's a 0, remove letter from all letter banks...
    # unless the letter exists somewhere else in the guess and that value is a 2.
    if bank_debug:
        zero_count = values.count(0)
        print(f'\nGoing through incorrect values: should be {zero_count}.')
    for i in range(len(values)):
        if values[i] == 0:
            # regardless of whether or not this is the only instance of this letter, it should be removed from its bank.
            # if previous_guess[i] in letter_banks[i]:
            #     letter_banks[i].remove(previous_guess[i])

            # if this is the only count of this char in the guess, remove from all banks.
            if previous_guess.count(previous_guess[i]) == 1:
                for j in range(len(values)):
                    if previous_guess[i] in letter_banks[j]:
                        letter_banks[j].remove(previous_guess[i])
                        if bank_debug:
                            print(f'removed {previous_guess[i]} from letter bank {j}')
                            debug_banks(j)
                if bank_debug: 
                    print(f"removed letter '{previous_guess[i]}' from all banks")
                    debug_banks(-1)
            else:
                # we have more than 1 instance of that letter in the guess. Go through each slot and check and remove.
                for j in range(len(values)):
                    # if we have an instance where we have a reoccuring letter in the guess..
                    if previous_guess[j] == previous_guess[i]:
                        # if it isn't a correct value (2), remove it from that specific letter bank.
                        if values[j] != 2 and previous_guess[j] in letter_banks[j]:
                            letter_banks[j].remove(previous_guess[j])
                            if bank_debug:
                                print(f'removing {previous_guess[i]} from letter bank {j} code=003')
                                debug_banks(j)

    answer_contains.sort()
    if answer_contains_debug:
        print(f'Answer contains: {answer_contains}')

def update_answer_pool():
    global answer_pool
    regex = generate_regex_string()
    count_before = len(answer_pool)

    r = re.compile(regex)
    # filter out all options that don't match regex pattern.
    updated_list = list(filter(r.match, answer_pool))
    # regex does not take into account the letters that exist in the word
    # but not in the correct spots. Correct regex string for that, the way
    # this has been implemented, would be a nightmare to write.
    # instead we will just remove any words from updated_list that do not contain
    # the letters from 'answer_contains'. Testing ensues. 
    # check_b4 = len(updated_list)
    # # separate list to ensure the loop does not get thrown by mid-iteration removal.
    # updated_list_copy = updated_list[:]
    # for guess in updated_list:
    #     remove = False
    #     #TODO Need to make sure guesses contain ALL elements of answer_contains
    #     # previously not considering duplicates. Changed but needs check.
    #     for letter in answer_contains:
    #         # print(letter, guess, remove)
    #         if letter not in guess:
    #             remove = True
    #     if remove:
    #         # print(f'removed {guess}')
    #         updated_list_copy.remove(guess)

    check_after = len(updated_list)
    answer_pool = updated_list[:]
    if answer_pool_debug:
        print(f'before regex: {count_before} words after: {check_after} words')
        # print(f'before answer_contains logic: {check_b4} words after: {check_after} words')

    if pool_snapshot:
        print(answer_pool[:15])
    

def update_guessed_letters(guess, guessed_letters):
    # given a guess, keep track of which letters have been guessed. vital to
    # information theory approach.
    for i in range(len(guess)):
        if guess[i] not in guessed_letters:
            guessed_letters += guess[i]
    
    if current_letters_debug:
        print(f'current guess: {guess} letters so far: {guessed_letters}')


def generate_regex_string():
    accounted_for = []
    strings = []
    for i in range(len(answer_contains)):
        if answer_contains[i] not in accounted_for:
            lookup = "(?="
            accounted_for.append(answer_contains[i])
            for j in range(answer_contains.count(answer_contains[i])):
                lookup += f'.*{answer_contains[i]}'
            lookup += ")"
            strings.append(lookup)


    for bank in letter_banks:
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
    if regex_debug:
        print(f'combined strings: {strings}')
        print(f'regex string: {regex}')
    return regex


def fill_answer_pool(answer_list):
    pool_file = open('5_letter_dict.txt', 'r')
    answers = pool_file.readlines()
    count = 0

    for answer in answers:
        answer_list.append(answer.strip())
        count += 1
    
    pool_file.close()
    
    if answer_pool_debug:
        print(f'added {count} words to answer pool.')
        print(f'first word is {answer_list[0]} and last word is {answer_list[-1]}')


def debug_banks(bank):
    if bank == -1:
        for bank in letter_banks:
            print(bank)
    elif 0 <= bank <= 4:
        print(f'bank slot {bank}: {letter_banks[bank]}')
    else:
        print("something is wrong, invalid input for debug_banks")


def information_theory_approach(guessed_letter_list):
    # Need to find the word with the highest amount of unguessed letters.
    # general information theory says this is the fastest way to narrow the
    # validity pool to a single answer, I think.

    # store words based on how many unguessed letters they contain.
    # index relates to the amount.
    rated_guesses = [[],[],[],[],[],[]]
    # separate words into groups of unguessed letters
    global answer_pool
    highest = 0
    for guess in answer_pool:
        score = 0
        for i in range(len(guess)):
            if guess[i] not in guessed_letter_list and guess[i] not in guess[:i]:
                score += 1
        rated_guesses[score].append(guess)

    if scored_guesses_debug:
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
    # test print.
    if frequency_debug:
        for i in range(len(sorted_frequencies)):
            # only want the first 10!
            if i > 9:
                break
            else:
                print(f' {i+1}. {sorted_frequencies[i][0]}: {sorted_frequencies[i][1]}')


def wordle_loop():
    # two options - jordle, where answer is grabbed from API and guessed.
    # wordle - feed bot results manually and let it give you the next guess.
    while True:
        mode = input("Jordle or Wordle? j/w: ")
        if mode not in ["j", "w"]:
            print("please pick between jordle or wordle approach.")
        else:
            break
        
    print(mode)
    # general cycle of input/output from wordle so far.
    fill_answer_pool(answer_pool)
    fill_answer_pool(validity_pool)
    # if we are guessing word (for testing purposes) grab random one.
    # in future, this will be the result of the API.
    if mode == "j":
        # answer = answer_pool[random.randint(0, len(answer_pool) - 1)]
        answer = "AGING"
    guessing = True
    guesses = 0
    result = False
    while guessing and guesses < 6:
        guess = input(f"guess {guesses + 1}: ").upper()
        # check if guess is valid - 3 options.
        # 1. must only contain letters.
        # 2. must only be 5 letters long.
        # 3. must be in the bank (should override all)
        if guess not in validity_pool:
            print("guess is invalid - please ensure guess is a valid 5 letter word.")
            
        else:
            guesses += 1
            # split here based on jordle/wordle.
            if mode == "w":
                # provide own results to run check.
                while True:
                    results_input = input("results: ")
                    results = results_input.split()
                    # should all be ints.
                    try:
                        results = list(map(int, results))
                    except: 
                        print("please enter numbers only.")
                    else:
                        if all(x in [0, 1, 2] for x in results) and len(results) == 5:
                            # update the guess and results since we are not calling check_guess.
                            final_guesses.append(guess)
                            final_results.append(results)
                            break
                        else:
                            print("Please type the 5 results from 0-2.")

            if mode == "j":
                results = check_guess(guess, answer)
            
            if results == [2, 2, 2, 2, 2]:
                # regardless 
                guessing = False
                result = True
                if mode == "w":
                    # just for output.
                    answer = guess
        
            else:
                update_letter_banks(letter_banks, guess, results)
                update_answer_pool()
                update_guessed_letters(guess, guessed_letters)
                # with information ready for next guess, pick best options for next guess.
                information_theory_approach(guessed_letters)
    
    if result:
        print(f'{answer} guessed in {guesses} attempts.')
    else:
        print(f'{answer} not guessed in {guesses} attempts.')

    if summary_debug:
        for i in range(len(final_guesses)):
            print(f'guess {i + 1}: {final_guesses[i]} - {final_results[i]}')

wordle_loop()
