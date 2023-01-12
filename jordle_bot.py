# V1 is aiming to build out the baseline functions to take in guesses and elimate words from the word pool
# based on the wordle's results. 
# 
# eventually, future versions should make more educated guesses and maybe even work directly from wordle's
# website and no longer require manual intervention. not sure if feasible yet.
import string
import re

# test values
starting_guess = "SEEPS"
answer = "BAKER"
previous_guess = starting_guess
answer_contains = []

answer_pool = []

bank_debug = True
guess_debug = True
answer_debug = True

# letter banks will keep track of chars viable for each slot in the wordle. 1 for each slot.
letter_banks = []
for i in range(5): letter_banks.append(list(string.ascii_uppercase))

if guess_debug:
    print(f'starting guess is {starting_guess}')
    print(f'wordle answer is {answer}')

# TODO: assign values to letters based on their guesses from previous iteration. 
# (ex: 0 = does not appear at all, 1 = appears but not in this slot, 2 = in correct slot)
def guess_result_test(previous_guess, answer):
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
        if char in answer_mod:
            result[i] = 1
            # get first instance of said element.
            index = answer_mod.index(char)
            answer_mod[index] = '-'

    return result

# TODO: update letter banks based on values of previous iteration. may need to assign priority here.
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
            letter_banks[i] = [previous_guess[i]]
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
            letter_banks[i].remove(previous_guess[i])
            if previous_guess[i] not in answer_contains:
                answer_contains.append(previous_guess[i])
            if bank_debug: 
                print(f"removing letter '{previous_guess[i]}' from bank {i}")
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

# TODO: update word pool based on updated letter banks for each slot. order should not matter.
def update_answer_pool():
    regex = generate_regex_string()
    count_before = len(answer_pool)

    for answer in answer_pool:
        if not re.match(regex, answer):
            answer_pool.remove(answer)

    if answer_debug:
        print(f'before: {count_before} words\nafter: {len(answer_pool)}')
    
def generate_regex_string():
    strings = []
    for bank in letter_banks:
        result = "["
        for letter in bank:
            result += letter
        result += "]"
        strings.append(result)

    regex = "".join(strings)
    print(regex)

def fill_answer_pool(answer_list):
    pool_file = open('5_letter_dict.txt', 'r')
    answers = pool_file.readlines()
    count = 0

    for answer in answers:
        answer_list.append(answer.strip())
        count += 1
    
    pool_file.close()
    
    if answer_debug:
        print(f'added {count} words to answer pool.')
        print(f'first word is {answer_list[1]} and last word is {answer_list[-1]}')

def debug_banks(bank):
    if bank == -1:
        for bank in letter_banks:
            print(bank)
    elif 0 <= bank <= 4:
        print(f'bank slot {bank}: {letter_banks[bank]}')
    else:
        print("something is wrong, invalid input for debug_banks")

# general cycle of input/output from wordle so far.
fill_answer_pool(answer_pool)

results = guess_result_test(previous_guess, answer)
print(results)
generate_regex_string()
update_letter_banks(letter_banks, previous_guess, results)
generate_regex_string()