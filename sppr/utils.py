def print_table(table):

	for row in table:
		s = ''
		for value in row:
			s += '{0:8.3f}'.format(value)
		print(s)