#!/usr/bin/python3
import argparse

from collections import deque

LANG_EN = 'en'
LANG_DE = 'de'

ALPHABET    = [chr(letter).upper() for letter in range(ord('A'), ord('Z') + 1)]
FREQUENCIES = {
    LANG_DE: [6.47, 1.93, 2.68, 4.83, 17.48, 1.65, 3.06, 4.23, 7.73, 0.27, 1.46, 3.39, 2.58, 9.84, 2.98, 0.96, 0.02, 7.54, 6.83, 6.13, 4.17, 0.94, 1.48, 0.04, 0.08, 1.14],
    LANG_EN: [8.12, 1.49, 2.71, 4.32, 12.02, 2.30, 2.03, 5.92, 7.31, 0.10, 0.69, 3.98, 2.61, 6.95, 7.68, 1.82, 0.11, 6.02, 6.28, 9.10, 2.88, 1.11, 2.09, 0.17, 2.11, 0.07]
}


def letter_to_number(letter: chr):
    return ALPHABET.index(letter.upper())


def sort_by_x(mapping: dict, index: int, reverse: bool):
    return {tuple[0]: tuple[1] for tuple in sorted(mapping.items(), key=lambda item: item[index], reverse=reverse)}


def sort_by_key(mapping: dict):
    return sort_by_x(mapping, 0, False)


def sort_by_value(mapping: dict):
    return sort_by_x(mapping, 1, True)


def get_plain_char(cipher: chr, key: chr):
    number_cipher = letter_to_number(cipher)
    number_key    = letter_to_number(key   )

    return ALPHABET[number_cipher - number_key]


def decode(cipher: str, key: str):
    plain = ''
    i     = 0

    for char in cipher.upper():
        if char in ALPHABET:
            key_char = key[i % len(key)]
            plain   += get_plain_char(char, key_char)
            i       += 1
        else:
            plain += char
    return plain


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input' , help='Input file with encrypted text', type=str                            , required=True)
    parser.add_argument('-l', '--length', help='Key length'                    , type=int, nargs='*'                 , required=True)
    parser.add_argument('-c', '--lang'  , help='Language'                      , type=str, choices=[LANG_EN, LANG_DE], required=True)

    args = parser.parse_args()

    # load input
    with open(args.input, 'r') as f:
        original_input = f.read().upper()
        input          = ''.join([c for c in original_input if c in ALPHABET]).upper()

    for length in args.length:
        key = ''

        # process different key lengths
        for start_index in range(0, length):
            collected_frequencies = {}
            letters_found         = 0

            # count
            for i in range(start_index, len(input), length):
                c = input[i]

                if c not in collected_frequencies:
                    collected_frequencies[c] = 1
                else:
                    collected_frequencies[c] += 1
                letters_found += 1

            # calculate frequencies
            for c, f in collected_frequencies.items():
                collected_frequencies[c] = f / letters_found

            # fill blanks
            for c in ALPHABET:
                if c not in collected_frequencies.keys():
                    collected_frequencies[c] = 0

            # sort alphabet
            sorted_frequencies = sort_by_key(collected_frequencies)

            deque_collected_chars       = deque(char      for char      in sorted_frequencies.keys())
            deque_collected_frequencies = deque(frequency for frequency in sorted_frequencies.values())

            # collect probabilities
            probabilities        = {}
            language_frequencies = FREQUENCIES[args.lang]

            for shift in range(0, len(language_frequencies)):
                probabilities[shift] = 0

                for i in range(0, len(deque_collected_frequencies)):
                    probabilities[shift] += deque_collected_frequencies[i] * language_frequencies[i]

                deque_collected_chars      .rotate(-1)
                deque_collected_frequencies.rotate(-1)

            # sort probabilities to get the most probable
            sorted_probabilities = sort_by_value(probabilities)

            # convert shift index with most probability to letter and add to key
            first_key = list(sorted_probabilities.keys())[0]
            key += ALPHABET[first_key]

        # output result
        print('-' * 30)
        print(f'Key length: {length}')
        print(f'Key: {key}')
        print(f'Plain text: {decode(original_input, key)}')
