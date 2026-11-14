class OpenDigraphLongestPathMixin:
    def tri_topologique(self):
        """
        Renvoie une liste de sets avec dans chaque set Li les noeuds de profondeur i.
        """
        if self.is_cyclic():
            raise ValueError("Le graphe donné ne doit pas être cyclique !")

        stack = []
        g = self.copy()
        while not g.is_empty():
            visited = set()
            for node in g.get_nodes():
                if node.get_parents() == {}:
                    visited.add(node.get_id())
            stack.append(visited)
            for node_id in visited:
                g.remove_node_by_id(node_id)
        return stack

    def profondeur_graphe(self):
        return len(self.tri_topologique())-1

    def profondeur_noeud(self, node):
        if node in self.nodes.values():
            list_of_set_of_node_id = self.tri_topologique()
            for e in list_of_set_of_node_id:
                if node.get_id() in e:
                    return list_of_set_of_node_id.index(e)
        raise ValueError("Le noeud donné n'est pas dans le graphe")

    def longest_path(self, u, v):
        if self.is_cyclic():
            raise ValueError("Le graphe donné ne doit pas être cyclique !")

        dist = {u: 0}
        prev = {}
        indice = -1
        tri_topo = self.tri_topologique()

        # Trouver l'indice de l'ensemble contenant le noeud u
        for i in range(len(tri_topo)):
            if u in tri_topo[i]:
                indice = i
                break

        # Parcourir les ensembles à partir de l'indice trouvé
        for i in range(indice + 1, len(tri_topo)):
            for w in tri_topo[i]:
                parent_max = -1
                for parent in self.get_node_by_id(w).get_parents():
                    if parent in dist and dist[parent] > parent_max:
                        parent_max = dist[parent]
                        prev[w] = parent
                if parent_max != -1:
                    dist[w] = parent_max + 1
                if w == v:
                    # Reconstruire le chemin
                    path = [v]
                    node = v
                    while node in prev:
                        node = prev[node]
                        path.append(node)
                    path.reverse()
                    return path, dist[v]

        raise ValueError("Le noeud v n'est pas atteignable depuis le noeud u.")
