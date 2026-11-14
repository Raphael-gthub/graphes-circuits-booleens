import sys
import os
import re  # pour RegEx dans from_dot_file
import webbrowser  # pour display
import urllib.parse  # pour display

class OpenDigraphDisplaysMixin:
    def save_as_dot_file(self, path, verbose=False, name="G"):
        """
        Crée un fichier .dot à partir d'un graphe
        """
        with open(path, 'w') as dot_file:
            dot_file.write(f"digraph {name} {{\n")

            # Écriture des nœuds
            for id, node in self.get_id_node_map().items():
                label = node.get_label() if node.get_label() else str(id)
                if verbose:
                    label = f"{label} ({id})"  # Afficher l'ID en plus du label

                attributes = [f'label="{label}"', 'shape=ellipse',
                              'style=filled', 'color="grey"']
                if id in self.get_input_ids():
                    attributes.append('color="#E2E9C0"')  # Entrées en vert
                if id in self.get_output_ids():
                    attributes.append('color="#CE6A6B"')  # Sorties en rouge

                dot_file.write(f"\t{id} [{', '.join(attributes)}];\n")

            # Écriture des arêtes
            for id, node in self.get_id_node_map().items():
                for child_id in node.get_children():
                    dot_file.write(f"\t{id} -> {child_id};\n")

            dot_file.write("}\n")

        return None

    @classmethod
    def from_dot_file(cls, path):
        """
        Charge un graphe à partir d'un fichier .dot
        """
        nodes = {}  # Dict tmp {id: (label, is_input, is_output)}
        edges = []  # Liste des arêtes (parent, enfant)
        input_ids = []
        output_ids = []

        with open(path, "r") as dot_file:
            for line in dot_file:
                line = line.strip()

                # Ignore les lignes de début et fin
                if line.startswith("digraph") or line == "}":
                    continue

                # Détection des nœuds avec attributs
                node_match = re.match(r'(\d+)\s+\[(.+)\];', line)
                if node_match:
                    node_id = int(node_match.group(1))
                    attributes = node_match.group(2).split(",")

                    label = None
                    is_input = False
                    is_output = False

                    for attr in attributes:
                        key, value = attr.strip().split("=")
                        value = value.strip('"')  # Enlève les guillemets

                        if key == "label":
                            label = value
                        elif key == "input" and value.lower() == "true":
                            is_input = True
                        elif key == "output" and value.lower() == "true":
                            is_output = True

                    nodes[node_id] = (label, is_input, is_output)
                    if is_input:
                        input_ids.append(node_id)
                    if is_output:
                        output_ids.append(node_id)

                    continue  # Passe à la ligne suivante

                # Détection des arêtes
                edge_match = re.match(r'(\d+)\s*->\s*(\d+);', line)
                if edge_match:
                    parent = int(edge_match.group(1))
                    child = int(edge_match.group(2))
                    edges.append((parent, child))

        # Création des objets node
        node_objects = [cls.node(nid, label, {}, {})
                        for nid, (label, _, _) in nodes.items()]

        # Ajout des enfants et parents
        node_dict = {n.id: n for n in node_objects}  # Accès rapide aux nœuds
        for parent, child in edges:
            node_dict[parent].children[child] = 1
            node_dict[child].parents[parent] = 1

        # Création du graphe final
        g = cls(input_ids, output_ids, node_objects)
        return g

    def display(self, dot_path, verbose=False, method="local"):
        """
        Affiche le graphe en générant un fichier .dot spécifié
        et en le convertissant en image.

        dot_path : chemin vers le fichier .dot.
        méthodes :
            - "local" : Affiche en local (Graphviz + visionneuse d'image)
            - "web" : Ouvre le graphe dans un visualiseur en ligne

        Si la variable d'environnement GRAPHES_SANS_AFFICHAGE est définie, les fichiers
        sont générés mais aucune fenêtre n'est ouverte (utile pour lancer les tests).
        """
        sans_affichage = bool(os.environ.get("GRAPHES_SANS_AFFICHAGE"))

        if method == "local":
            self.save_as_dot_file(dot_path, verbose)

            img_path = dot_path.replace(".dot", ".png")

            # Convertir en image avec Graphviz
            os.system(f"dot -Tpng {dot_path} -o {img_path}")

            if sans_affichage:
                return

            # Ouvrir l'image (multi-OS)
            if sys.platform == "darwin":  # macOS
                os.system(f"open {img_path}")
            elif sys.platform == "linux":  # Linux
                os.system(f"xdg-open {img_path}")
            elif sys.platform == "win32":  # Windows
                os.system(f"start {img_path}")
            else:
                print(f"Fichier généré : {img_path} (ouvrez-le manuellement)")

        elif method == "web":
            if sans_affichage:
                return
            dot_code = self.generate_dot_string(verbose)
            url_encoded_dot = urllib.parse.quote(dot_code)
            webbrowser.open(
                f"https://dreampuf.github.io/GraphvizOnline/#{url_encoded_dot}"
                )

    def generate_dot_string(self, verbose=False):
        """ Génère une représentation texte du graphe au format DOT. """
        dot_lines = ["digraph G {"]

        for node_id, node_obj in self.nodes.items():
            label = getattr(node_obj, "label", None)
            node_type = getattr(node_obj, "type", None)

            attributes = []

            if verbose:
                attributes.append(f'label="{label} ({node_id})"' if label else f'label="{node_id}"')
            else:
                attributes.append(f'label="{label}"' if label else f'label="{node_id}"')

            if node_type:
                attributes.append(f'type="{node_type}"')

            dot_lines.append(f'    {node_id} [{" ".join(attributes)}];')

        # Générer les arêtes à partir des enfants
        for parent_id, parent_node in self.nodes.items():
            for child_id, weight in parent_node.children.items():
                edge_label = f' [label="{weight}"]' if verbose and weight != 1 else ""
                dot_lines.append(f'    {parent_id} -> {child_id}{edge_label};')

        dot_lines.append("}")
        return "\n".join(dot_lines)