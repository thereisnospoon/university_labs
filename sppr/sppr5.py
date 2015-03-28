import itertools as itools
import numpy as np
import functools as ftools
import numpy.linalg as linalg
import math

p_ = [[0.9, 0.2],
      [0.1, 0.2, 0.4, 0.4, 0.6],
      [0.8, 0.7, 0.5, 0.05, 0.2, 0.05, 0.5, 0.05]]

c = {(0, 1): {(0, 4): 0.3, (1, 4): -0.3},
     (0, 2): {(0, 0): 0.7, (1, 0): 0.3, (0, 5): -0.3},
     (1, 2): {(0, 0): 0.3, (0, 4): 0.3, (0, 6): 0.3,
              (1, 2): 0.3, (2, 1): 0.3, (2, 2): 0.7,
              (3, 2): 0.3, (3, 6): 0.3,
              (4, 0): 0.3, (4, 3): 0.3, (4, 4): 0.3, (4, 6): 0.3},

     (0, 3): {(0, 2): 0.3, (0, 4): 0.7},
     (1, 3): {(0, 0): 0.3, (0, 1): 0.3, (0, 4): 0.3,
              (1, 0): -0.3, (1, 1): 0.3,
              (2, 0): -0.3, (2, 1): 0.3,
              (4, 0): 0.3, (4, 1): 0.3, (4, 3): 0.3, (4, 4): 0.3},
     (2, 3): {(0, 0): 0.7, (0, 1): 0.3, (0, 2): 0.3, (0, 3): -0.3, (0, 4): 0.3,
              (1, 4): -0.3, (2, 4): -0.3, (6, 0): 0.3}
}

N_ = 4
R_dimensions = {3: 5}


def normalize_p_():
    for i, row in enumerate(p_):
        row_sum = ftools.reduce(lambda x, y: x + y, row)
        p_[i] = [pij / row_sum for pij in row]


normalize_p_()


def get_c(i1, j1, i2, j2):
    if i1 > i2:
        i1, i2 = i2, i1
        j1, j2 = j2, j1

    if (j1, j2) in c[(i1, i2)]:
        return c[(i1, i2)][(j1, j2)]
    else:
        return 0


def cond_p(i, alts):
    p_mult = 1
    for m in range(len(alts)):
        if m != i:
            p_mult *= p_[m][alts[m]]

    c_mult = 1
    for m in range(len(alts) - 1):
        l = m + 1
        while l < len(alts):
            c_mult *= (get_c(m, alts[m], l, alts[l]) + 1)
            l += 1

    return p_mult * c_mult


def get_cond_p():
    p = {}
    for alts in itools.product(range(len(p_[0])),
                               range(len(p_[1])),
                               range(len(p_[2]))):
        p[alts] = {i: cond_p(i, alts) for i in range(len(alts))}

    return p


def get_normed_cond_p():
    cond_ps = get_cond_p()
    for f in range(len(p_)):
        for alt in range(len(p_[f])):
            cases_to_norm = []
            sum = 0

            for case in cond_ps:
                if case[f] == alt:
                    cases_to_norm.append(case)
                    sum += cond_ps[case][f]

            for case in cases_to_norm:
                cond_ps[case][f] /= sum

    return cond_ps


def print_cond_ps(cond_ps):
    keys = sorted([key for key in cond_ps])
    for key in keys:
        s = "{0} "
        for i in range(len(key)):
            s += "{" + str(i + 1) + ":4.3f} "

        ps = cond_ps[key]
        values = [value for p, value in ps.items()]
        print(s.format(key, *values))


def get_p_coeffs(i, j, cond_ps):
    coeffs = []
    if i == len(p_) - 1:
        l = 0
    else:
        l = i + 1
    for j2 in range(len(p_[l])):
        coeff = 0
        for case in cond_ps:
            if case[i] == j and case[l] == j2:
                coeff += cond_ps[case][l]
        coeffs.append(coeff)

    return coeffs


def get_matrixes(cond_ps):
    Ps = []
    for i in range(len(p_)):
        Ps.append(np.matrix([get_p_coeffs(i, j, cond_ps) for j in range(len(p_[i]))]))
    return Ps


def get_probabilities():
    Ps = get_matrixes(get_normed_cond_p())

    print("P[i]'s")
    for i, Pi in enumerate(Ps):
        print("P[{}]:".format(i))
        for row in Pi.getA().tolist():
            str_row = ""
            for el in row:
                str_row += "{0:4.3f}  ".format(el)
            print(str_row)
        print("")

    eig_vals, eig_vectors = linalg.eig(ftools.reduce(lambda p1, p2: p1.dot(p2), Ps))

    EPS = 1e-3
    for i, eig_val in enumerate(eig_vals):
        if math.fabs(1 - eig_val) < EPS:
            x1 = eig_vectors[:, i]

    probabilities = []
    for i in reversed(range(len(Ps))):
        probabilities.insert(0, Ps[i].dot(x1))
        x1 = probabilities[0]

    list_probabilities = [p.getA1().tolist() for p in probabilities]
    for i, pi in enumerate(list_probabilities):
        pi_sum = ftools.reduce(lambda p1, p2: p1 + p2, pi)
        list_probabilities[i] = [pij / pi_sum for pij in pi]

    return list_probabilities

def cond_r(i, j, case):

    def product(curr_k):
        prod = 1
        for m in range(len(p_)):
            prod *= get_c(m, case[m], i, curr_k) + 1
        return prod

    top = 1/N_*product(j)
    bottom = 0
    for k in range(R_dimensions[i]):
        bottom += 1/N_*product(k)

    return top/bottom

def get_effectiveness(cond_probabilities, probabilities):

    def get_case_probability(case):
        return cond_probabilities[case][0]*probabilities[0][case[0]]

    N = len(p_)
    R = []
    for i in range(N, N_):
        Ri = []
        for j in range(R_dimensions[i]):
            rij = 0
            for case in itools.product(*[range(len(pi)) for pi in p_]):
                rij += cond_r(i, j, case)*get_case_probability(case)
            Ri.append(rij)
        R.append(Ri)

    return R

# print("Conditional probabilities:")
conditional_probs = get_normed_cond_p()
# print_cond_ps(conditional_probs)

probs = get_probabilities()
# print("Probabilities:")
# for i, p_i in enumerate(probs):
#     text = "F{}: ".format(i)
#     for j, p_ij in enumerate(p_i):
#         text += " {0:4.3f}; ".format(p_ij)
#     print(text)
#
# print("Effectiveness")
# print(get_effectiveness(conditional_probs, probs))