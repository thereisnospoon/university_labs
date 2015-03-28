import sppr5
import functools
from utils import print_table

e1 = ((1, 1),
      (1, 0.707, 1, 1, 0.5),
      (0.707, 1, 1, 1, 1, 1, 1, 1))

e2 = ((1, 1),
      (0.5, 1, 1, 1, 0.707),
      (0.354, 1, 1, 1, 1, 1, 0.707, 1))

p = sppr5.probs


def corrected_probabilities(probabilities, e, t=None):

	result = []

	def tij(i, j, t):
		if t is None:
			return 1
		else:
			return t[i][j]

	for i, row in enumerate(probabilities):

		s = 0
		for j, p_ij in enumerate(row):
			s += e[i][j] * tij(i, j, t) * p_ij

		result_row = []
		for j, p_ij in enumerate(row):
			result_row.append(e[i][j] * tij(i, j, t) * p_ij / s)

		result.append(result_row)

	return result


print('Probabilities')
print_table(p)

print('Probabilities with E1')
print_table(corrected_probabilities(p, e1))


def t_function(t, y_upper):
	return 1 + (y_upper - 1)/5*t


t1 = ((1, 1),
      (1, 1, 1, 1, 1),
      (t_function(3, 2), t_function(3, 1.414), t_function(3, 1.414), 1, 1, 1,
       t_function(3, 2), 1))


print('Probabilities with E2 and T1')
print_table(corrected_probabilities(p, e2, t1))