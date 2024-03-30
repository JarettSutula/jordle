from jordle import Jordle
from tqdm import tqdm

prev_answers = []
with open('previous_wordle_answers.txt', 'r') as file:
    line = file.readline()
    prev_answers = line.split()

scores = {'1': 0, '2': 0, '3': 0, '4':0, '5':0, '6':0, 'X':0}
failures = []
for i in tqdm(range(len(prev_answers))):
    answer = prev_answers[i]
    test_jordle = Jordle("arise", answer)
    test_jordle.populate_banks()
    while len(test_jordle.final_guesses) < 6:
        # get results from the last guess before checking / trying again.
        test_jordle.get_results()

        if test_jordle.answer == test_jordle.guess:
            # print(f"Jordle found the answer after {len(test_jordle.final_guesses)} guesses.")
            scores[str(len(test_jordle.final_guesses))] += 1
            break

        else:
            test_jordle.update_letter_banks()
            test_jordle.update_answer_pool()
            test_jordle.update_guessed_letters()
            test_jordle.choose_guess()

    if test_jordle.final_guesses[-1] != test_jordle.answer:
        failures.append(test_jordle.answer)
        scores['X'] += 1
        # print(f"Jordle did not guess the answer correctly after {len(test_jordle.final_guesses)} guesses.")

    # test_jordle.output()
print(scores)
