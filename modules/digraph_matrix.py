import sys
import os
import modules.open_digraph as od
import random

root = os.path.normpath(os.path.join(__file__, './../..'))
sys.path.append(root)


def printMatrix(m):
    print("[")
    for i in range(len(m)):
        print(m[i])
    print("]")


def random_int_liste(n, bound):
    """
    Génère une liste de n entiers aléatoires entre 0 et bound.

    @param n: Nombre d'éléments dans la liste
    @param bound: Valeur maximale des entiers générés (exclus)
    @ return: Liste d'entiers aléatoires
    """
    return [random.randrange(0, bound) for i in range(n)]


def random_int_matrix(n, bound, null_diag=True):
    res = [random_int_liste(n, bound) for i in range(n)]
    if null_diag:
        for i in range(n):
            res[i][i] = 0
    return res


def random_symetric_int_matrix(n, bound, null_diag=True):
    res = random_int_matrix(n, bound, null_diag)
    for i in range(n):
        for j in range(n):
            res[i][j] = res[j][i]
    return res


def random_oriented_int_matrix(n, bound, null_diag=True):
    res = random_int_matrix(n, bound, null_diag)
    for i in range(n):
        for j in range(n):
            if (res[i][j] != 0):
                res[j][i] = 0
    return res


def random_triangular_int_matrix(n, bound, null_diag=True):
    res = random_int_matrix(n, bound, null_diag)
    for i in range(n):
        for j in range(n):
            if (i > j):
                res[i][j] = 0
    return res


def graph_from_adjcency_matrix(M):
    taille = len(M)
    g = od.open_digraph.empty()
    for _ in range(taille):
        g.add_node('', {}, {})

    for i in range(taille):
        for j in range(taille):
            multiplicite = M[i][j]
            if (multiplicite != 0):
                for k in range(multiplicite):
                    g.add_edge(i, j)
    return g

# A = [   [0, 1, 1, 0, 0],
#         [0, 0 , 0 , 1 , 2],
#         [0, 0, 0, 2, 0],
#         [1, 0, 0, 0, 1],
#         [0, 0, 0, 0, 0] ]

# Juste pour éviter que le code ne s'éxécute à chaque import du module


if __name__ == "__main__":
    # Matrix = random_int_liste(5, 100)
    # Matrix = random_int_matrix(5, 100, True)
    # Matrix = random_symetric_int_matrix(5, 100, True)
    Matrix = random_oriented_int_matrix(5, 100)
    # Matrix = random_triangular_int_matrix(5, 100)
    printMatrix(Matrix)
    # graph_from_adjcency_matrix(A)
