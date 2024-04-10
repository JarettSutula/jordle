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
starting_word = "crane"
# crane outcomes v1.01
# {'1': 1, '2': 79, '3': 320, '4': 355, '5': 165, '6': 65, 'X': 29}
# 3.902
# ['AGING', 'ARDOR', 'DANDY', 'FERRY', 'FOLLY', 'FOYER', 'GONER', 'HATCH', 
#  'HUNCH', 'LATTE', 'MARRY', 'MASSE', 'MERRY', 'NATAL', 'PAPER', 'PARER', 
#  'PIPER', 'REVEL', 'RIPER', 'RUDER', 'SASSY', 'SENSE', 'SEVER', 'SOWER', 
#  'STATE', 'SURER', 'TASTE', 'TASTY', 'TAUNT']
# crane outcomes v1.02 (man we got worse :c)
# {'1': 1, '2': 84, '3': 325, '4': 332, '5': 164, '6': 67, 'X': 41}
# 3.926
# ['ABATE', 'BOOBY', 'BOOZY', 'COCOA', 'COWER', 'DANDY', 'FERRY', 'FINER', 
#  'FOLLY', 'FOYER', 'FROZE', 'GAMER', 'GONER', 'HATCH', 'HATER', 'HUNCH', 
#  'HUTCH', 'INFER', 'JAUNT', 'KAZOO', 'LATTE', 'LEDGE', 'MASSE', 'MERRY', 
#  'PARER', 'PIPER', 'REVEL', 'RIPER', 'RUDER', 'SASSY', 'SEVER', 'SMITE', 
#  'SOWER', 'STASH', 'STEED', 'SURER', 'TASTE', 'TASTY', 'TAUNT', 'VERGE', 
#  'VERVE']

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
            test_jordle.choose_guess_v2()

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
