import itertools
import math

text = open('text.txt', encoding='utf-8').read()
print('Text length is {}'.format(len(text)))


def get_alphabet():
    alphabet = {chr(c) for c in range(ord('а'), ord('я') + 1) if chr(c) != 'ъ'}
    alphabet = alphabet | {' '}
    return alphabet


letters = get_alphabet()


def fix_symbol(symbol):
    if symbol not in letters:
        return ' '
    else:
        return symbol


def get_letter_frequencies():
    frequencies = {l: 0 for l in letters}
    for c in text:

        if c in frequencies:
            frequencies[c] += 1
        else:
            frequencies[' '] += 1

    for l in frequencies:
        frequencies[l] /= len(text)

    return frequencies


def text_bigramm_gen():
    i = 0
    while i + 1 < len(text):
        yield (fix_symbol(text[i]), fix_symbol(text[i + 1]))
        i += 2


bigramms = [bigramm for bigramm in text_bigramm_gen()]


def get_bigramm_frequencies():
    frequencies = {}
    for bigramm in bigramms:
        if bigramm not in frequencies:
            frequencies[bigramm] = 1
        else:
            frequencies[bigramm] += 1

    for bigramm in frequencies:
        frequencies[bigramm] /= (len(text) / 2)

    return frequencies


def get_Hn(frequencies, n):
    # for n = 1 case we should wrap single letters into tuples
    if n == 1:
        tempFreq = {tuple(l): frequencies[l] for l in frequencies}
        frequencies = tempFreq

    Hn = 0
    for zn in itertools.product(''.join(letters), repeat=n):
        if zn in frequencies:
            Hn -= frequencies[zn] * math.log2(frequencies[zn])

    return Hn / n


def print_frequencies(frequencies, columns, name):

    print(name)

    keys = [k for k in frequencies]
    for i in range(0, len(keys), columns):
        print(';  '.join(['{0:2s}: {1:5.4f}'.format(''.join(key), frequencies[key]) for key in keys[i: i + columns]]))

    print('')

letter_frequencies = get_letter_frequencies()
bigramm_frequencies = get_bigramm_frequencies()

print_frequencies(letter_frequencies, 5, 'Letters frequencies')
print_frequencies(bigramm_frequencies, 4, 'Bigramms frequencies')

print('H1 = {}'.format(get_Hn(letter_frequencies, 1)))
print('H2 = {}'.format(get_Hn(bigramm_frequencies, 2)))