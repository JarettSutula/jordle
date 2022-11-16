# V1 is aiming to build out the baseline functions to take in guesses and elimate words from the word pool
# based on the wordle's results. 
# 
# eventually, future versions should make more educated guesses and maybe even work directly from wordle's
# website and no longer require manual intervention. not sure if feasible yet.

# TODO: create letter banks for each slot (1-5) of alphabets. These will be updated for each iteration of guesses.

# TODO: assign values to letters based on their guesses from previous iteration. 
# (ex: 0 = does not appear at all, 1 = appears but not in this slot, 2 = in correct slot)

# TODO: update letter banks based on values of previous iteration. may need to assign priority to 0 values here?

# TODO: update word pool based on updated letter banks for each slot. order should not matter.
