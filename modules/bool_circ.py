import sys
import os

# Ajout du chemin vers modules/ pour les imports relatifs
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from open_digraph import open_digraph, node  # pour utiliser open_digraph et node

import random

class bool_circ(open_digraph):
    def __init__(self, g : open_digraph, test_cyclique=True):
        self.g = g
        if (test_cyclique):
            # On test is_cyclic avant is_well_formed pour déjà savoir c'est acyclique
            assert self.g.is_well_formed()
            assert not self.g.is_cyclic()
            assert self.is_well_formed()

    def is_cyclic(self):
        return self.g.is_cyclic()
    
    def is_well_formed(self):
        
        if self.g.is_cyclic():
            return False

        for node in self.g.get_nodes():
            label = node.get_label()
            indeg = node.indegree()
            outdeg = node.outdegree()
            node_id = node.get_id()

            if label in {'&', '|', '^'}:
                if indeg < 2 or outdeg != 1:
                    #print("problème & | ^")
                    return False

            elif label == '~':
                if indeg != 1 or outdeg != 1:
                    #print("problème ~")
                    return False

            elif label == '':
                if indeg != 1:
                    #print("problème ''")
                    return False

            elif label == '0' or label == '1' or label == 'Y':
                if indeg != 0 or outdeg < 1:
                    #print("problème 0 1 Y")
                    return False

            elif label == 'input':
                if indeg != 0 or outdeg != 1 or node_id not in self.g.get_input_ids():
                    #print("problème input")
                    return False

            elif label == 'output':
                if indeg != 1 or outdeg != 0 or node_id not in self.g.get_output_ids():
                    #print("problème output")
                    return False

            else:
                if node_id not in self.g.get_input_ids() and node_id not in self.g.get_output_ids():
                    #print("problème autre part")
                    return False

        return True
    
    @classmethod
    def PARSE_PARENTHESES(cls, *formulas):
        # le *formulas c'est pour dire que la fonction peut accepter plusieurs string
        inputs = []
        list_bool_circ = []

        # Pour chaque formule, construire un arbre de nœuds
        for formula in formulas:
            variable_nodes = {}
            g = cls(open_digraph([], [], []))
            # n0:
            g.g.add_node('', {}, {})
            # n1:
            g.g.add_node('', {g.g.get_node_ids()[0]:1}, {})
            current_node = g.g.get_node_by_id(0)
            s2 = ""

            for char in formula:
                if char == '(':
                    if current_node.get_label() != '|':
                        current_node.set_label(current_node.get_label() + s2)
                    parent_id = g.g.add_node()
                    g.g.add_edge(parent_id, current_node.get_id())
                    current_node = g.g.get_node_by_id(parent_id)
                    s2 = ""
                elif char == ')':
                    if current_node is not None:
                        current_node.set_label(current_node.get_label() + s2)
                    current_node = g.g.get_node_by_id(list(current_node.get_children().keys())[0])
                    s2 = ""
                else:
                    s2 += char

            #if current_node is not None:
            #    current_node.set_label(current_node.get_label() + s2)

            # Fusionner les nœuds avec le même label de variable
            for node in g.g.get_nodes():
                label = node.get_label()
                if label not in {'&', '|', '~', '', '^'}:
                    if label not in variable_nodes:
                        variable_nodes[label] = node
                    else:
                        g.g.fusion_noeuds(variable_nodes[label], node)

            # Créer les nœuds d'entrée pour chaque variable unique
            for label, node in variable_nodes.items():
                inputs.append(label)
                new_node_id = g.g.add_node()
                g.g.add_edge(new_node_id, node.get_id())
                node.set_label('')

            # Ajouter ce circuit booleen dans la liste
            list_bool_circ.append(g)
        
        # Une fois qu'on a tous les circuits booleen, on les fusionne en un seul graphe
        # Chaque sortie correspond à une formule
        circuit_fusion = list_bool_circ[0]
        for circuit in list_bool_circ[1:]:
            circuit_fusion.g.iparallel(circuit.g)

        return circuit_fusion, inputs

    @classmethod
    def random_bool_circ(cls, n, bound, inputs=1, outputs=1):
        """
        Génère un circuit booléen aléatoire avec un nombre spécifié d'entrées et de sorties.

        Paramètres :
        - n : int, nombre de nœuds dans le graphe.
        - bound : int, valeur maximale des poids des arêtes.
        - inputs : int, nombre d'entrées souhaitées.
        - outputs : int, nombre de sorties souhaitées.

        Retour :
        - Un circuit booléen aléatoire.
        """
        assert inputs >= 1 and outputs >= 1
        # Étape 1 : Générer un graphe dirigé acyclique aléatoire
        random_graph = open_digraph.random(n, bound, form="DAG")

        # Étape 2 : Ajouter des entrées et des sorties
        nb_inputs = 0
        nb_outputs = 0
        tab_inputs = [] # tableau des id des fils des inputs
        tab_outputs = [] # tableau des id des pères des outputs

        for node in random_graph.get_nodes():
            if node.get_parents() is None or node.get_parents() == {}:  # Si le nœud n'a pas de parents
                random_graph.add_input_node('input', node.get_id())
                nb_inputs += 1
                tab_inputs.append(node.get_id())
            if node.get_children() is None or node.get_children() == {}:  # Si le nœud n'a pas d'enfants
                random_graph.add_output_node('output', node.get_id())
                nb_outputs += 1
                tab_outputs.append(node.get_id())

        # Étape 2 bis : Ajuster le nombre d'entrées et de sorties
        tab_nodes = [
            node.get_id() for node in random_graph.get_nodes()
            if node.get_id() not in random_graph.get_input_ids() and
            node.get_id() not in random_graph.get_output_ids()
        ]

        while inputs > nb_inputs:
            random_input = random.choice(tab_nodes)
            random_graph.add_input_node(child_id = random_input)
            nb_inputs += 1

        while outputs > nb_outputs:
            random_output = random.choice(tab_nodes)
            random_graph.add_output_node(parent_id = random_output)
            nb_outputs += 1

        while inputs < nb_inputs:
            random_input_1 = random.choice(tab_inputs)
            tab_inputs.remove(random_input_1)
            random_input_2 = random.choice(tab_inputs)
            tab_inputs.remove(random_input_2)

            # Fusionner les deux nœuds d'entrée
            parent1 = list(random_graph.get_node_by_id(random_input_1).get_parents().keys())[0]
            parent2 = list(random_graph.get_node_by_id(random_input_2).get_parents().keys())[0]
            random_graph.remove_node_by_id(parent1)
            random_graph.remove_node_by_id(parent2)
            new_input_son_id = random_graph.add_node(label='', parents={}, children={random_input_1: 1, random_input_2: 1})
            random_graph.add_input_node('input', new_input_son_id)
            nb_inputs -= 1

        while outputs < nb_outputs:
            random_output_1 = random.choice(tab_outputs)
            tab_outputs.remove(random_output_1)
            random_output_2 = random.choice(tab_outputs)
            tab_outputs.remove(random_output_2)

            # Fusionner les deux nœuds de sortie
            child1 = list(random_graph.get_node_by_id(random_output_1).get_children().keys())[0]
            child2 = list(random_graph.get_node_by_id(random_output_2).get_children().keys())[0]
            random_graph.remove_node_by_id(child1)
            random_graph.remove_node_by_id(child2)
            new_output_father_id = random_graph.add_node(label='', parents={random_output_1 : 1, random_output_2 : 1}, children={})
            random_graph.add_output_node('output', new_output_father_id)
            nb_outputs -= 1

        # Étape 3 : Assigner des labels aux nœuds
        for node in random_graph.get_nodes():
            indegree = node.indegree()
            outdegree = node.outdegree()

            if indegree == 1 and outdegree == 1:
                node.set_label('~')  # Opérateur unaire
            elif indegree == 1 and outdegree > 1:
                node.set_label('')  # Copie
            elif indegree > 1 and outdegree == 1:
                node.set_label(random.choice(['|', '&']))  # Opérateur binaire
            elif indegree > 1 and outdegree > 1:
                # Séparer le nœud en deux
                new_node_id = random_graph.add_node(label=random.choice(['|', '&']), parents={}, children={})
                parent_ids = []
                for parent_id in node.get_parents().keys():
                    random_graph.add_edge(parent_id, new_node_id)
                    parent_ids.append(parent_id)
                for par_id in parent_ids:
                    random_graph.remove_parallel_edges(par_id, node.get_id())
                random_graph.add_edge(new_node_id, node.get_id())
                node.set_label('')
            elif node.get_id() in random_graph.get_input_ids():
                node.set_label('input')
            elif node.get_id() in random_graph.get_output_ids():
                node.set_label('output')
            
        return cls(random_graph)
    
    @classmethod
    def adder(cls, n):
        adder0 = bool_circ.adder_0()
        for i in range(n):
            adder0 = adder0.incrementeAdder()
        return adder0
    
    @classmethod
    def half_adder(cls, n):
        adder = bool_circ.adder(n).g
        input_ids = adder.get_input_ids()
        last_input_id = input_ids[len(input_ids) - 1]
        adder.inputs.remove(last_input_id)
        adder.get_node_by_id(last_input_id).set_label("0")
        return bool_circ(adder)


    @classmethod
    def adder_0(cls):
        n1 = node(1, "a0", {}, {4: 1})
        n2 = node(2, "b0", {}, {5: 1})
        n3 = node(3, "retenue", {}, {8: 1})

        copieInputA = node(4, "", {1: 1}, {6: 1, 9: 1})
        copieInputB = node(5, "", {2: 1}, {6: 1, 9: 1})

        xorAB = node(6, "^", {4: 1, 5: 1}, {7: 1})

        copieXorAB = node(7, "", {6: 1}, {11: 1, 10: 1})
        copieInputC = node(8, "", {3: 1}, {11: 1, 10: 1})

        n9 = node(9, "&", {4: 1, 5: 1}, {12: 1})
        n10 = node(10, "&", {7: 1, 8: 1}, {12: 1})
        n11 = node(11, "^", {7: 1, 8: 1}, {14: 1})

        n12 = node(12, "|", {9: 1, 10: 1}, {13: 1})

        n13 = node(13, "retenue", {12: 1}, {})
        n14 = node(14, "output", {11: 1}, {})
        
        g = open_digraph([1, 2, 3], [13, 14], [n1, n2, n3, copieInputA, copieInputB, xorAB, copieXorAB, copieInputC, n9, n10, n11, n12, n13, n14])
        return cls(g)
    
    def incrementeAdder(self):
        adder_1 = self.g
        adder_2 = adder_1.copy()

        inputs1 = adder_1.get_input_ids()
        inputs2 = adder_2.get_input_ids()

        retenue2_id = adder_2.get_output_ids()[0] 
        pere_retenue2_id = list(adder_2.get_node_by_id(retenue2_id).get_parents().keys())[0] #normalement l'id reste le même après l'appel à iparallel
        adder_2.remove_node_by_id(retenue2_id)

        inputC_id = inputs1[len(inputs1) - 1]
        fils_inputC_id = list(adder_1.get_node_by_id(inputC_id).get_children().keys())[0]
        adder_1.remove_node_by_id(inputC_id)

        taille_registre = len(inputs1)
        moitie_registre = taille_registre//2

        # Adder construit "en cascade de bas en haut" donc il faut adapter les labels en conséquence
        for i in range(len(inputs1)):
            input_id_1 = inputs1[i]
            input_1 = adder_1.get_node_by_id(input_id_1)
            if i % 2 == 0:
                label_num = taille_registre - 1 - (i // 2)
                input_1.set_label(f"a{label_num}")
            else:
                label_num = taille_registre - 1 - (i // 2)
                input_1.set_label(f"b{label_num}")

            input_id_2 = inputs2[i]
            input_2 = adder_2.get_node_by_id(input_id_2)
            if i % 2 == 0:
                label_num = moitie_registre - 1 - (i // 2)
                input_2.set_label(f"a{label_num}")
            else:
                label_num = moitie_registre - 1 - (i // 2)
                input_2.set_label(f"b{label_num}")


        M = adder_2.max_id()
        m = adder_1.min_id()
        fils_inputC_id += M - m + 1

        adder_1.iparallel(adder_2)

        adder_1.add_edge(pere_retenue2_id, fils_inputC_id)

        return bool_circ(adder_1)
    
    @classmethod
    def carry_lookahead_4(cls, reg1, reg2, retenue_label) -> 'bool_circ':
        """
        Crée un circuit Carry-Lookahead Adder (CLA) pour des registres de taille 4.

        Retour :
        - Un circuit booléen représentant un CLA pour des registres de taille 4.
        """

        # Vérification de la bonne taille des registres
        taille_reg1 = len(reg1.g.get_output_ids())
        taille_reg2 = len(reg2.g.get_output_ids())
        assert taille_reg1 == 4 and taille_reg2 == 4

        def add_edge_with_label(a, b, label):
            return g.add_node(label, {a:1, b:1}, {})

        g = open_digraph.empty()

        # inputs
        r1 = [g.add_node(label='') for _ in range(taille_reg1)]
        r2 = [g.add_node(label='') for _ in range(taille_reg2)]

        for i in range(4):
            id_parent = list(reg1.g.get_node_by_id(reg1.g.get_output_ids()[i]).get_parents().keys())[0]
            g.add_input_node(reg1.g.get_node_by_id(id_parent).get_label(), r1[i])
        for i in range(4):
            id_parent = list(reg2.g.get_node_by_id(reg2.g.get_output_ids()[i]).get_parents().keys())[0]
            g.add_input_node(reg2.g.get_node_by_id(id_parent).get_label(), r2[i])

        # pour la retenue
        c0_node = g.add_node(label='')
        g.add_input_node(retenue_label, c0_node)
        retenue = [c0_node]

        # generate et propagate
        generate, propagate = [], []
        for a, b in zip(r1, r2):
            generate.append(add_edge_with_label(a, b, '&'))
            p = add_edge_with_label(a, b, '^')
            # Ajout d'un noeud de copie pour passer is_well_formed
            cp = g.add_node(label='')
            g.add_edge(p, cp)
            propagate.append(cp)

        # retenue obtenue avec la relation récursive
        for i in range(4):
            p_and_c = add_edge_with_label(propagate[i], retenue[i], '&')
            ci     = add_edge_with_label(generate[i], p_and_c, '|')
            # Ajout d'un noeud de copie pour passer is_well_formed
            cp = g.add_node(label='')
            g.add_edge(ci, cp)
            retenue.append(cp)

        # pi ^ ci
        sommes = [add_edge_with_label(propagate[i], retenue[i], '^') for i in range(4)]

        # outputs
        for i in range(4):
            g.add_output_node(f"s{i}", sommes[i])
        g.add_output_node("c4", retenue[-1])
        return bool_circ(g)
    
    @classmethod
    def carry_lookahead_adder_4n(cls, reg1, reg2, retenue_label) -> 'bool_circ':
        """
        Chains 4‑bit carry‑lookahead blocks to handle any
        multiple of 4 bits by passing each block’s carry‑out
        into the next block’s carry‑in.
        """
        
        # Les registres doivent avoir la même taille multiple de 4
        taille_reg1 = len(reg1.g.get_output_ids())
        taille_reg2 = len(reg2.g.get_output_ids())
        assert taille_reg1 == taille_reg2 and taille_reg1 % 4 == 0
        blocs = taille_reg1 // 4

        reg1_4 = bool_circ(reg1.g.copy())
        reg1_4_nodes = reg1.g.get_nodes()[0 : 4]
        reg1_4.g.remove_nodes_by_id(reg1_4.g.get_node_ids())
        for node in reg1_4_nodes:
            output_id = reg1_4.g.add_output_node("output")
            reg1_4.g.add_node(node.get_label(), {}, {output_id:1})

        reg2_4 = bool_circ(reg2.g.copy())
        reg2_4_nodes = reg2.g.get_nodes()[0 : 4]
        reg2_4.g.remove_nodes_by_id(reg2_4.g.get_node_ids())
        for node in reg2_4_nodes:
            output_id = reg2_4.g.add_output_node("output")
            reg2_4.g.add_node(node.get_label(), {}, {output_id:1})

        circ = cls.carry_lookahead_4(reg1_4, reg2_4, retenue_label)

        # Pour chaque bloc de 4 bits suivants
        for i in range(1, blocs):
            retenue_label = f"retenue{4*i}"

            reg1_4i = bool_circ(reg1.g.copy())
            reg1_4i_nodes = reg1.g.get_nodes()[4*i : 4*(i+1)]
            reg1_4i.g.remove_nodes_by_id(reg1_4i.g.get_node_ids())
            for node in reg1_4i_nodes:
                output_id = reg1_4i.g.add_output_node("output")
                reg1_4i.g.add_node(node.get_label(), {}, {output_id:1})

            reg2_4i = bool_circ(reg2.g.copy())
            reg2_4i_nodes = reg2.g.get_nodes()[4*i : 4*(i+1)]
            reg2_4i.g.remove_nodes_by_id(reg2_4i.g.get_node_ids())
            for node in reg2_4i_nodes:
                output_id = reg2_4i.g.add_output_node("output")
                reg2_4i.g.add_node(node.get_label(), {}, {output_id:1})

            bloc = cls.carry_lookahead_4(reg1_4i, reg2_4i, retenue_label)
            merged = circ.g.parallel(bloc.g)


            #merge the carry out of the previous block with the carry in of the next block
            # find the carry out of the previous block
            try:
                out_id = next(
                    oid for oid in merged.get_output_ids()
                    if merged.get_id_node_map()[oid].get_label() == retenue_label
                )
                parent = list(merged.get_id_node_map()[out_id].parents.keys())[0]
                merged.remove_node_by_id(out_id)
            

                # find the carry in of the next block
                in_id = next(
                    iid for iid in merged.get_input_ids()
                    if merged.get_id_node_map()[iid].get_label() == retenue_label
                )
                child = list(merged.get_id_node_map()[in_id].children.keys())[0]
                merged.remove_node_by_id(in_id)

                merged.add_edge(parent, child)
            except:
                pass

            circ = bool_circ(merged)

        return circ
    
    @classmethod
    def from_int(cls, value: int, size: int = 8) -> 'bool_circ':
        """
        Crée un circuit booléen représentant un entier sous forme de registre.
        """
        assert value >= 0, "Seuls les entiers non signés sont supportés"
        assert value < 2**size, f"Impossible de représenter {value} sur {size} bits"

        g = open_digraph([], [], [])
        bitstring = bin(value)[2:].zfill(size)  # e.g. '00001101'

        for i, bit in enumerate(bitstring):  # LSB à droite
            bit_node = g.add_node(label=bit)
            output_id = g.add_output_node(f"b{len(bitstring)-i-1}")
            g.add_edge(bit_node, output_id)

        return cls(g)
    
    def simplifie_bool_circ(self, node_id):
        """
        Prend en entrée un id de noeud;
        regarde son fils (si c'est 0 ou 1) ou ses parents (si c'est une opération) et applique si possible une simplification.
        """
        if(node_id not in self.g.get_node_ids()):
            return False
        noeud = self.g.get_node_by_id(node_id)
        label_noeud = noeud.get_label()

        if label_noeud in {'0', '1'}:
            fils_ids = list(noeud.get_children().keys())
            assert len(fils_ids) == 1
            fils_id = fils_ids[0]
            fils = self.g.get_node_by_id(fils_id)
            label_fils = fils.get_label()
            petit_fils_ids = list(fils.get_children().keys())
            
            if label_fils == '':
                for pf_id in petit_fils_ids:
                    self.g.add_node(label_noeud, {}, {pf_id: 1})
                self.g.remove_node_by_id(node_id)
                self.g.remove_node_by_id(fils_id)
                return True

            elif label_fils == '~':
                petit_fils_id = next(iter(fils.get_children().keys()))
                new_label = '1' if label_noeud == '0' else '0'
                self.g.add_node(new_label, {}, {petit_fils_id: 1})
                self.g.remove_node_by_id(node_id)
                self.g.remove_node_by_id(fils_id)
                return True

            elif label_fils == '&':
                if label_noeud == '0':
                    # Supprimer le noeud 0
                    self.g.remove_node_by_id(node_id)

                    # Récupérer les parents et l'enfant du noeud ET
                    # Copie pour ne pas subir les effets des modifications plus tard
                    parents_of_and_node = list(fils.get_parents().keys()).copy()
                    child_of_and_node = list(fils.get_children().keys())[0]

                    # Supprimer le noeud ET
                    self.g.remove_node_by_id(fils_id)

                    # Pour chaque parent ajouter un noeud copie en fils
                    for parent in parents_of_and_node:
                        self.g.add_node('', {parent:1}, {})

                    # Ajouter un noeud 0 avec comme fils celui récupéré avant
                    self.g.add_node('0', {}, {child_of_and_node:1})
                    return True

                else:
                    self.g.remove_node_by_id(node_id)
                    return True

            elif label_fils == '|':
                if label_noeud == '1':
                    # Supprimer le noeud 1
                    self.g.remove_node_by_id(node_id)

                    # Récupérer les parents et l'enfant du noeud OU
                    # Copie pour ne pas subir les effets des modifications plus tard
                    parents_of_or_node = list(fils.get_parents().keys()).copy()
                    child_of_or_node = list(fils.get_children().keys())[0]

                    # Supprimer le noeud OU
                    self.g.remove_node_by_id(fils_id)

                    # Pour chaque parent ajouter un noeud copie en fils
                    for parent in parents_of_or_node:
                        self.g.add_node('', {parent:1}, {})

                    # Ajouter un noeud 1 avec comme fils celui récupéré avant
                    self.g.add_node('1', {}, {child_of_or_node:1})
                    return True

                else:
                    self.g.remove_node_by_id(node_id)
                    return True

            elif label_fils == '^':
                if label_noeud == '1':
                    for pf_id in petit_fils_ids:
                        # On ajoute un NOT (~) autour du XOR
                        not_node = self.g.add_node('~', {fils_id: 1}, {pf_id: 1})
                    self.g.remove_parallel_edges(fils_id, pf_id)
                self.g.remove_node_by_id(node_id)
                return True
            
            else:
                return False

        elif label_noeud in {'|', '^', '&'}:
            parents_ids = list(noeud.get_parents().keys())
            if len(parents_ids) != 0:
                return False
            elif label_noeud == '&':
                noeud.set_label('1')
                return True
            else:
                noeud.set_label('0')
                return True
            
        else:
            return False
    
    
    def evaluate(self, verbose: bool = False) -> None:
        """
        Simplifie le circuit booléen en appliquant les règles de simplification et de réécriture
        jusqu'à ce qu'aucune transformation ne soit possible.

        verbose : si True, affiche chaque transformation appliquée.
        """
        changed = True
        etape = 1
        while changed:
            changed = False
            node_ids = list(self.g.get_node_ids())
            
            for node_id in node_ids:
                # Le noeud peut avoir été supprimé par une simplification précédente
                if node_id not in self.g.get_node_ids():
                    continue

                # on essaie de simplifie
                if self.simplifie_bool_circ(node_id):
                    if verbose:
                        print(f"Simplification appliquée sur le noeud {node_id} à l'étape {etape}")
                    changed = True
                    etape += 1
                    continue  # on passe au noeud suivant après simplification
                
                # Essayer de réécrire
                avant = len(self.g.get_node_ids())
                self.rewrite(node_id)
                apres = len(self.g.get_node_ids())

                if avant != apres or node_id not in self.g.get_node_ids():
                    if verbose:
                        print(f"Réécriture appliquée sur le noeud {node_id} à l'étape {etape}")
                    changed = True
                    etape += 1

    @classmethod
    def encodeur_4_bits(cls, bit1, bit2, bit3, bit4):
        n1 = node(1, bit1, {}, {5: 1})
        n2 = node(2, bit2, {}, {6: 1})
        n3 = node(3, bit3, {}, {7: 1})
        n4 = node(4, bit4, {}, {8: 1})

        n5 = node(5, "", {1: 1}, {9: 1, 10: 1, 15: 1})
        n6 = node(6, "", {2: 1}, {9: 1, 11: 1, 16: 1})
        n7 = node(7, "", {3: 1}, {10: 1, 11: 1, 17: 1})
        n8 = node(8, "", {4: 1}, {9: 1, 10: 1, 11: 1, 18: 1})

        n9 = node(9, "^", {5: 1, 6: 1, 8: 1}, {12: 1})
        n10 = node(10, "^", {5: 1, 7: 1, 8: 1}, {13: 1})
        n11 = node(11, "^", {6: 1, 7: 1, 8: 1}, {14: 1})

        n12 = node(12, "outXor1", {9: 1}, {})
        n13 = node(13, "outXor2", {10: 1}, {})
        n14 = node(14, "outXor3", {11: 1}, {})
        
        n15 = node(15, "out1", {5: 1}, {})
        n16 = node(16, "out2", {6: 1}, {})
        n17 = node(17, "out3", {7: 1}, {})
        n18 = node(18, "out4", {8: 1}, {})

        g = open_digraph([1, 2, 3, 4], [12, 13, 14, 15, 16, 17, 18], [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14, n15, n16, n17, n18])
        return bool_circ(g)

    @classmethod
    def decodeur_4_bits(cls, bit1, bit2, bit3, bit4, bit5, bit6, bit7):
        n1 = node(1, bit1, {}, {5: 1})
        n2 = node(2, bit2, {}, {6: 1})
        n3 = node(3, bit3, {}, {7: 1})
        n4 = node(4, bit4, {}, {8: 1})
        n5_b = node(51, bit5, {}, {9: 1})
        n6_b = node(61, bit6, {}, {10: 1})
        n7_b = node(71, bit7, {}, {11: 1}) 

        n5 = node(5, "", {1: 1}, {9: 1, 10: 1, 15: 1})
        n6 = node(6, "", {2: 1}, {9: 1, 11: 1, 16: 1})
        n7 = node(7, "", {3: 1}, {10: 1, 11: 1, 17: 1})
        n8 = node(8, "", {4: 1}, {9: 1, 10: 1, 11: 1, 18: 1})

        n9 = node(9, "^", {5: 1, 6: 1, 8: 1, 51: 1}, {12: 1})
        n10 = node(10, "^", {5: 1, 7: 1, 8: 1, 61: 1}, {13: 1})
        n11 = node(11, "^", {6: 1, 7: 1, 8: 1, 71: 1}, {14: 1})

        n12 = node(12, "", {9: 1}, {29: 1, 26: 1, 24: 1, 23: 1})
        n13 = node(13, "", {10: 1}, {28: 1, 26: 1, 25: 1, 23: 1})
        n14 = node(14, "", {11: 1}, {27: 1, 26: 1, 25: 1, 24: 1})

        n15 = node(15, "^", {5: 1, 23: 1}, {19: 1})
        n16 = node(16, "^", {6: 1, 24: 1}, {20: 1})
        n17 = node(17, "^", {7: 1, 25: 1}, {21: 1})
        n18 = node(18, "^", {8: 1, 26: 1}, {22: 1})

        n19 = node(19, "output1", {15: 1}, {})
        n20 = node(20, "output2", {16: 1}, {})
        n21 = node(21, "output3", {17: 1}, {})
        n22 = node(22, "output4", {18: 1}, {})
        
        n23 = node(23, "&", {27: 1, 12: 1, 13: 1}, {15: 1})
        n24 = node(24, "&", {28: 1, 12: 1, 14: 1}, {16: 1})
        n25 = node(25, "&", {29: 1, 13: 1, 14: 1}, {17: 1})
        n26 = node(26, "&", {12: 1, 13: 1, 14: 1}, {18: 1})

        n27 = node(27, "~", {14: 1}, {23: 1})
        n28 = node(28, "~", {13: 1}, {24: 1})
        n29 = node(29, "~", {12: 1}, {25: 1})

        g = open_digraph([1, 2, 3, 4, 51, 61, 71], [19, 20, 21, 22],
                         [n1, n2, n3, n4, n5_b, n6_b, n7_b, n5, n6, n7, n8, n9, n10, n11, n12, n13,
                           n14, n15, n16, n17, n18, n19, n20, n21, n22, n23, n24, n25, n26, n27, n28, n29])
        return bool_circ(g)



    def rewrite(self, node_id):
        noeud = self.g.get_node_by_id(node_id)
        if noeud is None:
            return  # Le nœud a déjà été supprimé

        label_noeud = noeud.get_label()
        enfants = list(noeud.get_children().keys())
        parents = list(noeud.get_parents().keys())

        if label_noeud == '^':
            # Association de XOR
            if enfants:
                enfant_id = enfants[0]
                enfant_node = self.g.get_node_by_id(enfant_id)
                if enfant_node is not None and enfant_node.get_label() == '^':
                    for parent in noeud.get_parents().keys():
                        self.g.add_edge(parent, enfant_node.get_id())
                    self.g.remove_node_by_id(node_id)

            for parent in parents:
                parent_node = self.g.get_node_by_id(parent)
                if parent_node is None:
                    continue  # Parent supprimé
                # Involution de XOR
                if noeud.get_parents()[parent] > 1:
                    self.g.remove_parallel_edges(parent, node_id)
                    if noeud.get_parents().get(parent, 0) % 2 == 1:
                        self.g.add_edge(parent, node_id)
                # NON à travers XOR
                if parent_node.get_label() == '~':
                    self.g.add_edge(node_id, parent)  # noeud "~" devient enfant du XOR
                    self.g.remove_parallel_edges(node_id, parent)
                    parent_du_non_list = list(parent_node.get_parents().keys())
                    if parent_du_non_list:
                        parent_du_non = parent_du_non_list[0]
                        self.g.add_edge(parent_du_non, node_id)
                        self.g.remove_parallel_edges(parent_du_non, parent)
                    enfant_du_XOR_list = list(noeud.get_children().keys())
                    if enfant_du_XOR_list:
                        enfant_du_XOR = enfant_du_XOR_list[0]
                        self.g.add_edge(parent, enfant_du_XOR)
                        self.g.remove_parallel_edges(node_id, enfant_du_XOR)

        elif label_noeud == '':
            # Association de copies
            for enfant in enfants:
                enfant_node = self.g.get_node_by_id(enfant)
                if enfant_node is not None and enfant_node.get_label() == '':
                    petits_fils = list(enfant_node.get_children().keys())
                    for petit_fils in petits_fils:
                        self.g.add_edge(node_id, petit_fils)
                    self.g.remove_node_by_id(enfant)

        elif label_noeud != '':
            # Effacement : un noeud dont le fils est une copie sans enfant ne sert plus à rien.
            # La règle ne s'applique que si la copie n'a aucun enfant : sinon on supprimerait
            # un calcul encore utilisé plus bas dans le circuit (résultats faux à l'évaluation).
            if not enfants:
                return  # pas de fils, rien à faire
            enfant = enfants[0]
            enfant_node = self.g.get_node_by_id(enfant)
            if (enfant_node is not None and enfant_node.get_label() == ''
                    and not enfant_node.get_children()):
                self.g.remove_node_by_id(node_id)
                self.g.remove_node_by_id(enfant)
                for parent in parents:
                    self.g.add_node('', {parent: 1}, {})

        elif label_noeud == '~':
            if not enfants or not parents:
                return
            enfant = enfants[0]
            parent = parents[0]
            enfant_node = self.g.get_node_by_id(enfant)
            if enfant_node is not None and enfant_node.get_label() == '':
                self.g.add_edge(parent, enfant)
                self.g.remove_node_by_id(node_id)
                petits_fils = list(enfant_node.get_children().keys())
                for petit_fils in petits_fils:
                    self.g.add_node('~', {enfant: 1}, {petit_fils: 1})
            elif enfant_node is not None and enfant_node.get_label() == '~':
                petit_fils_list = list(enfant_node.get_children().keys())
                if petit_fils_list:
                    petit_fils = petit_fils_list[0]
                    self.g.add_edge(parent, petit_fils)
                    self.g.remove_node_by_id(node_id)
                    self.g.remove_node_by_id(enfant)
                    
    def remplace_inputs(self, registre1, registre2, half = False):
        """
        Remplace les nœuds d'entrée d'un adder par des nœuds normaux avec des labels 0 ou 1,
        en fonction des valeurs du registre.
        """
        # Récupérer les ids des nœuds d'entrée du circuit et des sorties du registre
        input_ids = self.g.get_input_ids()
        registre1_output_ids = registre1.g.get_output_ids()
        registre2_output_ids = registre2.g.get_output_ids()

        # Vérifier que le nombre d'entrées correspond au nombre de sorties du registre,
        assert len(input_ids) == len(registre1_output_ids) + len(registre2_output_ids) + half

        registre1.g.iparallel(registre2.g)

    @classmethod
    def composition_encodeur_decodeur(cls, bit1, bit2, bit3, bit4):
        encodeur = cls.encodeur_4_bits(bit1, bit2, bit3, bit4)
        encodeur.evaluate()
        labels = []
        for id in encodeur.g.get_output_ids():
            output = encodeur.g.get_node_by_id(id)
            parent_id = list(output.get_parents().keys())[0]
            parent = encodeur.g.get_node_by_id(parent_id)
            labels.append(parent.get_label())
        # L'encodeur sort d'abord les 3 bits de parité puis les 4 bits de données,
        # alors que le décodeur attend les 4 bits de données puis les 3 bits de parité.
        decodeur = cls.decodeur_4_bits(labels[3], labels[4], labels[5], labels[6], labels[0], labels[1], labels[2])
        decodeur.evaluate()
        return decodeur
