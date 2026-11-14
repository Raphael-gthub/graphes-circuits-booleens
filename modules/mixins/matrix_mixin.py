class OpenDigraphMatrixMixin:
    def adjency_matrix(self):
            """Retourne la matrice d'adjacence du graphe."""
            nb_node = len(self.nodes)
            # Création d'une matrice avec que des 0
            Matrix = [[0 for _ in range(nb_node)] for _ in range(nb_node)]
            dic = self.id_to_range_node()

            # Pour chaque noeud, récupérations de ses parents en enfantss
            for node in self.get_nodes():
                parents = node.get_parents()
                children = node.get_children()

                # Ajout de la multiplicité avec les ids réindexés
                for parent_id, m in parents.items():
                    if m != 0:
                        Matrix[dic[node.get_id()]][dic[parent_id]] = m

                for child_id, m in children.items():
                    if m != 0:
                        Matrix[dic[child_id]][dic[node.get_id()]] = m

            return Matrix