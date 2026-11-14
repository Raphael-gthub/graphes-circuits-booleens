class OpenDigraphPropertiesMixin:
    def is_well_formed(self):
        """Vérifie si le graphe est bien formé."""

        for input_id in self.inputs:
            # Vérification existence du noeud
            input_node = self.get_node_by_id(input_id)
            if input_node is None:
                return False
            
            # Le noeud existe
            input_node_children = input_node.get_children()
            input_node_parents = input_node.get_parents()
            children = input_node_children.values()
            if (len(children) == 0 or len(children) > 1):
                return False
            [m] = children
            # Vérification un seul enfant de multiplicité 1 et pas de parents
            if ((m != 1) or (len(input_node_parents) != 0)):
                return False

        for output_id in self.outputs:
            # Vérification existence du noeud
            output_node = self.get_node_by_id(output_id)
            if output_node is None:
                return False

            output_node_children = output_node.get_children()
            output_node_parent = output_node.get_parents()
            parents = output_node_parent.values()
            if (len(parents) == 0 or len(parents) > 1):
                return False
            [m] = parents
            # Vérification un seul parent de multiplicité 1 et pas d'enfants
            if ((m != 1) or (len(output_node_children) != 0)):
                return False


        # Vérifier que pour chaque clé de nodes (<c, node>), c = node.id
        for c, n in self.nodes.items():
            if (c != n.get_id()):
                return False
            # vérifier que pour chaque noeud,
            # ses parents le reconnaissent bien en tant qu'enfant
            # et ses enfants le reconnaissent bien en tant que parent
            parents = n.get_parents()
            gosses = n.get_children()
            for (parent_id, m) in parents.items():
                pere = self.get_node_by_id(parent_id)
                gosses_du_pere = pere.get_children()
                if c in gosses_du_pere:
                    mPere = gosses_du_pere[c]
                    if mPere != m:
                        return False
                else:
                    return False
            for (gosse_id, m) in gosses.items():
                gosse = self.get_node_by_id(gosse_id)
                parents_du_gosse = gosse.get_parents()
                if c in parents_du_gosse:
                    mGosse = parents_du_gosse[c]
                    if mGosse != m:
                        return False
                else:
                    return False

        # Tout est bon si on arrive ici
        return True


    def assert_is_well_formed(self):
        """Lève une exception si le graphe est mal formé."""
        if not self.is_well_formed():
            raise Exception("Graphe pas bien formé")
        
    def is_oriented(self):
        # Pour chaque noeud on s'assure
        # qu'il n'est l'enfant d'aucun de ses enfants
        for n in self.get_nodes():
            children_list = n.get_children()
            for id_child_node in children_list.keys():
                if n in (
                    self.get_node_by_id(id_child_node).get_children().values()
                ):
                    return False
        return True

    def is_cyclic(self):
        g_noeud = self.get_nodes()
        if len(g_noeud) == 0:
            return False  # si pas de noeud, acyclique
        else:
            for node in g_noeud:
                if node.outdegree() == 0:
                    # Pour ne pas modifier le graphe,
                    # on travaille sur une copie
                    g_copy = self.copy()
                    g_copy.remove_node_by_id(node.get_id())
                    return g_copy.is_cyclic()
        return True  # si pas de feuille, cyclique

    def is_symetric(self):
        for n in self.get_nodes():
            parents_list = n.get_parents()
            children_list = n.get_children()
            # Chaque noeud doit avoir le même nombre de parent et d'enfant
            if len(parents_list) != len(children_list):
                return False
            # La multiplicité doit être la même
            for id in parents_list.keys():
                if parents_list[id] != children_list[id]:
                    return False
        return True