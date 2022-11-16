# Should grab every 5 letter word from Scrabble Dictionary.
dict_file = open('dictionary.txt', 'r')
words = dict_file.readlines()
count = 0

new_words = []

for word in words:
    # strip word just to ensure no newline chars.
    stripped_word = word.strip()
    if len(stripped_word) == 5:
        new_words.append(stripped_word)
        count += 1

dict_file.close()

# now that we have the new words, fill them into the new file.
new_file = open('5_letter_dict', 'w')
for word in new_words:
    new_file.write(word)
    new_file.write('\n')

new_file.close()