import sys
import os
import random as random

##############################################################################
#                               MIXINS                                       #
##############################################################################

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from mixins.compositions_mixin import OpenDigraphCompositionsMixin
from mixins.longest_path_mixin import OpenDigraphLongestPathMixin
from mixins.display_mixin import OpenDigraphDisplaysMixin
from mixins.shortest_path_mixin import OpenDigraphShortestPathMixin
from mixins.properties_mixin import OpenDigraphPropertiesMixin
from mixins.matrix_mixin import OpenDigraphMatrixMixin

root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root)
import modules.digraph_matrix as dm
# Ajout du répertoire parent au sys.path

from collections import deque

##############################################################################
#                           CLASS NODE                                       #
##############################################################################

class node (OpenDigraphCompositionsMixin):
    def __init__(self, identity: int, label: str,
                 parents: dict[int, int], children: dict[int, int]):
        """
        identity: int; its unique id in the graph
        label: string;
        parents: int->int dict; maps a parent node's id to its multiplicity
        children: int->int dict; maps a child node's id to its multiplicity
        """
        self.id = identity
        self.label = label
        self.parents = parents
        self.children = children

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return (f"Numero: {self.id}, Nom: {self.label}, "
                f"Parents: {self.parents}, Enfants: {self.children}")

    def __repr__(self):
        return (f"node(id={self.id}, label='{self.label}', "
                f"parents={self.parents}, children={self.children})")

    def copy(self):
        return node(self.id, self.label,
                    self.parents.copy(),
                    self.children.copy())

    # Méthodes d'accès aux attributs
    def get_id(self): return self.id
    def get_label(self): return self.label
    def get_parents(self): return self.parents
    def get_children(self): return self.children

    # Méthode de modification des attributs
    def set_id(self, identity): self.id = identity
    def set_label(self, label): self.label = label
    def set_parents(self, parents): self.parents = parents
    def set_children(self, children): self.children = children

    def add_child_id(self, child_id, multiplicity):
        if child_id in self.children:
            self.children[child_id] += multiplicity
        else:
            self.children[child_id] = multiplicity

    def add_parent_id(self, parent_id, multiplicity):
        if parent_id in self.parents:
            self.parents[parent_id] += multiplicity
        else:
            self.parents[parent_id] = multiplicity

    def check_existence(self, id, parent):
        """
        @param int id: id du parent/enfant dont on veut vérifier l'existence
        @param bool parent: true si c'est un parent, false si c'est un gosse
        @return : none/une erreur
        verifie si un noeud existe parmi les parents/enfants d'un noeud
        """
        if parent:
            if not (id in self.parents):
                raise Exception("suppression d'un parent qui n'existe pas!")
        else:
            if not (id in self.children):
                raise Exception("suppression d'un enfant qui n'existe pas!")

    def remove_parent_once(self, parent_id):
        """
        @param int parent_id : l'identifiant du noeud parent
        @return : None
        Retire une occurence du noeud parent d'id parent_id,
        Retire la clé du dictionnaire si la multiplicité devient nulle
        """
        self.check_existence(parent_id, True)
        self.parents[parent_id] -= 1
        if (self.parents[parent_id] == 0):
            del self.parents[parent_id]

    def remove_child_once(self, child_id):
        """
        @param int child_id : l'identifiant du noeud enfant
        @return : None
        Retire une occurence du noeud enfant d'id child_id,
        Retire la clé du dictionnaire si la multiplicité devient nulle
        """
        self.check_existence(child_id, False)
        self.children[child_id] -= 1
        if (self.children[child_id] == 0):
            del self.children[child_id]

    def remove_parent_id(self, parent_id):
        """
        @param int parent_id : l'identifiant du noeud parent
        @return : None
        Retire toutes les occurences du noeud parent d'id parent_id,
        Retire la clé du dictionnaire
        """
        self.check_existence(parent_id, True)
        del self.parents[parent_id]

    def remove_child_id(self, child_id):
        """"
        @param int child_id : l'identifiant du noeud enfant
        @return : None
        Retire toutes les occurences du noeud enfant d'id child_id,
        Retire la clé du dictionnaire
        """
        self.check_existence(child_id, False)
        del self.children[child_id]

    # méthode de comparaison entre deux noeuds, utile notamment pour les tests
    def __eq__(self, other):
        if not isinstance(other, node):
            return False
        return (
            self.id == other.id
            and self.label == other.label
            and self.parents == other.parents
            and self.children == other.children
        )

    def indegree(self):
        """Retourne le degré d'entrée du noeud."""
        return len(self.parents)

    def outdegree(self):
        """Retourne le degré de sortie du noeud."""
        return len(self.children)

    def degree(self):
        """Retourne le degré du noeud."""
        return self.indegree() + self.outdregree()


##############################################################################
#                        CLASS OPEN_DIGRAPH                                  #
##############################################################################

class open_digraph(
    OpenDigraphCompositionsMixin,
    OpenDigraphLongestPathMixin,
    OpenDigraphDisplaysMixin,
    OpenDigraphShortestPathMixin,
    OpenDigraphPropertiesMixin,
    OpenDigraphMatrixMixin
):
    node = node  # utile pour utiliser node dans les mixins

    def __init__(self, inputs: list[int], outputs: list[int], nodes: list[node]):
        """
        inputs: int list; the ids of the input nodes
        outputs: int list; the ids of the output nodes
        nodes: dict; node iter;
        next_id: int; prochain identifiant libre;
        """
        self.inputs = inputs
        self.outputs = outputs
        # self.nodes: <int, node> dict
        self.nodes = {node.id: node for node in nodes}
        # ajout d'un attribut
        self.next_id = max(self.get_node_ids(), default=-1) + 1

    def __str__(self):
        """Renvoie une représentation textuelle du graphe."""
        nodes_str = "\n".join(
            [
                f"  {node_id}: {node}"
                for node_id, node in self.nodes.items()
            ]
            )
        return (f"Entrees: {self.inputs}\n"
                f"Sorties: {self.outputs}\n"
                f"Noeuds:\n{nodes_str}")

    def __repr__(self):
        """Renvoie une représentation textuelle du graphe."""
        nodes_repr = ", ".join([repr(node) for node in self.get_nodes()])
        return (f"open_digraph(inputs={self.inputs}, outputs={self.outputs}, "
                f"nodes=[{nodes_repr}])")

    def __eq__(self, other):
        """Compare deux graphes pour vérifier s'ils sont identiques."""
        if not isinstance(other, open_digraph):
            return False

        if set(self.inputs) != set(other.inputs)\
                or set(self.outputs) != set(other.outputs):
            return False

        if len(self.nodes) != len(other.nodes):
            return False

        for node_id, self_node in self.nodes.items():
            if self_node != other.nodes[node_id]:
                return False

        return True

    def __delitem__(self, node_id):
        """Supprime un noeud du graphe."""
        self.remove_node_by_id(node_id)

    @classmethod
    def empty(cls):
        """Retourne un graphe vide."""
        return open_digraph([], [], [])

    def is_empty(self):
        """Vérifie si le graphe est vide."""
        return self == open_digraph.empty()

    def copy(self):
        """Crée une copie indépendante du graphe."""
        copied_nodes = [node.copy() for node in self.get_nodes()]
        return open_digraph(self.inputs[:], self.outputs[:], copied_nodes)

    # Méthodes d'accès aux nœuds et IDs
    def get_input_ids(self): return self.inputs
    def get_output_ids(self): return self.outputs
    def get_id_node_map(self): return self.nodes
    def get_nodes(self): return list(self.nodes.values())
    def get_node_ids(self): return list(self.nodes.keys())
    def get_node_by_id(self, node_id: int) -> 'node': return self.nodes.get(node_id, None)
    def get_nodes_by_ids(self, ids):
        """Retourne une liste de noeuds correspondant aux IDs fournis."""
        return [
            self.get_node_by_id(node_id)
            for node_id in ids
            if self.get_node_by_id(node_id) is not None
        ]

    # Modification des entrées/sorties
    def set_inputs(self, inputs): self.inputs = inputs
    def set_outputs(self, outputs): self.outputs = outputs

    def add_input_id(self, input_id):
        """Ajoute un ID d'entrée au graphe."""
        if input_id not in self.inputs:
            self.inputs.append(input_id)

    def add_output_id(self, output_id):
        """Ajoute un ID de sortie au graphe."""
        if output_id not in self.outputs:
            self.outputs.append(output_id)

    def new_id(self):
        """Génère un nouvel ID unique pour un noeud."""
        new_id = max(self.get_node_ids(), default=-1) + 1
        #self.next_id += 1
        #max(self.get_node_ids(), default=-1) + 1
        return new_id

    @classmethod
    def random(cls, n, bound, inputs=0, outputs=0, form="free"):
        """
        Génère un graphe aléatoire selon la forme spécifiée.

        Paramètres :
        - n : Nombre de nœuds
        - bound : Valeur maximale des poids des arêtes
        - inputs : Nombre de nœuds d'entrée (par défaut 0)
        - outputs : Nombre de nœuds de sortie (par défaut 0)
        - form : Type de graphe (options : "free", "DAG", "oriented",
                                            "loop-free", "undirected",
                                            "loop-free undirected")

        Retour :
        - Un graphe généré aléatoirement selon les spécifications
        """
        matrix_generators = {
            "free": dm.random_int_matrix,
            "DAG": dm.random_triangular_int_matrix,
            "oriented": dm.random_oriented_int_matrix,
            "loop-free": lambda n, bound: dm.random_int_matrix(n, bound, True),
            "undirected": dm.random_symetric_int_matrix,
            "loop-free undirected": lambda n,
            bound: dm.random_symetric_int_matrix(n, bound, True),
        }

        if form not in matrix_generators:
            raise ValueError("Forme de graphe non reconnue.\n\
                             Options valides : 'free' 'DAG' 'oriented'\
                                                'loop-free' 'undirected'\
                                                'loop-free undirected'")

        Matrix = matrix_generators[form](n, bound)
        # return dm.graph_from_adjacency_matrix(Matrix)

        # print("Matrice :")
        # dm.printMatrix(Matrix)
        # Création du graphe à partir de la matrice selon l'option voulue
        g = dm.graph_from_adjcency_matrix(Matrix)

        # Liste des noeuds du graphe
        nodes_list = g.get_nodes()
        # for nd in nodes_list:
        #    print(nd)

        # Liste des id des noeuds d'inputs
        # et d'outputs possibles parmi ceux créés
        possible_inputs_ids_list = [i.get_id() for i in nodes_list
                                    if ((len(i.get_parents()) == 0)
                                        and (len(i.get_children()) == 1))]

        possible_outputs_ids_list = [o.get_id() for o in nodes_list
                                     if len(o.get_parents()) == 1
                                     and len(o.get_children()) == 0]

        # Vérification nombre de noeuds demandés en input et en output
        nb_inputs_possible = len(possible_inputs_ids_list)
        # print("nb d'inputs possibles : " + str(nb_inputs_possible))
        nb_outputs_possible = len(possible_outputs_ids_list)
        # print("nb d'inputs possibles : " + str(nb_outputs_possible))
        if (inputs > nb_inputs_possible):
            g.set_inputs({})
        elif (outputs > nb_outputs_possible):
            g.set_outputs({})
        else:
            # Choix aléatoire des inputs et des outputs
            inputs_ids = random.sample(possible_inputs_ids_list, inputs)
            outputs_ids = random.sample(possible_outputs_ids_list, outputs)

            # Ajout de ces noeuds dans le graphe
            for e in inputs_ids:
                g.add_input_id(e)
            for e in outputs_ids:
                g.add_output_id(e)

        return g

    def id_to_range_node(self):
        """
        Génère un dictionnaire qui associe chaque id de nœud du graphe
        à un index unique dans une plage continue.

        Retourne un dictionnaire où les clés sont les id
        des nœuds du graphe, et les valeurs sont des entiers
        uniques allant de 0 à n-1 (où n est le nombre total de nœuds).
        """
        return {node_id: i for i, node_id in enumerate(self.get_node_ids())}

    

    def min_id(self):
        if not (len(self.get_node_ids()) == 0):
            min = (self.get_node_ids())[0]
            for id in self.get_node_ids():
                if id < min:
                    min = id
            return min
        raise Exception("Liste vide")

    def max_id(self):
        if not (len(self.get_node_ids()) == 0):
            max = (self.get_node_ids())[0]
            for id in self.get_node_ids():
                if id > max:
                    max = id
            return max
        raise Exception("Liste vide")
