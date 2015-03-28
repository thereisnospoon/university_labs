import re
import fractions
import itertools

lab_text = open('lab2_cyph.txt', encoding='utf-8').read()
lab_text = re.sub(r'\W', '', lab_text)

m = 31


def get_bigramms(text):
	i = 1
	while i < len(text):
		yield text[i - 1: i + 1]
		i += 2


def count_bigramm_frequencies(text):
	frequencies = {}
	for bigramm in get_bigramms(text):
		if bigramm in frequencies:
			frequencies[bigramm] += 1
		else:
			frequencies[bigramm] = 1

	frequencies_tuples = ((bigramm, frequency) for bigramm, frequency in frequencies.items())
	return sorted(frequencies_tuples, key=lambda pair: pair[1], reverse=True)


def reverse_by_mod(a, m):

	if a == 1:
		return a

	a_ = a if a > 0 else m + a

	if fractions.gcd(a_, m) != 1:
		raise ValueError('gcd of {} and {} is not 1'.format(a, m))

	# print('Finding reverse of {} by mod {}'.format(a, m))

	def get_q_and_r(left, right):
		q = left // right
		r = left % right
		return q, r

	q1, r1 = get_q_and_r(m, a_)
	q = {1: q1}
	r = {1: r1}
	i = 2
	while r[i - 1] != 1:
		q[i], r[i] = get_q_and_r(a_ if i == 2 else r[i - 2], r[i - 1])
		i += 1

	i = 1
	pi_1, pi_2 = 1, 0
	pi = 0
	while i in q:
		pi = -q[i]*pi_1 + pi_2
		pi_1, pi_2 = pi, pi_1
		i += 1

	assert pi*a % m == 1

	return pi


def alphabet():
	letters = []
	for i in range(ord('а'), ord('я') + 1):
		if chr(i) not in {'ё', 'ъ'}:
			letters.append(chr(i))

	return letters


def bigramm_number(bigramm):
	letters = alphabet()
	return letters.index(bigramm[0])*len(letters) + letters.index(bigramm[1])


def bigramm_value(number):
	x1 = number // m
	x2 = number % m
	letters = alphabet()
	return letters[x1] + letters[x2]


def decode_text(text, a, b):
	reverse_a = reverse_by_mod(a, m**2)
	decoded_text = ''
	for bigramm in get_bigramms(text):
		decoded_text += bigramm_value((reverse_a*(bigramm_number(bigramm) - b)) % m**2)

	return decoded_text


def try_to_decode(text):
	possible_x_pairs = itertools.permutations(['ст', 'но', 'то', 'на', 'ен'], 2)
	possible_y_pairs = itertools.permutations([bigramm[0] for bigramm in count_bigramm_frequencies(text)[0:5]], 2)

	result = open('result.txt', mode='w', encoding='utf-8')
	keys_cache = set()

	for values in itertools.product(possible_x_pairs, possible_y_pairs):

		x1 = bigramm_number(values[0][0])
		x2 = bigramm_number(values[0][1])

		y1 = bigramm_number(values[1][0])
		y2 = bigramm_number(values[1][1])
		y_diff = y1 - y2

		gcd = fractions.gcd(x1 - x2, m**2)
		if gcd != 1:
			print("GCD of {} and {} is {}".format(x1 - x2, m**2, gcd))
			if y_diff % gcd == 0:
				print('But y1 - y2 can be divided by gcd')
			continue

		reverse_x_diff = reverse_by_mod(x1 - x2, m**2)

		a = (reverse_x_diff * y_diff) % m**2
		b = (y1 - a*x1) % m**2

		if (a, b) in keys_cache:
			continue
		else:
			keys_cache.add((a, b))

		if fractions.gcd(a, m**2) != 1:
			continue

		result.write('x1 = {}, x2 = {}; y1 = {}, y2 = {}; a = {}, b = {}. Text: {}'
						.format(bigramm_value(x1), bigramm_value(x2), bigramm_value(y1),
		                        bigramm_value(y2), a, b, decode_text(text, a, b) + '\n'))

	result.close()

	# x1 = bigramm_number('то')
	# x2 = bigramm_number('на')
	#
	# y1 = bigramm_number('ен')
	# y2 = bigramm_number('юи')
	# y_diff = y1 - y2
	#
	# gcd = fractions.gcd(x1 - x2, m**2)
	# if gcd != 1:
	# 	print("GCD of {} and {} is {}".format(x1 - x2, m**2, gcd))
	# 	if y_diff % gcd == 0:
	# 		print('But y1 - y2 can be divided by gcd')
	#
	# reverse_x_diff = reverse_by_mod(x1 - x2, m**2)
	#
	# a = (reverse_x_diff * y_diff) % m**2
	# b = (y1 - a*x1) % m**2
	#
	# print('x1 = {}, x2 = {}; y1 = {}, y2 = {}; a = {}, b = {}. Text: {}'
	# 	             .format(x1, x2, y1, y2, a, b, decode_text(text, a, b) + '\n'))


def encode_text(filename, a, b):

	assert fractions.gcd(a, m**2) == 1

	text = open(filename, encoding='utf-8').read()
	text = text.lower()
	text = re.sub(r'\W', '', text)
	text = re.sub(r'\d', '', text)
	text = re.sub('ъ', 'ь', text)
	text = re.sub('ё', 'е', text)

	encoded_text = open('encoded.txt', mode='w', encoding='utf-8')
	for bigramm in get_bigramms(text):
		encoded_text.write(bigramm_value((a*bigramm_number(bigramm) + b) % m**2))

	encoded_text.close()

# encoded_text = open('encoded.txt', encoding='utf-8').read()
try_to_decode(lab_text)
# encode_text('test.txt', 7, 8)