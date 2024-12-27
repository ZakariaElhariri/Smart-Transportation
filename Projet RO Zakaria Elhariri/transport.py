import networkx as nx
import matplotlib.pyplot as plt
import random
import pandas as pd
import streamlit as st

# Fonction pour générer le graphe des lignes de transport
def generate_transport_graph(num_lines, num_stops):
    # Générer des noms de lignes sous forme de L1, L2, L3, ...
    lines = [f"L{i+1}" for i in range(num_lines)]

    G = nx.Graph()

    # Ajouter des nœuds pour chaque ligne
    G.add_nodes_from(lines)
    
    # Ajouter des arêtes pour représenter les arrêts partagés
    for i in range(num_lines):
        for j in range(i+1, num_lines):
            # Créer une arête si deux lignes partagent un arrêt
            if random.random() < 0.5:  # Probabilité que deux lignes partagent un arrêt
                G.add_edge(lines[i], lines[j])

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

# Fonction pour colorier le graphe des lignes de transport
def color_transport_graph(G):
    # Appliquer la coloration gloutonne
    color_map = nx.coloring.greedy_color(G, strategy="largest_first")

    # Palette de couleurs pour les créneaux horaires
    color_palette = [
        "#FF6666", "#66B3FF", "#99FF99", "#FFD966", "#FF99CC",
        "#B3B3B3", "#FFB366", "#A366FF", "#66FFCC", "#FFCC66"
    ]
    node_colors = {node: color_palette[color_map[node]] for node in G.nodes}
    
    # Créer les groupes de lignes par créneau horaire
    groups = {}
    for node, color_index in color_map.items():
        groups.setdefault(color_index + 1, []).append(node)
    
    return node_colors, groups

# Streamlit UI
st.title("Optimisation des Horaires de Transport Public")

# Sidebar pour la navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choisissez une section:", ("Graphique", "Algorithme Glouton", "Coloration"))

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
    # Champ pour choisir le nombre de lignes et d'arrêts
    num_lines = st.slider("Choisissez le nombre de lignes de transport (2-50):", min_value=2, max_value=50, value=10)
    num_stops = st.slider("Choisissez le nombre d'arrêts (2-50):", min_value=2, max_value=50, value=10)

    # Bouton pour générer et afficher le graphe des lignes de transport
    if st.button("Générer le Graphe des Lignes de Transport"):
        # Générer le graphe des lignes
        G = generate_transport_graph(num_lines, num_stops)
        st.session_state.G = G  # Stocker le graphe en session

        # Générer les positions des nœuds
        pos_spread = nx.spring_layout(G, k=0.5)  # Facteur d'espacement
        st.session_state.pos_spread = pos_spread  # Stocker les positions

        # Dessiner le graphe normal
        st.write("Graph des Lignes de Transport :")
        draw_graph(G, pos_spread, title="Optimisation des Horaires de Transport")

    # Bouton pour générer et afficher le graphe coloré
    if st.button("Générer le Graphe Coloré") and st.session_state.G is not None:
        # Obtenir le graphe coloré et les groupes
        colored_graph, groups = color_transport_graph(st.session_state.G)
        st.session_state.colored_graph = colored_graph  # Stocker les couleurs
        st.session_state.groups = groups  # Stocker les groupes

        # Afficher les groupes de créneaux horaires
        st.write("Groupes de Créneaux Horaires :")
        for group, nodes in groups.items():
            st.write(f"Groupe {group} (Créneau Horaires): {', '.join(nodes)}")

        # Afficher un tableau des groupes
        df_groups = pd.DataFrame.from_dict(groups, orient="index").transpose()
        st.write("Tableau des Groupes de Créneaux :")
        st.dataframe(df_groups)

        # Afficher un graphique des groupes
        group_sizes = {f"Groupe {k}": len(v) for k, v in groups.items()}
        plt.figure(figsize=(8, 6))
        plt.bar(group_sizes.keys(), group_sizes.values(), color="#66B3FF", alpha=0.8)
        plt.title("Nombre de Lignes par Créneau Horaire", fontsize=14)
        plt.ylabel("Nombre de Lignes")
        plt.xlabel("Créneaux Horaires")
        st.pyplot(plt)

        # Dessiner le graphe coloré
        st.write("Graph Coloré des Lignes de Transport :")
        draw_graph(st.session_state.G, st.session_state.pos_spread, title="Optimisation des Horaires de Transport (Graph Coloré)", color_map=colored_graph)

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
    st.subheader("Algorithme Glouton pour l'Optimisation des Horaires")
    st.write("""L'algorithme glouton pour l'optimisation des horaires des transports consiste à attribuer des créneaux horaires aux lignes de transport, en choisissant à chaque étape le créneau horaire le plus favorable, en veillant à minimiser les conflits et à réduire les temps d'attente pour les passagers.""")

elif page == "Coloration":
    st.subheader("Coloration des Graphes pour l'Optimisation des Horaires")
    st.write("""La coloration des graphes permet d'attribuer des couleurs (créneaux horaires) aux lignes de transport de manière à ce que les lignes qui partagent les mêmes arrêts n'aient pas la même couleur, évitant ainsi les conflits d'horaires.""")

