import networkx as nx
import matplotlib.pyplot as plt
import random
import pandas as pd
import streamlit as st

# Fonction pour générer le graphe
def generate_graph(num_subjects):
    subjects = [chr(i) for i in range(65, 65 + num_subjects)]  # Générer A, B, C, ...
    G = nx.Graph()

    # Ajouter des nœuds et des arêtes
    G.add_nodes_from(subjects)
    for i in range(1, num_subjects):
        G.add_edge(subjects[i-1], subjects[i])  # Ajouter des arêtes entre nœuds consécutifs
    
    # Ajouter des arêtes supplémentaires aléatoires
    num_extra_edges = random.randint(num_subjects, num_subjects * 2)
    while len(G.edges) < num_extra_edges:
        sub1, sub2 = random.sample(subjects, 2)
        if not G.has_edge(sub1, sub2):
            G.add_edge(sub1, sub2)

    # Vérifier si le graphe est connexe
    assert nx.is_connected(G), "Le graphe n'est pas connexe !"

    return G

# Fonction pour dessiner le graphe
def draw_graph(G, pos_spread, title="Graph", color_map=None):
    plt.figure(figsize=(10, 10))

    if color_map is None:
        # Dessiner le graphe normal
        nx.draw(
            G,
            pos=pos_spread,
            with_labels=True,
            node_size=800,
            font_size=10,
            node_color="skyblue",
            edge_color="gray",
            alpha=0.8  # Transparence des nœuds
        )
    else:
        # Dessiner le graphe coloré
        node_colors = [color_map.get(node, "skyblue") for node in G.nodes]
        nx.draw(
            G,
            pos=pos_spread,
            with_labels=True,
            node_size=800,
            font_size=10,
            node_color=node_colors,
            edge_color="gray",
            alpha=0.8  # Transparence des nœuds
        )

    plt.title(title, fontsize=14)
    st.pyplot(plt)

# Fonction pour colorier le graphe
def color_graph(G):
    # Appliquer la coloration gloutonne
    color_map = nx.coloring.greedy_color(G, strategy="largest_first")

    # Palette de couleurs
    color_palette = [
        "#FF6666", "#66B3FF", "#99FF99", "#FFD966", "#FF99CC",
        "#B3B3B3", "#FFB366", "#A366FF", "#66FFCC", "#FFCC66"
    ]
    node_colors = {node: color_palette[color_map[node]] for node in G.nodes}
    
    # Créer les groupes
    groups = {}
    for node, color_index in color_map.items():
        groups.setdefault(color_index + 1, []).append(node)
    
    return node_colors, groups

# Streamlit UI
st.title("Graph Planification et Algorithme de Coloration")

# Sidebar pour la navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choisissez une section:", ("Graphique", "Algorithme Glouton", "Coloration"))

    # Choisir le nombre de sommets pour générer le graphe
    num_vertices = st.number_input("Nombre de sommets", min_value=1, max_value=100, value=20, step=1)

# Initialisation des variables de session
if 'G' not in st.session_state:
    st.session_state.G = None
if 'pos_spread' not in st.session_state:
    st.session_state.pos_spread = None
if 'colored_graph' not in st.session_state:
    st.session_state.colored_graph = None
if 'groups' not in st.session_state:
    st.session_state.groups = None

# Afficher le contenu selon la section choisie
if page == "Graphique":
    # Bouton pour générer et afficher le graphe normal
    if st.button("Générer le Graphe Normal"):
        # Générer le graphe avec le nombre de sommets choisi
        G = generate_graph(num_vertices)
        st.session_state.G = G  # Stocker le graphe en session

        # Générer les positions des nœuds
        pos_spread = nx.spring_layout(G, k=0.5)  # Facteur d'espacement
        st.session_state.pos_spread = pos_spread  # Stocker les positions

        # Dessiner le graphe normal
        st.write("Graph Normal:")
        draw_graph(G, pos_spread, title="Planification des Examens (Graph Connexe)")

    # Bouton pour générer et afficher le graphe coloré
    if st.button("Générer le Graphe Coloré") and st.session_state.G is not None:
        # Obtenir le graphe coloré et les groupes
        colored_graph, groups = color_graph(st.session_state.G)
        st.session_state.colored_graph = colored_graph  # Stocker les couleurs
        st.session_state.groups = groups  # Stocker les groupes

        # Afficher les groupes
        st.write("Groupes :")
        for group, nodes in groups.items():
            st.write(f"Groupe {group} : {', '.join(nodes)}")

        # Afficher un tableau des groupes
        df_groups = pd.DataFrame.from_dict(groups, orient="index").transpose()
        st.write("Tableau des Groupes :")
        st.dataframe(df_groups)

        # Afficher un graphique des groupes
        group_sizes = {f"Groupe {k}": len(v) for k, v in groups.items()}
        plt.figure(figsize=(8, 6))
        plt.bar(group_sizes.keys(), group_sizes.values(), color="#66B3FF", alpha=0.8)
        plt.title("Nombre de Sommets par Groupe", fontsize=14)
        plt.ylabel("Nombre de Sommets")
        plt.xlabel("Groupes")
        st.pyplot(plt)

        # Dessiner le graphe coloré
        st.write("Graph Coloré:")
        draw_graph(st.session_state.G, st.session_state.pos_spread, title="Planification des Examens (Graph Coloré)", color_map=colored_graph)

    # Bouton pour effacer les graphes
    if st.button("Effacer les Graphes"):
        if 'G' in st.session_state:
            del st.session_state.G
            del st.session_state.pos_spread
            del st.session_state.colored_graph
            del st.session_state.groups
            st.write("Graphes effacés.")
        else:
            st.write("Aucun graphe à effacer.")

elif page == "Algorithme Glouton":
    st.subheader("Algorithme Glouton pour la Planification")
    st.write("""L'algorithme glouton pour la planification des examens consiste à affecter les ressources (par exemple, les salles d'examen) aux examens de manière successive, en choisissant à chaque étape l'option la plus favorable selon certains critères. Cet algorithme est utilisé pour résoudre des problèmes d'optimisation, en particulier lorsqu'il est difficile d'obtenir une solution optimale exacte, mais où une solution approximative est acceptable.""")

elif page == "Coloration":
    st.subheader("Coloration des Graphes pour la Planification")
    st.write("""La coloration des graphes est une technique utilisée pour résoudre des problèmes de planification, où l'on cherche à attribuer des couleurs aux nœuds d'un graphe de manière à ce que deux nœuds adjacents n'aient pas la même couleur. Dans le cadre de la planification des examens, cela permet de s'assurer qu'aucun examen ne soit planifié à deux endroits ou à deux horaires conflictuels.""")
