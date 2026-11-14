import sys
import os
import unittest
import random
import itertools

root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root)
from modules.open_digraph import node
from modules.open_digraph import open_digraph
from modules.bool_circ import bool_circ



def valeurs_sorties(circ):
    """
    Renvoie les valeurs ('0' ou '1') portées par les sorties d'un circuit
    booléen évalué, dans l'ordre de ses sorties.
    """
    valeurs = []
    for output_id in circ.g.get_output_ids():
        sortie = circ.g.get_node_by_id(output_id)
        parent_id = list(sortie.get_parents().keys())[0]
        valeurs.append(circ.g.get_node_by_id(parent_id).get_label())
    return valeurs


class InitTest(unittest.TestCase):

    def test_init_node(self):
        n0 = node(0, 'i', {}, {1: 1})
        self.assertEqual(n0.id, 0)
        self.assertEqual(n0.label, 'i')
        self.assertEqual(n0.parents, {})
        self.assertEqual(n0.children, {1: 1})
        self.assertIsInstance(n0, node)

    def test_init_node_2(self):
        n1 = node(545, 'b', {1: 2, 2: 2}, {3: 10, 4: 0, 5: 4})
        self.assertEqual(n1.id, 545)
        self.assertEqual(n1.label, 'b')
        self.assertEqual(n1.parents, {1: 2, 2: 2})
        self.assertEqual(n1.children, {3: 10, 4: 0, 5: 4})
        self.assertIsInstance(n1, node)


class NodeTest(unittest.TestCase):

    def setUp(self):
        self.n0 = node(0, 'a', [], [1])

    def test_get_id(self):
        self.assertEqual(self.n0.get_id(), 0)

    def test_get_label(self):
        self.assertEqual(self.n0.get_label(), 'a')

    def test_copy_node(self):
        n = node(1, 'x', {2: 1}, {3: 2})
        n_copy = n.copy()

        self.assertIsNot(n, n_copy)

        self.assertEqual(n.id, n_copy.id)
        self.assertEqual(n.label, n_copy.label)
        self.assertEqual(n.parents, n_copy.parents)
        self.assertEqual(n.children, n_copy.children)

        self.assertIsNot(n.parents, n_copy.parents)
        self.assertIsNot(n.children, n_copy.children)


class CopyTest(unittest.TestCase):

    def test_copy(self):
        n0 = node(0, 'i', {}, {1: 1})
        n1 = node(545, 'b', {1: 2, 2: 2}, {3: 10, 4: 0, 5: 4})

        g = open_digraph([0], [545], [n0, n1])
        g_copy = g.copy()

        self.assertIsNot(g_copy, g)

        self.assertEqual(g.inputs, g_copy.inputs)
        self.assertEqual(g.outputs, g_copy.outputs)
        self.assertIsNot(g.inputs, g_copy.inputs)
        self.assertIsNot(g.outputs, g_copy.outputs)

        for node_original, node_copy in zip(g.get_nodes(), g_copy.get_nodes()):
            self.assertIsNot(node_original, node_copy)
            self.assertEqual(node_original.id, node_copy.id)
            self.assertEqual(node_original.label, node_copy.label)
            self.assertEqual(node_original.parents, node_copy.parents)
            self.assertEqual(node_original.children, node_copy.children)

        g_copy.add_input_id(999)
        g_copy.get_node_by_id(0).set_label('z')

        self.assertNotIn(999, g.inputs)
        self.assertNotEqual(g.get_node_by_id(0).get_label(),
                            g_copy.get_node_by_id(0).get_label())


class AddEdgeTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'a', {}, {})
        self.n1 = node(1, 'b', {}, {})
        self.n2 = node(2, 'c', {}, {})
        self.g = open_digraph([0], [1], [self.n0, self.n1, self.n2])

    def test_add_edge(self):
        self.g.add_edge(0, 1)
        self.assertEqual(self.n0.get_children(), {1: 1})
        self.assertEqual(self.n1.get_parents(), {0: 1})

    def test_add_edges(self):
        self.g.add_edges([(0, 1), (1, 2)])
        self.assertEqual(self.n0.get_children(), {1: 1})
        self.assertEqual(self.n1.get_parents(), {0: 1})
        self.assertEqual(self.n1.get_children(), {2: 1})
        self.assertEqual(self.n2.get_parents(), {1: 1})


class AddNodeTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'a', {}, {})
        self.n1 = node(1, 'b', {}, {})
        self.n2 = node(2, 'c', {}, {})
        self.g = open_digraph([0], [1], [self.n0, self.n1, self.n2])

    def test_add_node(self):
        # Comme add_edge incrémente de 1 la multiplicité,
        # on ajoute un nouveau noeud avec multiplicité finale - 1
        # A voir si satisfaisant ou si besoin de changer
        self.g.add_node("d", {0: 0}, {1: 0})
        self.g.add_node("e")
        self.assertEqual(self.n0.get_children(), {3: 1})
        self.assertEqual(self.g.get_node_by_id(3),
                         node(3, 'd', {0: 1}, {1: 1}))
        self.assertEqual(self.g.get_node_by_id(4),
                         node(4, 'e', {}, {}))


class IsWellFormedTest(unittest.TestCase):

    def test_is_well_formed_with_one_input_and_one_output(self):
        n0 = node(0, 'a', {}, {1: 1})
        n1 = node(1, 'b', {0: 1}, {})
        g = open_digraph([0], [1], [n0, n1])
        try:
            g.assert_is_well_formed()
        except Exception as e:
            self.fail(f"Erreur : {e}")

    def test_is_not_well_formed_with_one_input_and_one_output(self):
        n0 = node(0, 'a', {}, {})  # Ce noeud n'a pas d'enfant
        n1 = node(1, 'b', {0: 1}, {})
        g = open_digraph([0], [1], [n0, n1])
        with self.assertRaises(Exception):
            g.assert_is_well_formed()


class AddRemoveNodeTest(unittest.TestCase):

    def test_add_remove_node(self):
        n0 = node(0, 'a', {}, {2: 1})
        n1 = node(1, 'b', {2: 1}, {})
        a = node(2, 'c', {0: 1}, {1: 1, 3: 1})
        b = node(3, 'd', {2: 1}, {})
        g = open_digraph([0], [1], [n0, n1, a, b])

        # Ajout d'un noeud et vérification de la bonne formation du graphe
        # print(g)
        self.assertTrue(g.is_well_formed())

        new_node_id = g.add_node("C", {2: 1}, {3: 1})
        # print("Test Add/Remove node :")
        # print(g)
        self.assertTrue(g.is_well_formed())

        # Retrait du noeud et vérification de la bonne formation du graphe
        g.remove_node_by_id(new_node_id)
        self.assertTrue(g.is_well_formed())

    def test_add_input_output(self):
        n0 = node(0, 'a', {}, {2: 1})
        n1 = node(1, 'b', {2: 1}, {})
        a = node(2, 'c', {0: 1}, {1: 1})
        g = open_digraph([0], [1], [n0, n1, a])

        # Ajouter un noeud d'entrée
        input_node_id = g.add_input_node("Input", 2)
        # self.assertTrue(g.is_well_formed())

        # Ajouter un noeud de sortie
        output_node_id = g.add_output_node("Output", 2)
        self.assertTrue(g.is_well_formed())

        # Retirer les noeuds ajoutés
        g.remove_node_by_id(input_node_id)
        g.remove_node_by_id(output_node_id)
        self.assertTrue(g.is_well_formed())


class AddRemoveEdgeTest(unittest.TestCase):

    def test_add_remove_edge(self):
        n0 = node(0, 'a', {}, {})
        n1 = node(1, 'b', {}, {})
        g = open_digraph([0], [1], [n0, n1])

        # Ajouter une arête
        g.add_edge(0, 1)  # Ajouter une arête entre n0 et n1
        self.assertTrue(g.is_well_formed())

        # Retirer l'arête
        g.remove_edge(0, 1)
        self.assertFalse(g.is_well_formed())

    def test_add_remove_edges(self):
        n0 = node(0, 'a', {}, {})
        n1 = node(1, 'b', {}, {})
        n2 = node(2, 'c', {}, {})
        n3 = node(3, 'd', {}, {})
        n4 = node(4, 'e', {}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])

        self.assertFalse(g.is_well_formed())
        g.add_edges([(0, 1), (1, 2), (1, 3), (3, 4)])
        self.assertTrue(g.is_well_formed())
        g.add_edge(0, 1)
        self.assertFalse(g.is_well_formed())
        g.remove_parallel_edges(0, 1)
        self.assertFalse(g.is_well_formed())
        g.add_edges([(0, 1), (1, 3)])
        self.assertTrue(g.is_well_formed())

        g.remove_several_parallel_edges([(1, 3), (1, 2)])
        self.assertTrue(g.is_well_formed())


class RandomGraphTest(unittest.TestCase):
    def test_random_free(self):
        for _ in range(10):
            g = open_digraph.random(5, 100)
            self.assertTrue(g.is_well_formed())

    def test_random_oriented(self):
        for _ in range(10):
            g = open_digraph.random(5, 100, form="oriented")
            self.assertTrue(g.is_well_formed())
            self.assertTrue(g.is_oriented())

    def test_random_DAG(self):
        for _ in range(10):
            g = open_digraph.random(5, 100, form="DAG")
            self.assertTrue(g.is_well_formed())
            self.assertTrue(g.is_oriented())
            # En plus d'être dirigé, un DAG doit être acyclique
            self.assertFalse(g.is_cyclic())

    def test_random_loop_free(self):
        for _ in range(10):
            g = open_digraph.random(5, 100, form="loop-free")
            self.assertTrue(g.is_well_formed())

    def test_random_undirected(self):
        for _ in range(10):
            g = open_digraph.random(5, 100, form="undirected")
            self.assertTrue(g.is_well_formed())
            self.assertTrue(g.is_symetric())

    def test_random_loop_free_undirected(self):
        for _ in range(10):
            g = open_digraph.random(5, 100, form="loop-free undirected")
            self.assertTrue(g.is_well_formed())
            self.assertTrue(g.is_symetric())


"""
class AdjencyMatrix(unittest.TestCase):
    def test_adjency_matrix(self):
        g = open_digraph.random(5, 100, 1, 1)
        print("Test Adjency Matrix : Graphe :")
        print(g)
        Matrix = g.adjency_matrix()
        print("Matrice associée :")
        dm.printMatrix(Matrix)
 """


class CreateDotFileFromGraph(unittest.TestCase):
    def test_example_graph(self):

        # Création des nœuds
        n0 = node(0, 'a', {}, {2: 1})
        n1 = node(1, 'b', {2: 1}, {})
        n2 = node(2, 'c', {0: 1}, {1: 1, 3: 1})
        n3 = node(3, 'd', {2: 1}, {})

        # Création du graphe
        g = open_digraph([0], [1], [n0, n1, n2, n3])

        # Sauvegarde du graphe
        dot_path = "graphes/test.dot"
        g.save_as_dot_file(dot_path)
        # print(f"Fichier {dot_path} sauvegardé")

    def test_star_graph(self):
        # print("\nTest d'un graphe en étoile")

        # Création des nœuds
        n0 = node(0, 'center', {}, {1: 1, 2: 1, 3: 1, 4: 1})
        n1 = node(1, 'leaf1', {0: 1}, {})
        n2 = node(2, 'leaf2', {0: 1}, {})
        n3 = node(3, 'leaf3', {0: 1}, {})
        n4 = node(4, 'leaf4', {0: 1}, {})

        # Création du graphe
        g = open_digraph([0], [1, 2, 3, 4], [n0, n1, n2, n3, n4])

        # Sauvegarde du graphe
        dot_path = "graphes/star.dot"
        g.save_as_dot_file(dot_path)
        # print(f"Fichier {dot_path} sauvegardé")

    def test_cyclic_graph(self):
        # print("\nTest d'un graphe cyclique")

        # Création des nœuds
        n0 = node(0, 'A', {3: 1}, {1: 1})
        n1 = node(1, 'B', {0: 1}, {2: 1})
        n2 = node(2, 'C', {1: 1}, {3: 1})
        n3 = node(3, 'D', {2: 1}, {0: 1})

        # Création du graphe
        g = open_digraph([], [], [n0, n1, n2, n3])

        # Sauvegarde du graphe
        dot_path = "graphes/cycle.dot"
        g.save_as_dot_file(dot_path)
        # print(f"Fichier {dot_path} sauvegardé")

    def test_binary_tree(self):
        # print("\nTest d'un arbre binaire")

        # Création des nœuds
        n0 = node(0, 'Root', {}, {1: 1, 2: 1})
        n1 = node(1, 'Left', {0: 1}, {3: 1, 4: 1})
        n2 = node(2, 'Right', {0: 1}, {5: 1, 6: 1})
        n3 = node(3, 'L-Left', {1: 1}, {})
        n4 = node(4, 'L-Right', {1: 1}, {})
        n5 = node(5, 'R-Left', {2: 1}, {})
        n6 = node(6, 'R-Right', {2: 1}, {})

        # Création du graphe
        g = open_digraph([0], [3, 4, 5, 6], [n0, n1, n2, n3, n4, n5, n6])

        # Sauvegarde du graphe
        dot_path = "graphes/tree.dot"
        g.save_as_dot_file(dot_path)
        # print(f"Fichier {dot_path} sauvegardé")

    def test_random_graph(self):
        # print("\nTest d'un graphe aléatoire")

        n = 6
        p = 0.3

        # Création des nœuds
        nodes = [node(i, f"N{i}", {}, {}) for i in range(n)]

        # Création du graphe
        g = open_digraph([], [], nodes)
        for i in range(n):
            for j in range(n):
                if i != j and random.random() < p:
                    # Probabilité p d'avoir une arête
                    nodes[i].children[j] = 1
                    nodes[j].parents[i] = 1

        # Sauvegarde du graphe
        dot_path = "graphes/random.dot"
        g.save_as_dot_file(dot_path)
        # print(f"Fichier {dot_path} sauvegardé")


class CreateGraphFromDotFile(unittest.TestCase):
    def test_load_existing_dot_file(self):
        # Liste des fichiers .dot à tester
        test_files = [
            # "test_graph.dot",  # Un graphe linéaire simple (n'existe plus ?)
            "graphes/star.dot",  # Graphe en étoile
            "graphes/cycle.dot",  # Graphe cyclique
            "graphes/tree.dot",  # Arbre binaire
        ]

        for dot_file in test_files:
            with self.subTest(dot_file=dot_file):
                if not os.path.exists(dot_file):
                    self.skipTest(f"Le fichier {dot_file} n'existe pas.")

                # print(f"\nTest du fichier : {dot_file}")

                # Charger le graphe avec la méthode `from_dot_file`
                g = open_digraph.from_dot_file(dot_file)

                # Vérifier que le graphe a bien été chargé
                self.assertGreater(len(g.get_id_node_map()),
                                   0, "Le graphe ne contient aucun nœud.")

                # Vérifier que chaque nœud a un label
                for node_id, nod in g.get_id_node_map().items():
                    self.assertIsNotNone
                    (nod.get_label(), f"Le nœud {node_id} n'a pas de label.")

                # Vérifier qu'au moins une connexion existe
                # si ce n'est pas un graphe isolé
                if len(g.get_id_node_map()) > 1:
                    has_edges = any(node.children
                                    for node in g.get_id_node_map().values())
                    self.assertTrue(has_edges,
                                    "Le graphe devrait contenir des arêtes.")


class Display(unittest.TestCase):
    def test_display(self):
        # Création des nœuds
        n0 = node(0, 'center', {}, {1: 1, 2: 1, 3: 1, 4: 1})
        n1 = node(1, 'leaf1', {0: 1}, {})
        n2 = node(2, 'leaf2', {0: 1}, {})
        n3 = node(3, 'leaf3', {0: 1}, {})
        n4 = node(4, 'leaf4', {0: 1}, {})

        # Création du graphe
        # g = open_digraph([0], [1, 2, 3, 4], [n0, n1, n2, n3, n4])
        g = open_digraph.random(6, 2, form="DAG")
        g.add_input_node(label='n', child_id=2)

        # Spécifier le chemin du fichier .dot
        dot_file_path = "graphes/mon_graphe.dot"

        g.display(dot_path=dot_file_path, verbose=True, method="web")
        # méthode web à fixer bug


class BoolCircTest(unittest.TestCase):
    def test_is_not_well_formed_invalid_label(self):
        n0 = node(0, '&', {}, {2: 1})
        n1 = node(1, '|', {}, {2: 1})
        n2 = node(2, 'a', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {4: 1})
        n4 = node(4, '', {3: 1}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])
        with self.assertRaises(AssertionError):
            G = bool_circ(g)

    def test_is_not_well_formed_copy_label(self):
        n0 = node(0, '&', {}, {2: 1})
        n1 = node(1, '|', {}, {2: 1})
        n2 = node(2, '|', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {4: 1})
        n4 = node(4, '', {3: 1, 4: 1}, {4: 1})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])
        with self.assertRaises(AssertionError):
            G = bool_circ(g)

    def test_is_not_well_formed_and_label(self):
        n0 = node(0, '&', {}, {1: 1, 2: 1})
        n1 = node(1, '|', {0: 1}, {2: 1})
        n2 = node(2, '|', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {4: 1})
        n4 = node(4, '', {3: 1}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])
        with self.assertRaises(AssertionError):
            G = bool_circ(g)

    def test_is_not_well_formed_or_label(self):
        n0 = node(0, '&', {1: 1}, {2: 1})
        n1 = node(1, '|', {}, {0: 1, 2: 1})
        n2 = node(2, '|', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {4: 1})
        n4 = node(4, '', {3: 1}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])
        with self.assertRaises(AssertionError):
            G = bool_circ(g)

    def test_is_not_well_formed_not_label(self):
        n0 = node(0, '&', {}, {2: 1})
        n1 = node(1, '|', {}, {2: 1})
        n2 = node(2, '|', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1, 3: 1}, {4: 1, 3: 1})
        n4 = node(4, '', {3: 1}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])
        with self.assertRaises(AssertionError):
            G = bool_circ(g)

    def test_is_not_well_formed_cyclic(self):
        n0 = node(0, '&', {4: 1}, {1: 1})
        n1 = node(1, '|', {0: 1}, {2: 1})
        n2 = node(2, '|', {1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {4: 1})
        n4 = node(4, '', {3: 1}, {0: 1})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])
        with self.assertRaises(AssertionError):
            G = bool_circ(g)

    def test_is_well_formed(self):
        n0 = node(0, 'input', {}, {2: 1})
        n1 = node(1, '|', {5: 1, 6: 1}, {2: 1})
        n2 = node(2, '&', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {4: 1})
        n4 = node(4, 'output', {3: 1}, {})
        n5 = node(5, 'input', {}, {1: 1})
        n6 = node(6, 'input', {}, {1: 1})
        g = open_digraph([0, 5, 6], [4], [n0, n1, n2, n3, n4, n5, n6])
        self.assertTrue(g.is_well_formed())
        G = bool_circ(g)
        self.assertTrue(G.is_well_formed())


class ShiftIndicesTest(unittest.TestCase):
    def test_shift_indices(self):
        n0 = node(0, '&', {}, {2: 1})
        n1 = node(1, '|', {}, {2: 1})
        n2 = node(2, '&', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {4: 1})
        n4 = node(4, '', {3: 1}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])
        n = 10

        old_ids = g.get_node_ids()

        # On doit faire une copie sinon passage par référence
        old_input_ids = g.get_input_ids().copy()
        old_output_ids = g.get_output_ids().copy()

        # Avant de décaler les indices, on vérifie les indices des nœuds
        # Vérification des IDs des nœuds, des inputs et des outputs
        assert n0.get_id() == 0, f"Erreur: n0 a ID {n0.get_id()} au lieu de 0"
        assert n1.get_id() == 1, f"Erreur: n1 a ID {n1.get_id()} au lieu de 1"
        assert n2.get_id() == 2, f"Erreur: n2 a ID {n2.get_id()} au lieu de 2"
        assert n3.get_id() == 3, f"Erreur: n3 a ID {n3.get_id()} au lieu de 3"
        assert n4.get_id() == 4, f"Erreur: n4 a ID {n4.get_id()} au lieu de 4"

        assert 0 in g.get_input_ids(), "Erreur: l'input 0 manque"
        assert 4 in g.get_output_ids(), "Erreur: l'output 4 manque"

        # Appliquer le décalage
        g.shift_indices(n)

        # print(g)

        new_ids = g.get_node_ids()
        new_input_ids = g.get_input_ids()
        new_output_ids = g.get_output_ids()

        # Nouveaux indices = anciens indices + n
        for old_id, new_id in zip(old_ids, new_ids):
            self.assertEqual(new_id, old_id + n)

        # Pareil pour les ids d'input et d'output
        for old_input_id, new_input_id in zip(old_input_ids, new_input_ids):
            self.assertEqual(new_input_id, old_input_id + n)

        for old_output_id, new_out_id in zip(old_output_ids, new_output_ids):
            self.assertEqual(new_out_id, old_output_id + n)

        # Après le décalage, on vérifie les nouveaux indices
        assert n0.get_id() == 0 + n, f"Erreur: nœud n0 a l'ID {n0.get_id()}"
        assert n1.get_id() == 1 + n, f"Erreur: nœud n1 a l'ID {n1.get_id()}"
        assert n2.get_id() == 2 + n, f"Erreur: nœud n2 a l'ID {n2.get_id()}"
        assert n3.get_id() == 3 + n, f"Erreur: nœud n3 a l'ID {n3.get_id()}"
        assert n4.get_id() == 4 + n, f"Erreur: nœud n4 a l'ID {n4.get_id()}"

        assert 10 in g.get_input_ids(), "Erreur: l'input 10 manque"
        assert 14 in g.get_output_ids(), "Erreur: l'output 14 manque"

        # Vérification des relations de parenté et de filiation après décalage

        assert 10 in n2.get_parents().keys(), f"Erreur: nœud n2 doit avoir 10 comme parent"
        assert 11 in n2.get_parents().keys(), f"Erreur: nœud n2 doit avoir 11 comme parent"
        assert 12 in n3.get_parents(), f"Erreur: nœud n3 doit avoir 12 comme enfant"
        assert 14 in n3.get_children(), f"Erreur: nœud n3 doit avoir 14 comme enfant"
        
        # Vérification des parents et enfants après décalage
        assert 12 in n0.get_children(), f"Erreur: nœud n0 doit avoir 12 comme enfant"
        assert 12 in n1.get_children(), f"Erreur: nœud n1 doit avoir 12 comme enfant"

        #print("Tous les tests ont réussi.")

class TP6_Test(unittest.TestCase):
    def test_iparallel_connected_components(self):
        n0 = node(0, 'a', {}, {2:1})
        n1 = node(1, 'b', {}, {2:1})
        n2 = node(2, 'c', {0:1, 1:1}, {3:1})
        n3 = node(3, 'd', {2:1}, {4:1})
        n4 = node(4, 'e', {3:1}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])

        n0_ = node(0, 'f', {7:1}, {24:1})
        n1_ = node(4, 'g', {}, {18:1})
        n2_ = node(7, 'h', {18:1}, {0:1})
        n3_ = node(18, 'i', {4:1}, {7:1})
        n4_ = node(24, 'j', {0:1}, {})
        f = open_digraph([4], [24], [n0_, n1_, n2_, n3_, n4_])

        #print("Graphe g :", g)
        #print("Graphe f :", f)
        f_copy = f.copy()
        g.iparallel(f)
        #print("g après appel à g.iparallel(f) :")
        #print(g)
        #print("f après appel à g.iparallel(f) :")
        #print(f)
        self.assertTrue(g.is_well_formed())
        # Deuxième graphe ne doit pas être modifié
        self.assertEqual(f, f_copy)

        #TEST DE L EXO 3
        # print(open_digraph.identity(4))

        #MAINTENANT TESTS DES EXOS 4 ET 5 :)
        (nb1, dico1) = g.connected_components()
        (nb2, dico2) = f.connected_components()
        self.assertTrue(nb1 == 2)
        self.assertTrue(nb2 == 1)
        #print(dico1)
        #print(dico2)
        g.iparallel(f)
        (nb3, dico3) = g.connected_components()
        self.assertTrue(nb3 == 3)
        #print(dico3)
        list_f = f.connected_components_graphs()
        list_g = g.connected_components_graphs()
        self.assertEqual(len(list_f), 1)
        self.assertEqual(len(list_g), 3)
        self.assertEqual(list_f[0], f)
        self.assertTrue(list_f[0] == f or list_f[1] == f or list_f[2] == f)



    def test_icompose(self):
        n0 = node(0, '0', {}, {2:1})
        n1 = node(1, '1', {}, {2:1})
        n2 = node(2, '2', {0:1, 1:1}, {3:1})
        n3 = node(3, '3', {2:1}, {4:1})
        n4 = node(4, '4', {3:1}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4])

        n0_ = node(0, '0', {7:1}, {24:1})
        n1_ = node(4, '4', {}, {18:1})
        n2_ = node(7, '7', {18:1}, {0:1})
        n3_ = node(18, '18', {4:1}, {7:1})
        n4_ = node(24, '24', {0:1}, {})
        f = open_digraph([4], [24], [n0_, n1_, n2_, n3_, n4_])

        #print("Graphe g :", g)
        #print("Graphe f :", f)
        f_copy = f.copy()

        g.icompose(f)
        #print("g après appel à g.icompose(f) :")
        #print(g)
        #print("f après appel à g.compose(f) :")
        #print(f)
        self.assertTrue(g.is_well_formed())
        g.display("graphes/TP6_icompose.dot")
        # Deuxième graphe ne doit pas être modifié
        self.assertEqual(f, f_copy)


class TP7_Test(unittest.TestCase):
    def test_dij(self):
        n0 = node(0, '&', {}, {2:1})
        n1 = node(1, '|', {}, {2:1})
        n2 = node(2, '&', {0:1, 1:1}, {3:1})
        n3 = node(3, '~', {2:1}, {4:1})
        n4 = node(4, '', {3:1}, {})
        n5 = node(5, 'relieARien', {}, {})
        g = open_digraph([0], [4], [n0, n1, n2, n3, n4, n5])

        #print(tuple(g.dijkstra(n0.get_id())))
        #print(tuple(g.dijkstra(n2.get_id(), direction = -1)))
        #print(tuple(g.dijkstra(n2.get_id(), direction = 1)))

    def test_short2(self):
        # Création d'un graphe de test
        g = open_digraph([], [], {})

        # Ajout de nœuds
        n1_id = g.add_node(label="A")
        n2_id = g.add_node(label="B")
        n3_id = g.add_node(label="C")
        n4_id = g.add_node(label="D")
        n5_id = g.add_node(label="E")

        # Ajout d'arêtes
        g.add_edge(n1_id, n2_id)
        g.add_edge(n1_id, n3_id)
        g.add_edge(n2_id, n4_id)
        g.add_edge(n3_id, n4_id)
        g.add_edge(n4_id, n5_id)

        # Test 1: Chemin le plus court de n1 à n5
        path = g.shortest_path(n1_id, n5_id)
        #print(path)
        assert path == [n1_id, n2_id, n4_id, n5_id] or path == [n1_id, n3_id, n4_id, n5_id], f"Test 1 failed: {path}"
        g.display("graphes/graph_test_1.dot", verbose=True)

        # Test 2: Chemin le plus court de n1 à n4
        path = g.shortest_path(n1_id, n4_id)
        assert path == [n1_id, n2_id, n4_id] or path == [n1_id, n3_id, n4_id], f"Test 2 failed: {path}"
        g.display("graphes/graph_test_2.dot", verbose=True)

        # Test 3: Chemin le plus court de n2 à n5
        path = g.shortest_path(n2_id, n5_id)
        assert path == [n2_id, n4_id, n5_id], f"Test 3 failed: {path}"
        g.display("graphes/graph_test_3.dot", verbose=True)

        # Test 4: Chemin le plus court de n3 à n5
        path = g.shortest_path(n3_id, n5_id)
        assert path == [n3_id, n4_id, n5_id], f"Test 4 failed: {path}"
        g.display("graphes/graph_test_4.dot", verbose=True)

        # Test 5: Chemin le plus court de n1 à n1 (devrait être juste n1)
        path = g.shortest_path(n1_id, n1_id)
        assert path == [n1_id], f"Test 5 failed: {path}"
        g.display("graphes/graph_test_5.dot", verbose=True)

        # Test 6: Chemin le plus court de n5 à n1 (devrait être vide car pas de chemin inverse)
        # JE CROIS QUE CE TEST EST PAS BON PUISQU'UN CHEMIN DE U VERS V NE VEUT PAS DIRE QUE U EST FORCEMENT UN PARENT ET V FORCEMENT UN ENFANT (signé Raphaël)

        #path = g.shortest_path(n5, n1)
        #assert path == [], f"Test 6 failed: {path}"
        #g.display("graph_test_6.dot", verbose=True)

        #print("TOUS LES TESTS SONT PASSÉS !!!!")
    
    def test_short(self):
        # Graphe de test :
        # 
        #    A
        #   / \
        #  B   C
        #  |   |
        #  E   D
        #       \
        #        E
        #
        # Et un nœud F isolé.

        g = open_digraph([], [], {})

        # Création des nœuds
        A = g.add_node(label="A")
        B = g.add_node(label="B")
        C = g.add_node(label="C")
        D = g.add_node(label="D")
        E = g.add_node(label="E")
        #F = g.add_node(label="F")  # isolé

        # Ajout des arêtes
        g.add_edge(A, B)
        g.add_edge(B, E)     # chemin A->B->E (longueur 2)
        g.add_edge(A, C)
        g.add_edge(C, D)
        g.add_edge(D, E)     # chemin A->C->D->E (longueur 3)

        # # Test 1 : plus court chemin A → E doit être [A, B, E]
        # path = g.shortest_path(A, E)
        # self.assertEqual(path, [A, B, E],
        #     f"Chemin attendu [A, B, E], obtenu {path}")

        # # Test 2 : chemin trivial A → A doit être [A]
        # path = g.shortest_path(A, A)
        # self.assertEqual(path, [A],
        #     f"Pour un même nœud, on doit obtenir [{A}], obtenu {path}")

        # # Test 3 : F est isolé, donc aucun chemin F → E
        # path = g.shortest_path(F, E)
        # self.assertEqual(path, [],
        #     f"Aucun chemin attendu de F vers E, obtenu {path}")

        # (Optionnel) génère .dot pour inspection visuelle
        g.display("graphes/graph_test_AE.dot", verbose=True)
    
    def test_ancetre_commun(self):
        n0 = node(0, '0', {}, {3:1})
        n1 = node(1, '1', {}, {5:1, 4:1, 8:1})
        n2 = node(2, '2', {}, {4:1})
        n3 = node(3, '3', {0:1}, {5:1, 6:1})
        n4 = node(4, '4', {1:1, 2:1}, {6:1})
        n5 = node(5, '5', {3:1, 1:1}, {7:1})
        n6 = node(6, '6', {3:1, 4:1}, {8:1, 9:1})
        n7 = node(7, '7', {5:1}, {})
        n8 = node(8, '8', {1:1, 6:1}, {})
        n9 = node(9, '9', {6:1}, {})

        g = open_digraph([0, 2], [7], [n0, n1, n2, n3, n4, n5, n6, n7, n8, n9])

        self.assertTrue(g.is_well_formed())
        anc_com = g.ancetre_commun(5, 8)
        self.assertTrue(anc_com == {0 : (2, 3), 3 : (1, 2), 1 : (1, 1)})

class TP8_Test(unittest.TestCase):
    def setUp_signe_Raphael(self):    
        self.n0 = node(0, '0', {}, {3:1})
        self.n1 = node(1, '1', {}, {5:1, 4:1, 8:1})
        self.n2 = node(2, '2', {}, {4:1})
        self.n3 = node(3, '3', {0:1}, {5:1, 6:1})
        self.n4 = node(4, '4', {1:1, 2:1}, {6:1})
        self.n5 = node(5, '5', {3:1, 1:1}, {7:1})
        self.n6 = node(6, '6', {3:1, 4:1}, {8:1, 9:1})
        self.n7 = node(7, '7', {5:1}, {})
        self.n8 = node(8, '8', {1:1, 6:1}, {})
        self.n9 = node(9, '9', {6:1}, {})
        self.g = open_digraph([0, 2], [7], [self.n0, self.n1, self.n2, self.n3, self.n4,
                                            self.n5, self.n6, self.n7, self.n8, self.n9])

    def setUp(self):
        # Initialisation des nœuds
        self.n0 = node(0, '0', {}, {3: 1})
        self.n1 = node(1, '1', {}, {5: 1, 4: 1, 8: 1})
        self.n2 = node(2, '2', {}, {4: 1})
        self.n3 = node(3, '3', {0: 1}, {5: 1, 6: 1})
        self.n4 = node(4, '4', {1: 1, 2: 1}, {6: 1})
        self.n5 = node(5, '5', {3: 1, 1: 1}, {7: 1})
        self.n6 = node(6, '6', {3: 1, 4: 1}, {8: 1, 9: 1})
        self.n7 = node(7, '7', {5: 1}, {})
        self.n8 = node(8, '8', {1: 1, 6: 1}, {})
        self.n9 = node(9, '9', {6: 1}, {})

        # Initialisation du graphe avec les nœuds d'entrée et de sortie
        self.g = open_digraph([0, 2], [7], [self.n0, self.n1, self.n2, self.n3, self.n4,
                                            self.n5, self.n6, self.n7, self.n8, self.n9])


    def test_tri_topologique(self):
        tri = self.g.tri_topologique()
        self.assertTrue(tri == [{0, 1, 2}, {3, 4}, {5, 6}, {7, 8, 9}])
        
    #Fonction/Test a revoir
    def test_profondeurs(self):
        self.assertTrue(self.g.profondeur_graphe() == 3)
        self.assertTrue(self.g.profondeur_noeud(self.n9) == 3)
        self.assertTrue(self.g.profondeur_noeud(self.n5) == 2)
        self.assertTrue(self.g.profondeur_noeud(self.n6) == 2)
        self.assertTrue(self.g.profondeur_noeud(self.n4) == 1)
        self.assertTrue(self.g.profondeur_noeud(self.n1) == 0)

    def test_longest_path(self):
        #print(tuple(self.g.longest_path(self.n1.get_id(), self.n5.get_id())))
        self.assertTrue(self.g.longest_path(self.n1.get_id(), self.n5.get_id()) == ([self.n1.get_id(), self.n5.get_id()], 1))

        self.assertTrue(self.g.longest_path(self.n1.get_id(), self.n8.get_id()) == ([self.n1.get_id(), self.n4.get_id(),
                                                                                    self.n6.get_id(), self.n8.get_id()], 3))

        self.assertTrue(self.g.longest_path(self.n0.get_id(), self.n7.get_id()) == ([self.n0.get_id(), self.n3.get_id(),
                                                                                    self.n5.get_id(), self.n7.get_id()], 3))

        self.assertTrue(self.g.longest_path(self.n4.get_id(), self.n9.get_id()) == ([self.n4.get_id(), self.n6.get_id(),
                                                                                    self.n9.get_id()], 2))

        self.assertTrue(self.g.longest_path(self.n3.get_id(), self.n7.get_id()) == ([self.n3.get_id(), self.n5.get_id(),
                                                                                    self.n7.get_id()], 2))

class TP9_Test(unittest.TestCase):
    def test_parse_parentheses(self):
        formula = "((x0)&((x1)&(x2)))|((x1)&(~(x2)))"
        circuit, inputs = bool_circ.PARSE_PARENTHESES(formula, "((x0)&(~(x1)))|(x2)", "((x0)^(x1))")
        #print(circuit.g)
        #print(inputs)
        
        # Spécifier le chemin du fichier .dot
        dot_file_path = "graphes/mon_graphe.dot"

        circuit.g.display(dot_path=dot_file_path, verbose=False, method="local")

class TP10_Test(unittest.TestCase):
    def test_random_bool_circ(self):
        # Créer un circuit booléen aléatoire avec 5 nœuds, une valeur maximale de poids de 2, 2 entrées et 2 sorties
        random_graph = bool_circ.random_bool_circ(5, 2, inputs=2, outputs=2)
        #print("Random Boolean Circuit:")
        #print(random_graph.g)
        self.assertTrue(random_graph.is_well_formed())
        random_graph.g.display(dot_path="graphes/random_bool_circ.dot", verbose=False, method="local")

    def test_adder_0(self): 
        adder_0 = bool_circ.adder_0()
        self.assertTrue(adder_0.is_well_formed)
        adder_0.g.display("graphes/adder_0.dot")
    
    def test_half_adder(self):
        # Créer un Half-Adder pour des registres de taille 2^2 (4 bits)
        half_adder_circuit = bool_circ.half_adder(2)
        #print("Half-Adder Circuit:")
        #print(half_adder_circuit.g)
        self.assertFalse(half_adder_circuit.g.is_cyclic())
        self.assertTrue(half_adder_circuit.is_well_formed())
        half_adder_circuit.g.display(dot_path="graphes/half_adder_4.dot", verbose=False, method="local")

    def test_adder_nous(self):
        # Créer un Adder pour des registres de taille 2^2 (4 bits)
        adder_circuit = bool_circ.adder(2)
        #print("Adder Circuit:")
        #print(adder_circuit.g)
        self.assertTrue(adder_circuit.is_well_formed())
        adder_circuit.g.display(dot_path="graphes/adder.dot", verbose=False, method="local")

    def test_adder(self):
        adder = bool_circ.adder(1)
        self.assertTrue(adder.g.is_well_formed())

    def test_carry_lookahead_adder_4(self):
        reg1 = bool_circ.from_int(4,4)
        reg2 = bool_circ.from_int(7,4)
        cla = bool_circ.carry_lookahead_4(reg1, reg2, "retenue0")
        print("CLA Circuit (4 bits):")
        print(cla.g)
        self.assertTrue(cla.is_well_formed())
        cla.g.display(dot_path="graphes/cla_4.dot", verbose=False, method="local")

    def test_carry_lookahead_adder_4n(self):
        # Créer un CLA pour des registres de taille 16 (4 * 4)
        reg1 = bool_circ.from_int(4,16)
        reg2 = bool_circ.from_int(7,16)
        cla_circuit = bool_circ.carry_lookahead_adder_4n(reg1, reg2, "retenue0")
        print("CLA Circuit (16 bits):")
        print(cla_circuit.g)
        self.assertTrue(cla_circuit.is_well_formed())
        cla_circuit.g.display(dot_path="graphes/cla_16.dot", verbose=False, method="local")

class TP11_Test(unittest.TestCase):
    def test_is_well_formed(self):
        g = open_digraph([], [], [])
        zero = g.add_node('0')
        one = g.add_node('1')
        xor = g.add_node('^')
        g.add_edge(zero, xor)
        g.add_edge(one, xor)
        out = g.add_output_node('out')
        g.add_edge(xor, out)
        circ = bool_circ(g)
        self.assertTrue(circ.is_well_formed())

    def test_from_int(self):
        circ = bool_circ.from_int(13, 4)
        circ2 = bool_circ.from_int(11)
        self.assertTrue(circ.is_well_formed())
        self.assertTrue(circ2.is_well_formed())
        circ2.g.display("graphes/TP11_from_int.dot")
        #print(circ2.g)

    def test_simplifie_bool_circ(self):
        g = open_digraph([], [], [])
        and_node = g.add_node('&')
        const_0 = g.add_node('0', {}, {and_node:1})
        other = g.add_node('1', {}, {and_node:1})
        g.add_node('1', {}, {and_node:1})
        
        g.add_output_node('output', and_node)
        g_1 = g.copy()
        circ = bool_circ(g)
        circ_1 = bool_circ(g_1)
        circ.simplifie_bool_circ(const_0)
        circ_1.simplifie_bool_circ(other)

        labels = [node.get_label() for node in circ.g.get_nodes()]
        self.assertIn('0', labels)
        self.assertNotIn('&', labels)

        labels_1 = [node.get_label() for node in circ_1.g.get_nodes()]
        #print(circ_1.g)
        self.assertIn('0', labels_1)
        self.assertIn('&', labels_1)

    def test_EXO5(self):
        adder = bool_circ.half_adder(2)
        registre1 = bool_circ.from_int(103, 8) # ça fera les 2 nombres 11 et 5 selon comment on a écrit les adder !
        
        #registre1.g.display("graphes/TP11_EXO5.dot") # ici tout a l'air bon
        adder.g.display("graphes/TP11_EXO5_adder_initial.dot")
        adder.g.icompose_simplifie(registre1.g)

        adder.g.display("graphes/TP11_EXO5_avant.dot")
        adder.evaluate()
        self.assertTrue(adder.is_well_formed)
        adder.g.display("graphes/TP11_EXO5_apres.dot") # ça fait bien 16 !
        self.assertEqual(valeurs_sorties(adder), ["1", "0", "0", "0", "0"])

    def test_addition_exhaustive(self):
        # Toutes les additions de deux entiers de 4 bits : le circuit évalué doit donner a + b.
        # Les entrées de l'additionneur sont entrelacées : a3, b3, a2, b2, a1, b1, a0, b0.
        for a in range(16):
            for b in range(16):
                bits_a, bits_b = format(a, "04b"), format(b, "04b")
                entrelaces = "".join(x + y for x, y in zip(bits_a, bits_b))
                adder = bool_circ.half_adder(2)
                registre = bool_circ.from_int(int(entrelaces, 2), 8)
                adder.g.icompose_simplifie(registre.g)
                adder.evaluate()
                # Sorties : la retenue, puis les 4 bits de la somme (poids fort en premier)
                resultat = int("".join(valeurs_sorties(adder)), 2)
                self.assertEqual(resultat, a + b)

class TP12_Test(unittest.TestCase): 
    def test_encodeur(self):
        encodeur = bool_circ.encodeur_4_bits("0", "1", "1", "1")
        encodeur.g.display("graphes/TP12_encodeur.dot")
        encodeur.evaluate()
        encodeur.g.display("graphes/TP12_encodeur_evaluate.dot")

    def test_decodeur(self):
        # Mot 0111 suivi de ses 3 bits de parité (0, 0, 1)
        decodeur = bool_circ.decodeur_4_bits("0", "1", "1", "1", "0", "0", "1")
        self.assertTrue(decodeur.is_well_formed())
        decodeur.g.display("graphes/TP12_decodeur.dot")
        decodeur.evaluate()
        self.assertEqual(valeurs_sorties(decodeur), ["0", "1", "1", "1"])

    def test_identite(self):
        # Encoder puis décoder doit redonner le mot de départ, pour les 16 mots de 4 bits
        for mot in itertools.product("01", repeat=4):
            decodeur = bool_circ.composition_encodeur_decodeur(*mot)
            self.assertEqual(valeurs_sorties(decodeur), list(mot))

    def test_correction_une_erreur(self):
        # Le code de Hamming (7,4) corrige une erreur sur n'importe lequel des 7 bits transmis
        for mot in itertools.product("01", repeat=4):
            encodeur = bool_circ.encodeur_4_bits(*mot)
            encodeur.evaluate()
            code = valeurs_sorties(encodeur)      # 3 bits de parité puis 4 bits de données
            transmis = code[3:] + code[:3]        # ordre attendu par le décodeur
            for position in range(7):
                recu = list(transmis)
                recu[position] = "1" if recu[position] == "0" else "0"
                decodeur = bool_circ.decodeur_4_bits(*recu)
                decodeur.evaluate()
                self.assertEqual(valeurs_sorties(decodeur), list(mot))

    def test_encodeur_decodeur(self):
        res = bool_circ.composition_encodeur_decodeur("0", "1", "1", "1")
        res.g.display("graphes/TP12_test_comp_encodeur_decodeur.dot")
        self.assertEqual(valeurs_sorties(res), ["0", "1", "1", "1"])

if __name__ == '__main__':
    unittest.main()
