import re
import random
import fractions
import functools


def gorner_scheme(x, a, m):

	if x >= m:
		raise ValueError('x should be less then m (x = {}, m = {})'.format(x, m))

	a_bin = re.sub('^0b', '', bin(a))
	result = 1
	for ak in a_bin:
		result = result**2 % m
		result = result*x**int(ak) % m

	return result


def ferma_test(p, k):

	for _ in range(k):
		x = random.randint(1, p - 1)
		while fractions.gcd(x, p) != 1:
			x = random.randint(1, p - 1)

		if gorner_scheme(x, p - 1, p) != 1:
			return False

	return True


def is_strong_prime(p, a):

	d = p - 1
	s = 0
	while d % 2 == 0:
		d //= 2
		s += 1

	if gorner_scheme(a, d, p) == 1:
		return True
	else:
		for r in range(s):
			if gorner_scheme(a, 2**r * d, p) == p - 1:
				return True

	return False


def is_prime(p):

	for a in (2, 3, 5, 7):
		if not is_strong_prime(p, a):
			return False

	return True


def lfsr():

	s = list(random.randint(0, 1) for _ in range(20))
	a = (0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)

	while True:
		s_new = functools.reduce(lambda x, y: x ^ y, (sa[0]*sa[1] for sa in zip(a, s)))
		s.insert(0, s_new)
		yield s.pop(-1)


def number_generator(n0, n1):

	if n0 >= n1:
		raise ValueError('n1 should be greater then n0. (n0 = {}, n1 = {})'.format(n0, n1))

	binary_generator = lfsr()
	number_length = len(re.sub('^0b', '', bin(n1)))

	current_number = []
	for k in range(number_length):
		current_number.append(next(binary_generator))

	while True:

		current_number.pop(0)
		current_number.append(next(binary_generator))

		num = int(''.join((str(i) for i in current_number)), 2)
		if n0 <= num <= n1:
			yield num


def prime_generator(n0, n1):

	for x in number_generator(n0, n1):

		m = x if x % 2 != 0 else x + 1
		for i in range((n1 - m) // 2 + 1):

			p = m + 2*i
			if p > n1:
				continue

			if ferma_test(p, 8) and is_prime(p):
				yield p
				break


def egcd(a, b):
		x, y, u, v = 0, 1, 1, 0
		while a != 0:
			q, r = b // a, b % a
			m, n = x - u*q, y - v*q
			b, a, x, y, u, v = a, r, u, v, m, n
		gcd = b
		return gcd, x, y


def modinv(a, m):

	gcd, x, y = egcd(a, m)
	if gcd != 1:
		return None  # modular inverse does not exist
	else:
		return x % m


def rsa_numbers_generator():

	pg = prime_generator(100, 255)
	p, q = next(pg), next(pg)
	n = p * q

	phi_n = (p - 1)*(q - 1)

	for e in number_generator(2, phi_n - 1):
		if fractions.gcd(e, phi_n) == 1:
			break

	d = modinv(e, phi_n)
	assert 1 < d < phi_n

	return p, q, n, e, d


def rsa_encrypt(M):

	p, q, n, e, d = rsa_numbers_generator()

	if M >= n:
		raise ValueError('Message should be less then n')

	C = gorner_scheme(M, e, n)

	return n, e, d, C


def rsa_decrypt(C, n, d):

	if C >= n:
		raise ValueError('C should be less then n')

	return gorner_scheme(C, d, n)


def get_signature(M):

	p, q, n, e, d = rsa_numbers_generator()
	return gorner_scheme(M, d, n), n, e


def simulate_confidential_distribution():

	# generate rsa pairs
	while True:
		p, q, n, e, d = rsa_numbers_generator()
		p1, q1, n1, e1, d1 = rsa_numbers_generator()

		if n <= n1:
			break

	print('p = {}, q = {}, e = {}, d = {}'.format(p, q, e, d))
	print('p1 = {}, q1 = {}, e1 = {}, d1 = {}'.format(p1, q1, e1, d1))

	# abonent A values
	k = next(number_generator(1, n - 1))

	print('New key to distribute: k = {}'.format(k))

	S = gorner_scheme(k, d, n)
	S1 = gorner_scheme(S, e1, n1)
	k1 = gorner_scheme(k, e1, n1)

	# abonent B finds k and check whether it's valid
	k_of_b = gorner_scheme(k1, d1, n1)
	S_of_b = gorner_scheme(S1, d1, n1)

	assert k_of_b == gorner_scheme(S_of_b, e, n)
	print('Authentication is successful')

	assert k == k_of_b
	print('Decrypted for abonent B key: k = {}'.format(k_of_b))

simulate_confidential_distribution()