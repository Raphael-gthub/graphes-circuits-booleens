class OpenDigraphShortestPathMixin:
    def dijkstra(self, src: int, tgt: int = None, direction=None):
        """
        Implémente l'algo de Dijkstra pour trouver le chemin le plus court
        à partir du noeud source src_id vers tous les autres nœuds du graphe.
        Si tgt_id est spécifié, retourne les résultats dès que le chemin le
        plus court vers tgt_id est trouvé.

        @param src_id: id noeud source
        @param tgt_id: id noeud cible (optionnel)
        @param direction: La direction de la recherche.
                            None pour les deux directions,
                            -1 pour les parents,
                            1 pour les enfants.
        @return: tuple (dist, prev) où dist est un dictionnaire des distances
                 les plus courtes à partir de src, et prev est un dictionnaire
                 des prédécesseurs pour reconstruire le chemin.
        """
        Q = [src]
        dist = {src: 0}
        prev = {}
        while Q != []:
            # Trouver le noeud avec la distance minimale dans Q
            u = min(Q, key=lambda node_id: dist[node_id])
            Q.remove(u)

            # Si tgt_id est spécifié et que nous avons atteint tgt,
            # retourner les résultats
            if tgt is not None and u == tgt:
                return dist, prev

            # Récupérer les voisins en fonction de la direction
            if direction is None:
                parent_node_list =\
                    list({id for id in
                          self.get_node_by_id(u).get_parents().keys()})
                children_node_list =\
                    list({id for id in
                          self.get_node_by_id(u).get_children().keys()})
                neighbors = parent_node_list + children_node_list
            elif direction == -1:
                neighbors = list({id for id in
                                  self.get_node_by_id(u).get_parents().keys()})
            else:
                neighbors = list({id for id in
                                 self.get_node_by_id(u).get_children().keys()})

            for v in neighbors:
                if v not in dist:
                    Q.append(v)
                if v not in dist or dist[v] > dist[u] + 1:
                    dist[v] = dist[u] + 1
                    prev[v] = u
        return dist, prev

    def shortest_path(self, src, tgt, direction=None):
        """
        Trouve le chemin le plus court entre src_id et tgt_id en utilisant
        l'algorithme de Dijkstra.

        @param src_id: id noeud source.
        @param tgt_id: id noeud cible.
        @param direction: La direction de la recherche.
                            None pour les deux directions,
                            -1 pour les parents,
                            1 pour les enfants.
        @return: liste des noeuds représentant le chemin le plus court.
        """
        dist, prev = self.dijkstra(src, tgt, direction)
        path = [tgt]
        node = tgt

        while node in prev:
            node = prev[node]
            path.append(node)

        path.reverse()
        return path
    
    def ancetre_commun(self, id1, id2):
        res = {}
        (dist1, prev1) = self.dijkstra(id1, direction = -1)
        (dist2, prev2) = self.dijkstra(id2, direction = -1)
        for id in prev1:
            if id in prev2:
                res[id] = (dist1[id], dist2[id])
        return res

    # Fonction optionnelle qui pourrait être utile
    # def ancetre_commun(self, id1, id2):
    #     res = {}
    #     (dist1, prev1) = self.dijkstra(id1, direction = -1)
    #     (dist2, prev2) = self.dijkstra(id2, direction = -1)
    #     for id in prev1:
    #         if id in prev2:
    #             res[id] = (dist1[id], dist2[id])
    #     return res