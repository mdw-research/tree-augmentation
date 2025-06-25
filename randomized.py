import networkx as nx
import matplotlib.pyplot as plt
import random
import tracemalloc
import datetime
import time
import treegenerator as tg

def randomized(T, L):
    minimumSolution = 0
    for i in range(100):
        tree = T.copy()
        links = L.copy()
        S = tree.copy()

        for u in tree.nodes():
            if S.degree(u) == 1:
                v = random.choice(list(links[u]))
                S.add_edge(u, v)
                links.remove_edge(u, v)

        while nx.has_bridges(S):
            randomEdge = random.choice(list(links.edges()))
            S.add_edge(randomEdge[0], randomEdge[1])
            links.remove_edge(randomEdge[0], randomEdge[1])

        currentSolution = S.number_of_edges() - tree.number_of_edges()

        if not minimumSolution:
            minimumSolution = currentSolution

        minimumSolution = currentSolution if currentSolution < minimumSolution else minimumSolution

    return minimumSolution


def main():
    file = open("randomized.txt", "w")
    file.write(f"{datetime.datetime.now()}\n")
    file.write(f"test, size, density, tree, edges, time, memory\n")

    sizes = [10]
    densities = [0.1, 0.5, 0.8]
    trees = ["path", "star", "starlike", "caterpillar", "lobster", "random"]
    treeFunc = [tg.path_tree, tg.star_tree, tg.starlike_tree, tg.caterpillar_tree, tg.lobster_tree, tg.random_tree]
    iterations = range(3)
    for s in sizes:
        for d in densities:
            for idx, tree in enumerate(trees):
                for i in iterations:
                    T = treeFunc[idx](s)
                    L = tg.generate_links(T, d)

                    st = time.time()
                    tracemalloc.start()
                    edges = randomized(T, L)
                    running_time = time.time() - st
                    current, mem = tracemalloc.get_traced_memory()

                    file.write(f"{i+1}, {s}, {d}, {tree}, {edges}, {running_time}, {mem}\n")

    file.close()


if __name__ == '__main__':
    main()
