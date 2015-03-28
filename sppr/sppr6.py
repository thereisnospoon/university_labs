import functools
from utils import print_table


eta_f1 = ((0.75, 0.62), (0.12, 0.58), (0.57, 0.05))
eta_f2 = ((0.32, 0.57), (0.59, 0.32), (0.74, 0.79), (0.35, 0.14), (0.52, 0.21))
eta_f3 = ((0.91, 0.21), (0.76, 0.28), (0.17, 0.4), (0.23, 0.23), (0.15, 0.26),
          (0.58, 0.62), (0.27, 0.28))

w_f1 = ((0.81, 0.87), (0.2, 0.91), (0.73, 0.37))
w_f2 = ((0.59, 0.83), (0.81, 0.58), (0.91, 0.9), (0.74, 0.53), (0.54, 0.52))
w_f3 = ((0.81, 0.33), (0.83, 0.38), (0.62, 0.69), (0.86, 0.21),
        (0.84, 0.33), (0.83, 0.8), (0.8, 0.32))

eta = (eta_f1, eta_f2, eta_f3)
w = (w_f1, w_f2, w_f3)


def aggregated_risk_values(unaggregated_values):

	result_values = []

	def aggregated_value(values):
		return 1 - functools.reduce(lambda x, y: x * y, (1 - x for x in values))

	for factor_row in unaggregated_values:
		result_values.append(list(map(aggregated_value, factor_row)))

	return result_values


def pi_function(x, b, c):

	def s(x, a, b, c):

		if x <= a:
			return 0
		if a <= x <= b:
			return 2 * ((x - a) / (c - a)) ** 2
		if b <= x <= c:
			return 1 - 2 * ((x - c) / (c - a)) ** 2
		if x >= c:
			return 1

	if x <= c:
		return s(x, c - b, c - b / 2, c)
	else:
		return 1 - s(x, c, c + b / 2, c + b)


def class_membership_value(config, values, membership_function):

	mult_value = 1
	for i, j in enumerate(config):
		mult_value *= 1 - membership_function(values[i][j])

	return 1 - mult_value**(1 / len(config))


def general_class_membership_value(config, etas, omegas, mf1, mf2):

	return (class_membership_value(config, etas, mf1) *
		class_membership_value(config, omegas, mf2))**0.5


def class_membership_table(config, etas, omegas):

	intervals = ((0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1))
	table = []
	for w_interval in intervals[:]:
		table.append(
			list([general_class_membership_value(config, etas, omegas,
			                                     functools.partial(pi_function, b=eta_interval[0], c=eta_interval[1]),
			                                     functools.partial(pi_function, b=w_interval[0], c=w_interval[1]))
			      for eta_interval in intervals[:]]))

	return table


aggregated_eta = aggregated_risk_values(eta)
aggregated_omega = aggregated_risk_values(w)

s1_table = class_membership_table((0, 1, 3), aggregated_eta, aggregated_omega)
s2_table = class_membership_table((2, 0, 0), aggregated_eta, aggregated_omega)

print('Etas: ')
print_table(aggregated_eta)

print('Omegas')
print_table(aggregated_omega)

print('S1 classes')
print_table(s1_table)

print('S2 classes')
print_table(s2_table)