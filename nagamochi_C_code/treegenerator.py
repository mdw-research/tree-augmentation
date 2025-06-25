import networkx as nx
import matplotlib.pyplot as plt
import random

def path_tree(n):
    return nx.path_graph(n)

def star_tree(n):
    return nx.star_graph(n-1)

def starlike_tree(n):
    branchingFactor = random.random()
    G = nx.Graph()
    for node in range(1, n):
        if (random.random() < branchingFactor):
            G.add_edge(0, node)
        else:
            G.add_edge(node - 1, node)
    return G

def caterpillar_tree(n):
    spine = range(0, random.randrange(1, n - 2))
    legs = range(len(spine), n)
    G = path_tree(spine)
    for node in legs:
        G.add_edge(random.choice(spine), node)
    return G

def lobster_tree(n):
    l1 = random.randrange(1, n - 3)
    l2 = random.randrange(1, (n - 2) - l1)
    spine = range(0, n - l1 - l2)
    legs1 = range(n - l1 - l2, n - l2)
    legs2 = range(n - l2, n)
    G = path_tree(spine)
    for node in legs1:
        G.add_edge(random.choice(spine), node)
    for node in legs2:
        G.add_edge(random.choice(legs1), node)
    return G

def random_tree(n):
    return nx.random_labeled_tree(n)

def generate_links(T, density):
    L = nx.Graph()
    for u in T:
        for v in T:
            if (u != v and random.random() < density):
                L.add_edge(u, v)

    while (not nx.is_k_edge_connected(nx.compose(T, L), 2)):
        u = random.choice(list(T))
        v = random.choice(list(T))
        if (u != v):    
            L.add_edge(u, v)

    L.remove_edges_from(T.edges)

    return L
