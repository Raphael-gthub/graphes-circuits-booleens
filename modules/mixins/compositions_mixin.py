class OpenDigraphCompositionsMixin:
    def add_edge(self, src: int, tgt: int):
        """Ajoute une arête entre deux noeuds."""
        if src not in self.nodes or tgt not in self.nodes:
            raise ValueError(
                f"Un ou les deux nœuds (src={src}, tgt={tgt})\
                n'existent pas dans le graphe."
            )

        src_node = self.nodes[src]
        tgt_node = self.nodes[tgt]

        src_node.add_child_id(tgt, 1)
        tgt_node.add_parent_id(src, 1)

    def add_edges(self, edges):
        """Ajoute plusieurs arêtes à la fois."""
        for src, tgt in edges:
            self.add_edge(src, tgt)

    def add_node(self, label: str='', parents: dict[int : int]=None, children: dict[int: int]=None):
        """Ajoute un noeud au graphe avec des parents et enfants optionnels."""
        if parents is None:
            parents = {}
        if children is None:
            children = {}

        new_id = self.new_id()
        new_node = self.node(new_id, label, {}, {})

        self.nodes[new_id] = new_node

        for key in parents.keys():
            self.add_edge(key, new_id)
        for key in children.keys():
            self.add_edge(new_id, key)

        return new_id

    def remove_edge(self, src: int, tgt: int):
        """Supprime une arête entre deux noeuds."""
        parent = self.get_node_by_id(src)
        gosse = self.get_node_by_id(tgt)
        parent.remove_child_once(tgt)
        gosse.remove_parent_once(src)

    def remove_parallel_edges(self, src, tgt):
        gosse = self.get_node_by_id(tgt)
        parent = self.get_node_by_id(src)
        
        if src in gosse.get_parents():
            gosse.remove_parent_id(src)
        else:
            # print(f"Avertissement : {src} n'était pas parent de {tgt}, aucune suppression faite.")
            pass
        
        if tgt in parent.get_children():
            parent.remove_child_id(tgt)
        else:
            # print(f"Avertissement : {tgt} n'était pas enfant de {src}, aucune suppression faite.")
            pass

    def remove_node_by_id(self, node_id):
        """Supprime un nœud ainsi que ses relations avec les autres noeuds."""
        node = self.get_node_by_id(node_id)
        parents = node.get_parents()
        gosses = node.get_children()
        liste_parents = list(parents.keys())
        liste_gosses = list(gosses.keys())

        # Suppression des relations parents-enfants
        for parent_id in liste_parents:
            self.remove_parallel_edges(parent_id, node_id)
        for gosse_id in liste_gosses:
            self.remove_parallel_edges(node_id, gosse_id)

        # Suppression du noeud
        del self.nodes[node_id]
        if node_id in self.inputs:
            self.inputs.remove(node_id)
        if node_id in self.outputs:
            self.outputs.remove(node_id)

    def remove_edges(self, args):
        """Supprime une arrête de chaque paire (src, tgt)."""
        for (src, tgt) in args:
            self.remove_edge(src, tgt)

    def remove_several_parallel_edges(self, args):
        """Supprime toutes les arrêtes entre chaque paires (src, tgt)."""
        for (src, tgt) in args:
            self.remove_parallel_edges(src, tgt)

    def remove_nodes_by_id(self, node_ids):
        """Supprime plusieurs noeuds du graphe."""
        for node_id in node_ids:
            self.remove_node_by_id(node_id)

    def add_input_node(self, label='', child_id=None):
        """Ajoute un noeud d'entrée au graphe."""
        if child_id is None:
            #child_id = {}
            new_id = self.add_node(label, {}, {})
        else:
            new_id = self.add_node(label, {}, {child_id: 1})

        self.add_input_id(new_id)

        return new_id

    def add_output_node(self, label='', parent_id=None):
        """Ajoute un noeud de sortie au graphe."""
        if parent_id is None:
            #parent_id = {}
            new_id = self.add_node(label, {}, {})
        else:
            new_id = self.add_node(label, {parent_id: 1}, {})

        self.add_output_id(new_id)

        return new_id
    
    def iparallel(self, g):
        """
        Modifie self en ajoutant les nœuds et arêtes de g
        avec des indices décalés.
        """
        if not g.nodes:
            return  # Si g est vide, rien à faire

        M = g.max_id()
        m = self.min_id()

        # Translation des indices
        self.shift_indices(M - m + 1)

        # Mise à jour des ids input et output
        for input in g.get_input_ids():
            self.add_input_id(input)
        for output in g.get_output_ids():
            self.add_output_id(output)

        # Ajout des noeuds du deuxième graphe
        for id, node in g.get_id_node_map().items():
            self.nodes[id] = node.copy()

    def parallel(self, g):
        """
        Renvoie un nouveau graphe représentant
        la composition parallèle de self et g.
        """
        f = self.copy()
        f.iparallel(g)
        return f

    def icompose(self, f):
        if len(self.inputs) != len(f.outputs):
            raise ValueError("Le nombre d'entrées de self ne correspond pas au nombre de sorties de f.")

        i = 0

        M = f.max_id()
        m = self.min_id()
        self.shift_indices(M - m + 1)
        liste_inputs = self.get_input_ids().copy()

        self.inputs = f.inputs

        for id, node in f.get_id_node_map().items():
            self.nodes[id] = node.copy()
        
        for node_id in f.get_output_ids():
            self.add_edge(node_id, liste_inputs[i])
            i += 1

    def icompose_simplifie(self, f):
        '''
        Fait comme icompose, mais retire directement les inputs/outputs inutiles
        Fonction normalement utile pour la simplification de graphes du TP11/12
        '''
        if len(self.inputs) != len(f.outputs):
            raise ValueError("Le nombre d'entrées de self ne correspond pas au nombre de sorties de f.")

        i = 0

        M = f.max_id()
        m = self.min_id()
        self.shift_indices(M - m + 1)
        liste_inputs = self.get_input_ids().copy()

        liste_fils_inputs_ids = [list(self.get_node_by_id(input).get_children().keys())[0] for input in liste_inputs]

        for input in liste_inputs:
            self.remove_node_by_id(input)

        self.inputs = f.inputs

        for id, node in f.get_id_node_map().items():
            self.nodes[id] = node.copy()

        for node_id in f.get_output_ids().copy():
            pere_output_id = list(self.get_node_by_id(node_id).get_parents().keys())[0]
            self.add_edge(pere_output_id, liste_fils_inputs_ids[i])
            self.remove_node_by_id(node_id)
            i += 1


    def compose(self, f):
        g = self.copy()
        g.icompose(f)
        return g

    @classmethod
    def identity(cls, n):
        list_nodes = []
        tab_inputs = []
        tab_outputs = []
        for i in range(n):
            n1 = cls.node(i, "node " + str(i), {}, {i + n: 1})
            n2 = cls.node(i + n, "node " + str(i), {i: 1}, {})
            list_nodes.append(n1)
            list_nodes.append(n2)
            tab_inputs.append(i)
            tab_outputs.append(i + n)
        return cls(tab_inputs, tab_outputs, list_nodes)

    def connected_components(self):
            """
            Renvoie le nombre de composantes connexes et un dictionnaire associant à chaque id
            de nœud un entier représentant sa composante connexe.
            """
            visited = set()  # Ensemble des nœuds déjà visités
            component_dict = {}  # Dictionnaire pour associer chaque nœud à sa composante connexe
            component_id = 0  # Identifiant de la composante connexe en cours
            
            def dfs(node_id):
                """DFS pour explorer les nœuds connectés à partir de node_id."""
                stack = [node_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component_dict[current] = component_id  # Associer le nœud à la composante
                        # Ajouter les voisins non visités à la pile
                        current_node = self.get_node_by_id(current)
                        for neighbor_id in current_node.get_children().keys():
                            if neighbor_id not in visited:
                                stack.append(neighbor_id)
                        for parent_id in current_node.get_parents().keys():
                            if parent_id not in visited:
                                stack.append(parent_id)

            # Parcours de tous les nœuds
            for node_id in self.get_node_ids():
                if node_id not in visited:
                    # Si le nœud n'a pas été visité, démarrer un DFS depuis ce nœud
                    dfs(node_id)
                    component_id += 1  # Passer à la composante suivante
            
            # Le nombre de composantes est simplement l'id de la dernière composante
            return component_id, component_dict
    
    def connected_components_graphs(self):
        """
        Renvoie une liste d'open_digraphs,
        chaque graph représentant une composante connexe
        du graphe de départ.
        """
        visited = set()  # Ensemble des nœuds déjà visités
        component_graphs = []  # Liste pour stocker les sous-graphes des composantes
        
        def dfs(node_id, current_component_nodes, current_component_edges):
            """DFS pour explorer les nœuds connectés à partir de node_id et collecter les arêtes."""
            stack = [node_id]

            while stack:
                current = stack.pop()

                if current not in visited:
                    visited.add(current)
                    current_component_nodes.add(current)

                    # Ajouter les arêtes sortantes
                    current_node = self.get_node_by_id(current)

                    for neighbor_id in current_node.get_children().keys():
                        if neighbor_id not in visited:
                            stack.append(neighbor_id)
                        current_component_edges.add((current, neighbor_id))

                    # Ajouter les arêtes entrantes
                    for parent_id in current_node.get_parents().keys():
                        if parent_id not in visited:
                            stack.append(parent_id)
                        current_component_edges.add((parent_id, current))
        
        # Exploration de tous les nœuds pour découvrir les composantes connexes
        for node_id in self.get_node_ids():
            if node_id not in visited:
                # Si le nœud n'a pas été visité, démarrer un DFS depuis ce nœud
                current_component_nodes = set()  # Ensemble des nœuds dans la composante
                current_component_edges = set()  # Ensemble des arêtes dans la composante
                dfs(node_id, current_component_nodes, current_component_edges)
                
                # Créer un sous-graphe pour cette composante
                subgraph_nodes = [self.get_node_by_id(n) for n in current_component_nodes]
                subgraph = self.__class__(
                    list(current_component_nodes & set(self.inputs)),  # Inputs de la composante
                    list(current_component_nodes & set(self.outputs)),  # Outputs de la composante
                    subgraph_nodes
                )
                
                # Ajouter les arêtes du sous-graphe
                subgraph.add_edges(list(current_component_edges))
                
                # Ajouter le sous-graphe à la liste des composantes
                component_graphs.append(subgraph)
        
        return component_graphs
    
    def fusion_noeuds(self, n1, n2):
        """
        Ici, n1 et n2 sont 2 noeuds du graphe.
        La fusion consiste à faire que: 
        - Tous les parents et fils de n1 et n2 sont des parents/fils du nouveau noeud
        - Le noeud a le label et l'id de n1
        - Si n1 était un input/output, le noeud final en est un aussi
        - Peut parfaitement créer des graphes pas du tout valides
        (par exemple un grapĥe avec un input qui a des parents)
        """
        for parent, mult in n2.get_parents().items():
            self.add_edges([(parent, n1.get_id()) for i in range(mult)])
            # autre ligne à tester si l'autre ne fonctionne pas
            # self.add_edge(self.get_node_by_id(parent), n1)
        for children, mult in n2.get_children().items():
            self.add_edges([(n1.get_id(), children) for i in range(mult)])
        self.remove_node_by_id(n2.get_id())

    def shift_indices(self, n):
        """
        Modifie les indices des nœuds, entrées et sorties de self
        en les décalant de n.
        TODO : optimiser pour ne pas modifier directement l'attribut
        """

        new_nodes = {}

        # set plus rapide que list
        set_old_inputs_ids = set(self.get_input_ids())
        set_old_outputs_ids = set(self.get_output_ids())

        for node in self.get_nodes():
            # Récupération des anciens ids
            old_id = node.get_id()
            new_id = old_id + n

            # Modification des ids d'input et d'output
            if old_id in set_old_inputs_ids:
                self.inputs.remove(old_id)
                self.add_input_id(new_id)

            if old_id in set_old_outputs_ids:
                self.outputs.remove(old_id)
                self.add_output_id(new_id)

            # Modifier id du noeud
            node.set_id(new_id)

            # Modifier id des parents/enfants dans le dictionnaire de ce noeud
            dict_parent = node.get_parents()
            parent_id_list = list(dict_parent.keys())
            for parent_id in parent_id_list:
                multiplicity = dict_parent.pop(parent_id)
                dict_parent[parent_id + n] = multiplicity

            dict_children = node.get_children()
            children_id_list = list(dict_children.keys())
            for children_id in children_id_list:
                multiplicity = dict_children.pop(children_id)
                dict_children[children_id + n] = multiplicity

            # Ajouter ces modifications au graphe
            new_nodes[node.get_id()] = node

        self.nodes = new_nodes
