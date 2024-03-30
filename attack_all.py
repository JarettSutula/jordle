from jordle import Jordle
from tqdm import tqdm
import matplotlib.pyplot as plt

prev_answers = []
with open('previous_wordle_answers.txt', 'r') as file:
    line = file.readline()
    prev_answers = line.split()

scores = {'1': 0, '2': 0, '3': 0, '4':0, '5':0, '6':0, 'X':0}
failures = []
avg = 0
starting_word = "arise"
for i in tqdm(range(len(prev_answers))):
    answer = prev_answers[i]
    test_jordle = Jordle(starting_word, answer)
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
print(scores)
print(avg)
score = list(scores.keys())
values = list(scores.values())
plt.bar(range(len(score)), values, tick_label=score)
plt.ylabel('Number of words')
plt.title("""Performance of Jordle starting with word '""" + starting_word +"""'""")
plt.xlabel('Number of Guesses')
plt.show()
