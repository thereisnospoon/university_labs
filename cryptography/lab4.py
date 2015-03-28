import functools
import re
import itertools
from scipy.stats import norm


def lfsr(a, s):

	while True:
		new_s = functools.reduce(lambda x, y: (x + y) % 2, [a_and_s[0]*a_and_s[1] for a_and_s in zip(a, s)])
		output_s = s.pop(-1)
		s.insert(0, new_s)
		yield output_s


def geffe_generator(lfsr1, lfsr2, lfsr3):

	for xys in zip(lfsr1, lfsr2, lfsr3):
		yield xys[2]*xys[0] ^ (1 ^ xys[2])*xys[1]


def sequence(filename):

	text = open(filename, encoding='utf-8').read()
	text = re.sub(r'\D', '', text)
	return tuple(int(i) for i in text)


a1 = (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1)
a2 = (0, 0, 0, 0, 1, 1, 0, 1, 1)
a3 = (0, 0, 0, 0, 0, 0, 1, 0, 0, 1)

given_z = sequence('lab4_seq.txt')


def solve_system(m):

	betha = 1/m
	alpha = 0.01
	t2 = norm.ppf(1 - betha)
	t1 = norm.ppf(1 - alpha)
	N = (t1 * 3**0.5 + 2 * t2)**2
	C = N/4 + t1 * (3*N/16)**0.5

	return betha, N, C


def r_stat(x, z, n):

	i = 0
	r = 0
	for xz in zip(x, z):
		if i >= n:
			break
		r += xz[0] ^ xz[1]
		i += 1

	return r


def find_probable_keys(a, z):

	betha, N, C = solve_system(2**len(a))
	print('N = {}, C = {}, betha = {}'.format(N, C, betha))
	probable_keys = []
	for s in itertools.product((0, 1), repeat=len(a)):
		s_list = list(s)
		r = r_stat(lfsr(a, s_list[:]), z, N)
		if r < C:
			probable_keys.append(s_list)

	return probable_keys


def find_keys():

	print('Finding keys for L1')
	l1_keys = find_probable_keys(a1, given_z)
	print('Finding keys for L2')
	l2_keys = find_probable_keys(a2, given_z)

	print('Finding keys')
	keys = []
	for s1_s2 in itertools.product(l1_keys, l2_keys):
		for s3 in itertools.product((0, 1), repeat=len(a3)):

			s1 = list(s1_s2[0])
			s2 = list(s1_s2[1])
			s3_list = list(s3)

			correct_sequence = True
			for z in zip(given_z, geffe_generator(lfsr(a1, s1[:]),
			                                      lfsr(a2, s2[:]),
			                                      lfsr(a3, s3_list[:]))):

				if z[0] != z[1]:
					correct_sequence = False
					break

			if correct_sequence:
				keys.append((s1, s2, s3_list))

	return keys

for keys in find_keys():
	print(keys)