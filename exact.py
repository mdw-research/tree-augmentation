import subprocess
import networkx as nx
import time
import datetime
import tracemalloc
import treegenerator as tg
import os

def cutlp(T, L):
    tree = T.copy()
    links = L.copy()
    link_list = list(links.edges)
    edge_list = list(tree.edges)
    paths = {(i, j): nx.shortest_path(tree, i, j) for (i, j) in link_list}
    cover = {(i, j): [(u, v) for (u, v) in link_list if i in paths[(u, v)] and j in paths[(u, v)]] for (i, j) in edge_list}

    # Create the .mod file
    with open("ampl/cut.mod", 'w') as f:
        # Write set declarations
        f.write(f'set LINK_LIST = {{0..{len(link_list)-1}}};\n')
        f.write(f'set EDGE_LIST = {{0..{len(edge_list)-1}}};\n\n')
    
        f.write('param cover{EDGE_LIST, LINK_LIST} binary;\n')
        f.write('var X{LINK_LIST} binary;\n\n')
    
        # Write objective function
        f.write('minimize LinksUsed:\n')
        f.write('\tsum{i in LINK_LIST} X[i];\n\n')
    
        # Write constraints
        f.write('subject to Constraint{i in EDGE_LIST}:\n')
        f.write('\tsum{j in LINK_LIST} cover[i,j]*X[j] >= 1;\n') 

    with open("ampl/cut.dat", 'w') as f:
        # Write param cover
        f.write('param cover :=\n')
        for i in range(len(edge_list)):
            f.write(f'[{i},*] ')
            for j in range(len(link_list)):
                if edge_list[i][0] in paths[link_list[j]] and edge_list[i][1] in paths[link_list[j]]:
                    f.write(f'{j} 1  ')
                else:
                    f.write(f'{j} 0  ')
            f.write('\n')
        f.write(';\n\n')

        # Write param X
        f.write('param X :=\n')
        for i in range(len(link_list)):
            f.write(f'{i} 0\n')
        f.write(';\n')

    # Create the .run file
    with open("ampl/cut.run", 'w') as f:
        f.write('model cut.mod;\ndata cut.dat;\n\n')
        f.write('option solver cplex;\n\n')
        f.write('solve;\n\n')
        f.write('display {i in LINK_LIST: X[i] == 1} i > ../amplout.txt;\n')

    # Define the path to the AMPL files
    ampl_path = "ampl/"

    # List of commands to execute
    command = "./ampl cut.run"

    os.remove('amplout.txt') if os.path.exists('amplout.txt') else None
    st = time.time()
    tracemalloc.start()

    # Execute commands one by one
    subprocess.run(command, shell=True, cwd=ampl_path)    

    solution = set()
    with open("amplout.txt", 'r') as f:
        for line in f.readlines()[1:-2]:
            numbers = line.split()
            for number in numbers:
                solution.add(link_list[int(number)])

    current, exactMem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    exactTime = time.time()-st
    return len(solution), exactMem, exactTime    

def main():
    file = open("exact.txt", "w")
    file.write(f"{datetime.datetime.now()}\n")
    file.write(f"test, size, density, tree, edges, time, memory\n")

    sizes = [100]
    densities = [0.1, 0.5, 0.8]
    #trees = ["path", "star", "starlike", "caterpillar", "lobster", "random"]
    trees = ["star"]
    #treeFunc = [tg.path_tree, tg.star_tree, tg.starlike_tree, tg.caterpillar_tree, tg.lobster_tree, tg.random_tree]
    treeFunc = [tg.star_tree]
    iterations = range(3)
    for s in sizes:
        for d in densities:
            for idx, tree in enumerate(trees):
                for i in iterations:
                    T = treeFunc[idx](s)
                    L = tg.generate_links(T, d)
                    print("LEAVES", [node for node, degree in T.degree() if degree == 1])
                    st = time.time()
                    tracemalloc.start()
                    exact_edges = cutlp(T, L)
                    exact_time = time.time() - st
                    current, exact_mem = tracemalloc.get_traced_memory()

                    file.write(f"{i+1}, {s}, {d}, {tree}, {exact_edges}, {exact_time}, {exact_mem}\n")
    file.close()


if __name__ == "__main__":
    main()
