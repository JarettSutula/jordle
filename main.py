from jordle import Jordle

test_jordle = Jordle("ember", "arise")
test_jordle.populate_banks()
while len(test_jordle.final_guesses) < 6:
    # get results from the last guess before checking / trying again.
    test_jordle.get_results()

    if test_jordle.answer == test_jordle.guess:
        print(f"Jordle found the answer after {len(test_jordle.final_guesses)} guesses.")
        break

    else:
        test_jordle.update_letter_banks()
        test_jordle.update_answer_pool()
        test_jordle.update_guessed_letters()
        test_jordle.choose_guess()

if test_jordle.final_guesses[-1] != test_jordle.answer:
    print(f"Jordle did not guess the answer correctly after {len(test_jordle.final_guesses)} guesses.")

test_jordle.output()