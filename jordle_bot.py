# V1 is aiming to build out the baseline functions to take in guesses and elimate words from the word pool
# based on the wordle's results. 
# 
# eventually, future versions should make more educated guesses and maybe even work directly from wordle's
# website and no longer require manual intervention. not sure if feasible yet.
import string

lowercase_letters = list(string.ascii_lowercase)
# test values
starting_guess = "seeps"
answer = "baker"
previous_guess = starting_guess


# TODO: create letter banks for each slot (1-5) of alphabets. These will be updated for each iteration of guesses.
letter_banks = [lowercase_letters] * 5
# print(letter_banks)

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

# TODO: update letter banks based on values of previous iteration. may need to assign priority to 0 values here?


# TODO: update word pool based on updated letter banks for each slot. order should not matter.


# general cycle of input/output from wordl so far.
results = guess_result_test(previous_guess, answer)
print(results)
