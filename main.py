from jordle import Jordle

test_jordle = Jordle("ember", "dream")
test_jordle.populate_banks()
while len(test_jordle.final_guesses) < 6:
    if test_jordle.answer == test_jordle.guess:
        print(f"Jordle found the answer after {len(test_jordle.final_guesses)} guesses.")

    else:
        test_jordle.get_results()
        test_jordle.update_letter_banks()
        test_jordle.update_guessed_letters()
        test_jordle.choose_guess()
        input()

if test_jordle.final_results[-1] != test_jordle.answer:
    print(f"Jordle did not guess the answer correctly after {len(test_jordle.final_guesses)} guesses.")

print(f"The Wordle Answer was {test_jordle.answer}. Jordle's guesses:")
for i in range(len(test_jordle.final_guesses)):
    print(f"{i+1} {test_jordle.final_results[i]}")