"""
Given a starting word, return how it does vs the 1000+ previous
Wordle answers.
"""

from jordle import Jordle, AnswerPool
from tqdm import tqdm
import matplotlib.pyplot as plt
from wordfreq import zipf_frequency

prev_answers = []
with open('previous_wordle_answers.txt', 'r') as file:
    line = file.readline()
    prev_answers = line.split()

# best_answers = []
answers = AnswerPool()
failures = []
scores = {'1': 0, '2': 0, '3': 0, '4':0, '5':0, '6':0, 'X':0}
avg = 0
starting_word = "slant"
# slant outcomes v1.01
# {'1': 0, '2': 72, '3': 331, '4': 389, '5': 153, '6': 42, 'X': 27}
# 3.845
# ['ABATE', 'AGING', 'CATCH', 'CLASS', 'COWER', 'CRASS', 'DANDY', 'FOLLY', 
#  'GULLY', 'HATCH', 'HOUND', 'LABEL', 'LAPEL', 'MERRY', 'PAPER', 'PARER', 
#  'PARRY', 'RIPER', 'RUDER', 'SEVER', 'STASH', 'STATE', 'SWILL', 'TAUNT', 
#  'TRAIT', 'TRICE', 'TRITE']

for i in tqdm(range(len(prev_answers))):
    # freq_word = answers.pool[i]  
    # freq = zipf_frequency(freq_word, 'en', wordlist='best')
    # if freq > 2.5:
    #     failures = 0
    # for j in range(len(prev_answers)):
    answer = prev_answers[i]
    test_jordle = Jordle(prev_answers[i], starting_word)
    test_jordle.populate_banks()
    while len(test_jordle.final_guesses) < 6:
        # get results from the last guess before checking / trying again.
        test_jordle.get_results()

        if test_jordle.answer == test_jordle.guess:
            # print(f"Jordle found the answer after {len(test_jordle.final_guesses)} guesses.")
            scores[str(len(test_jordle.final_guesses))] += 1
            avg += len(test_jordle.final_guesses)
            break

        else:
            test_jordle.update_letter_banks()
            test_jordle.update_answer_pool()
            test_jordle.update_guessed_letters()
            test_jordle.choose_guess()

    if test_jordle.final_guesses[-1] != test_jordle.answer:
        failures.append(test_jordle.answer)
        scores['X'] += 1
        avg += 7 
        # print(f"Jordle did not guess the answer correctly after {len(test_jordle.final_guesses)} guesses.")

    # test_jordle.output()
avg /= len(prev_answers)
avg = round(avg, 3)
#     best_answers.append((answers.pool[i], avg, failures))

# best_answers.sort(key=lambda tup: tup[1])

# with open("best_starting_guesses_2.txt", "w") as file:
#     for i in range(len(best_answers)):
#         file.write(f'{i}. {best_answers[i][0]} {best_answers[i][1]} {best_answers[i][2]}\n')

print(scores)
print(avg)
print(failures)
score = list(scores.keys())
values = list(scores.values())
plt.bar(range(len(score)), values, tick_label=score)
plt.ylabel('Number of words')
plt.title("""Performance of Jordle starting with word '""" + starting_word +"""'""")
plt.xlabel('Number of Guesses')
plt.show()
