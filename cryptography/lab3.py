import re
import functools
import random

m = 32


def alphabet():
	letters = []
	for i in range(ord('а'), ord('я') + 1):
		if chr(i) not in {'ё'}:
			letters.append(chr(i))

	return letters


def text_from_file(filename):

	text = open(filename, encoding='utf-8').read()
	text = text.lower()
	text = re.sub(r'\W', '', text)
	text = re.sub(r'\d', '', text)
	text = re.sub('ё', 'е', text)

	return text


def partition(iterable, chunk_size):

	for i in range(0, len(iterable), chunk_size):
		yield iterable[i: i + chunk_size]


def apply_by_module(a, b, f):

	letters = alphabet()
	return ''.join([letters[(f(letters.index(pair[0]), letters.index(pair[1]))) % m] for pair in zip(a, b)])


def encode(text, key):

	encoded_chunks = []
	for chunk in partition(text, len(key)):
		encoded_chunks.append(apply_by_module(chunk, key, lambda x, y: x + y))

	return ''.join(encoded_chunks)


def decode(text, key):

	return ''.join([apply_by_module(chunk, key, lambda x, y: x - y) for chunk in partition(text, len(key))])


def count_frequencies(text):

	frequencies = {}
	for letter in text:
		if letter in frequencies:
			frequencies[letter] += 1
		else:
			frequencies[letter] = 1

	return frequencies


def phi(text):

	frequencies = count_frequencies(text)

	return functools.reduce(lambda x, y: x + y,
	                        [n_t*(n_t - 1) for n_t in frequencies.values()])


def get_index(text):

	n = len(text)
	return phi(text)/n/(n - 1)


def random_key(r):

	letters = alphabet()
	return ''.join([letters[random.randint(0, m - 1)] for i in range(r)])


def D(text, j):

	n = len(text)
	value = 0
	for i in range(0, n):

		shifted_index = i + j % n
		if shifted_index < n and text[i] == text[shifted_index]:
			value += 1

	return value


def most_frequent(text):
	return max(*((letter, value) for letter, value in count_frequencies(text).items()), key=lambda pair: pair[1])[0]


def hack(text, r, x):

	letters = alphabet()
	x = letters.index(x)
	keys = []
	for i in range(r):
		chunk = text[i::r]
		y = letters.index(most_frequent(chunk))
		keys.append(letters[(y - x) % m])

	return ''.join(keys)

lab_text = text_from_file('test.txt')
given_text = text_from_file('lab3_enc.txt')

print('Indexes for different r')
print({len(key): get_index(encode(lab_text, key))
       for key in map(random_key, [1, 2, 3, 4, 5, 20])})

print('Dj values: {}'.format(sorted(((j, D(given_text, j)) for j in range(2, 15, 1)), key=lambda pair: pair[1],
                                    reverse=True)))

print('Given text:\n{}'.format(given_text))
calculated_key = hack(given_text, 14, 'о')
print('Calculated key = {}'.format(calculated_key))
key = 'вшекспирбуря'
print('Corrected key = {}'.format(key))
print(decode(given_text, calculated_key))