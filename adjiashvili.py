from collections import defaultdict
from math import ceil
import os
import random
import subprocess
import networkx as nx
from itertools import chain, combinations, product
import treegenerator as tg

def adjiashvili(tree,L, epsilon):
    """
    Implementation of the Adjiashvili algorithm for the Tree Augmentation Problem\n
    Approximation Factor: 5/3 + epsilon\n
    \tT: input unweighted undirected tree
    \tL: input unweighted undirected link set
    \tepsilon: approximation factor
    """
    T = tree.copy()

    # Fixed gamma (from the paper) is the number of paths in a gamma-bundle
    gamma = int(168/(epsilon**2))

    # find all distinct unions of gamma-many paths
    unions = find_distinct_unions(T, gamma)

    # bookkeeping for LP formulation. form: [(linksubset, OPT), ...]
    bundle_links_OPT = []

    # list of available links
    link_list = list(L.edges())

    # for each union, find the optimal solution for the LP formulation. this is OPT
    for union in unions:

        # find relevant links which cover at least one edge in the union
        linksubset = []

        # iterate through the links
        for i in range(len(link_list)):
            path = nx.shortest_path(T, link_list[i][0], link_list[i][1])
            steps = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            for edge in union:
                # keep track of the link indices which cover at least one edge in the union
                if edge in steps or edge[::-1] in steps:
                    linksubset.append(i)
                    break

        
        # split the union into paths by splitting on vertices of degree >= 3
        paths, nodes, leaves = split_edges_at_high_degree_vertices(union)

        # list of the links kept
        linkcopy = [link_list[i] for i in linksubset]

        # truncate the links which extend past the paths in the union
        for a,b in linkcopy.copy():
            start = a
            end = b
            if a not in nodes:
                path = nx.shortest_path(T, a, b)
                # walk towards the closest path in the correct direction
                for node in path:
                    if node not in nodes:
                        continue
                    else:
                        start = node
            if b not in nodes:
                path = nx.shortest_path(T, b, a)
                for node in path:
                    if node not in nodes:
                        continue
                    else:
                        end = node

            # if some link data changes, update it in the copy
            if start != a or end != b:
                linkcopy.remove((a,b))
                linkcopy.append((start, end))

        # partition the links into between-path and within-path links
        cross_same = partition_links(paths, linkcopy)

        # orders between-path links with form {(path i, path j): {(u, v), ...}, ...} where i < j. Inserts empty list of links if necessary
        subsets = {}

        # for each first node of inter-path links
        for outer_key, outer_value in cross_same[0].items():

            # insert empty list if inconsistency in order
            expected = outer_key + 1
            if cross_same[0][outer_key] == {}:
                for i in range(expected, len(paths)):
                    subsets[(outer_key, i)] = [[]]

            # for each second node of inter-path links
            for inner_key, items in cross_same[0][outer_key].items():

                # insert empty list if inconsistency in order
                while expected != inner_key:
                    subsets[(outer_key, expected)] = [[]]
                    expected += 1
                
                subsets[(outer_key, inner_key)] = []
                # find all subsets of size <= 2 of the inter-path links
                for i in range(3):
                    for j in combinations(items, i):
                        subsets[(outer_key, inner_key)].append(list(j))
                expected += 1
            
            # if some inner paths are missing, insert empty list of links
            if expected != len(paths) and outer_key != len(paths) - 1:
                for i in range(expected, len(paths)):
                    subsets[(outer_key, i)] = [[]]

        # for each 'guess' of optimal inter-path links
        min = float('inf')
        for combo in product(*(subsets[key] for key in list(subsets.keys()))):
            min_cand = 0

            # give each path the correct links with algebra
            for pathnum in range(len(paths)):
                linkset = set()
                addends = []
                for i in range(len(paths)-1, len(paths)-1-pathnum, -1):
                    addends.append(i)
                base = sum(addends)
                last = addends[-1] if len(addends) > 0 else len(paths)
                for i in range(0, last-1):
                    linkset.update(combo[base + i])

                counter = 0
                for i in range(len(addends)-1, -1, -1):
                    base = sum(addends[:i])
                    linkset.update(combo[base + counter])
                    counter += 1

                # with the inter-path link subset guess, discover what still needs covered
                uncovered = paths[pathnum].copy()
                for link in linkset:
                    # innode = link node on the current path
                    innode, outnode = (link[0], link[1]) if any(link[0] in t for t in paths[pathnum]) else (link[1],link[0])

                    # note the edges covered by each link
                    path = nx.shortest_path(T, innode, outnode)
                    for step in [(path[i], path[i + 1]) for i in range(len(path) - 1)]:
                        if step not in uncovered and step[::-1] not in uncovered:
                            break
                        uncovered.remove(step) if step in uncovered else uncovered.remove(step[::-1])

                # find the optimal cover for the remaining edges with within-path links
                opt_path_cover = cover(uncovered, cross_same[1][pathnum].copy()) if len(uncovered) > 0 else 0

                # if no cover is found, the guess is invalid
                if opt_path_cover == -1:
                    min_cand = float('inf')
                    break
                
                # otherwise, add the links used in the within-path cover
                min_cand += opt_path_cover
            
            # after covering each path, add the number of inter-path links used
            min_cand += sum(1 for tup in chain.from_iterable(combo) if isinstance(tup, tuple))

            # find the optimal guess
            if min_cand < min:
                min = min_cand
            
            # short-circuit for best possible solution
            if min == ceil(len(leaves)/2):
                break

        # note OPT for the corresponding links which cover the union
        bundle_links_OPT.append((linksubset, min))
    
    # formulate the LP
    edge_list = list(T.edges())
    paths = {(i, j): nx.shortest_path(T, i, j) for (i, j) in link_list}
        
    # Create the .mod file
    with open("ampl/adj.mod", 'w') as f:
        # Write set declarations
        f.write(f'set LINK_LIST = {{0..{len(link_list)-1}}};\n')
        f.write(f'set EDGE_LIST = {{0..{len(edge_list)-1}}};\n\n')
    
        f.write('param cover{EDGE_LIST, LINK_LIST} binary;\n')
        f.write('var X{LINK_LIST};\n\n')
    
        # Write objective function
        f.write('minimize LinksUsed:\n')
        f.write('\tsum{i in LINK_LIST} X[i];\n\n')
    
        # Write constraints
        f.write('subject to Constraint{i in EDGE_LIST}:\n')
        f.write('\tsum{j in LINK_LIST} cover[i,j]*X[j] >= 1;\n\n') 
        f.write('subject to Constraint2{j in LINK_LIST}:\n')
        f.write('\t X[j] >= 0;\n\n')
        for linksubset, OPT in bundle_links_OPT:
            counter = 1
            f.write(f'subject to BundleConstraint{counter}:\n')
            formatted_links = ', '.join(map(str, linksubset))  # Convert each element to string and join with commas
            f.write(f'\tsum{{j in {{{formatted_links}}}}} X[j] >= {OPT};\n')
            counter += 1

    with open("ampl/adj.dat", 'w') as f:
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
    with open("ampl/adj.run", 'w') as f:
        f.write('model adj.mod;\ndata adj.dat;\n\n')
        f.write('option solver cplex;\n\n')
        f.write('solve;\n\n')
        f.write('display {i in LINK_LIST : X[i] > 0} i > "../adjout.txt";\n')

    # Define the path to the AMPL files
    ampl_path = "ampl/"

    # List of commands to execute
    command = "./ampl adj.run"

    os.remove('adjout.txt') if os.path.exists('adjout.txt') else None

    # Execute commands one by one
    subprocess.run(command, shell=True, cwd=ampl_path)    

    # obtain fractional solution from AMPL
    support_indices = set()
    with open("adjout.txt", 'r') as f:
        for line in f.readlines()[1:-2]:
            numbers = line.split()
            for number in numbers:
                support_indices.add(link_list[int(number)])

    # obtain the links of the fractional solution
    support = [link_list[i] for i in support_indices]

    # arbitrarily designate a root node
    root = random.choice(list(T.nodes()))

    for link in support.copy():
        # find all in-links
        if root not in nx.shortest_path(T, link[0], link[1]):
            set1 = set(nx.shortest_path(T, link[0], root))
            # replace in-links with 2 shadows which are also up-links
            for node in nx.shortest_path(T, link[1], root):
                if node in set1:
                    if node == link[0] or node == link[1]:
                        break
                    support.remove(link)
                    support.append(link[0], node)
                    support.append(node, link[1])
                    break

    # final solution set I
    I = set()
    
    # rounding algorithm
    while(1):

        # if any leaf edge is covered only by up-links
        leaf_nodes = [node for node in T.nodes if T.degree(node) == 1]

        adjacent_edges = []
        for leaf_node in leaf_nodes:    
            adjacent_edges.extend((leaf_node, next(T.neighbors(leaf_node))))

        for link in support:
            if link[0] in leaf_nodes or link[1] in leaf_nodes:
                if root in nx.shortest_path(T, link[0], link[1]):
                    if link[0] in leaf_nodes:
                        leaf_nodes.remove(link[0])
                    if link[1] in leaf_nodes:
                        leaf_nodes.remove(link[1])
    
        chosen = link[0]

        # case 1: some leaf isn't covered by a cross-link
        if len(leaf_nodes) > 0:
            length = 0
            # find the longest up-link and include it in the solution
            for link in support:
                if link[0] == leaf_nodes[0] or link[1] == leaf_nodes[0]:
                    len_can = nx.shortest_path(T, link[0], link[1])
                    if len(len_can) > length:
                        length = len(len_can)
                        chosen = link
        else: # case 2: otherwise, look for a leaf-to-leaf link and choose it
            leaf_nodes = [node for node in T.nodes if T.degree(node) == 1]
            for link in support:
                if link[0] in leaf_nodes and link[1] in leaf_nodes:
                    chosen = link
                    break
            else: # otherwise ...
                break

        # contract the chosen link
        I.add(chosen)
        contract(T, chosen, support)

    # for each leaf, choose an arbitrary link to cover it
    leaf_nodes = [node for node in T.nodes if T.degree(node) == 1]
    for leaf in leaf_nodes:
        for link in support:
            if link[0] == leaf or link[1] == leaf:
                if root in nx.shortest_path(T, link[0], link[1]):
                    I.add(link)
                    support.remove(link)
                    break

    return len(I)

    # TODO: round the LP solution using the easy 3-step algo
def contract(tree, link, links):
    """
    Contract the edges covered by a given link.\n
    """
    global root_node

    toContract = []

    # determine the set of edges covered by the link
    shadow = nx.shortest_path(tree, link[0], link[1])
    #print("link", link) if not_copy and update_map else None
    # perpare each edge for contraction
    for i in range(len(shadow)-1):
        toContract.append([shadow[i],shadow[i+1]]) if [shadow[i],shadow[i+1]] not in toContract and [shadow[i+1],shadow[i]] not in toContract else None

    # contract each edge covered by the link
    while(not len(toContract) == 0):

        # update the root node if necessary
        if toContract[0][1] == root_node:
            root_node = toContract[0][0]

        # contract the first edge in the list
        nx.contracted_edge(tree,tuple(toContract[0]),self_loops=False, copy=False)

        # add the tree edge to L for the sake of contracting to see the resulting link configuration
        if links is not None and tuple(toContract[0]) not in links.edges() and tuple(toContract[0])[::-1] not in links.edges():
            links.add_edge(*tuple(toContract[0]))
        nx.contracted_edge(links,tuple(toContract[0]),self_loops=False, copy=False) if links is not None else None

        # if any other edge in our list is adjacent to the "dest" node of contraction, re-index it
        for toFix in toContract[1:]:
            if(toFix[0] == toContract[0][1]):
                toFix[0] = toContract[0][0]
            elif(toFix[1] == toContract[0][1]):
                toFix[1] = toContract[0][0]

        # remove the edge we contracted from our list, 
        toContract.remove(toContract[0])

def cover(uncovered_edges, available_links):
    """
    Finds a minimum cover of the path with available links by greedy algorithm\n
    \tuncovered_edges: list of edges to cover
    \tavailable_links: list of available links
    """
    covered_edges = []  # To store the covered edges
    current_position = 0  # Start from the leftmost end of the path
    
    while current_position < len(uncovered_edges):
        current_edge = uncovered_edges[current_position]
        left_endpoint = current_edge[0]
        max_right = current_edge[1]
        best_link = None
        
        for link in available_links:
            link_start, link_end = link
            if link_start <= left_endpoint and link_end >= max_right:
                if best_link is None or link_end > best_link[1]:
                    best_link = link
        
        if best_link is None:
            # No link found to cover the current edge
            return -1
        
        # Add the best_link to covered_edges
        covered_edges.append(best_link)
        available_links.remove(best_link)
        
        # Move to the next uncovered edge
        current_position = max_right+1

    return len(covered_edges)

def enumerate_paths(tree):
    """
    Returns a list of all possible paths between pairs of nodes in the tree\n
    \ttree: input tree
    """
    paths = []
    nodes = list(tree.nodes)

    # for each pair of nodes, return the path between them. this path is unique
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            paths.append(nx.shortest_path(tree, nodes[i], nodes[j]))

    return paths

def generate_combinations(paths, union_size):
    """
    returns a list of all possible combinations of k-many paths\n
    \tpaths: list of all paths in the tree
    \tunion_size: number of paths to combine
    """
    return list(combinations(paths, union_size))

def union_of_paths(paths_combination):
    """
    given a combination of paths, returns their union as a set of edges\n
    \tpaths_combination: a list of combination of paths
    """
    union_edges = set()
    for path in paths_combination:
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            if (u, v) not in union_edges and (v, u) not in union_edges:
                union_edges.add((u, v))

    return union_edges

def find_distinct_unions(tree, k):
    """
    returns a list of distinct unions (sets of edges) of k-many paths\n
    \ttree: input tree
    \tk: number of paths to combine
    """
    # obtain a list of all distinct paths on the tree. this is a list of nodes
    all_paths = enumerate_paths(tree)

    # generate all combinations of k-many paths. If a combination has more paths than available, use all paths
    path_combinations = generate_combinations(all_paths, k) if k < len(all_paths) else generate_combinations(all_paths, len(all_paths))
    
    # find the union of each combination of paths. this is a list of edges
    unions = [union_of_paths(comb) for comb in path_combinations]

    # find the distinct unions
    distinct_unions = set(frozenset(union) for union in unions)

    return [set(union) for union in distinct_unions]

def split_edges_at_high_degree_vertices(edges):
    """
    splits the input edges at high-degree vertices. returns a list of list of edges, all nodes in the tree, and all leaves\n
    \tedges: input edges
    """
    # keep track of vertex degrees
    degree = defaultdict(int)

    for (u, v) in edges:
        degree[u] += 1
        degree[v] += 1


    # convenient lists
    leaves = [node for node, deg in degree.items() if deg == 1]
    nodes = [node for node, deg in degree.items()]
    
    # identify nodes of degree >= 3
    high_degree_vertices = {node for node, deg in degree.items() if deg >= 3}

    # if the input tree is a disjoint union of paths, return all edges
    if high_degree_vertices == set():
        return [edges], nodes, leaves
    
    # split edges into paths. high degree vertices are duplicated.
    split_paths = []
    visited_edges = set()
    
    for v in high_degree_vertices:

        # split the graph with DFS
        stack = [(v, neighbor) for neighbor in get_neighbors(v, edges)]
        current_path = []
        
        while stack:

            # visit a vertex
            parent, current = stack.pop()
            
            if (parent, current) in visited_edges or (current, parent) in visited_edges:
                continue
            
            visited_edges.add((parent, current))
            current_path.append((parent, current))

            # reaching a high-degree vertex means the end of the current path
            
            if current in high_degree_vertices or degree[current] == 1:
                split_paths.append(current_path.copy())
                current_path.clear()
                continue
            else: # otherwise, continue DFS
                for neighbor in get_neighbors(current, edges):
                    stack.append((current, neighbor)) if neighbor != parent else None
        
        if current_path:
            split_paths.append(current_path)

    return split_paths, nodes, leaves

def get_neighbors(vertex, edges):
    """
    returns the neighbors of a vertex, given a vertex and edge set\n
    \tvertex: input vertex
    \tedges: input edge set
    """
    neighbors = []
    for u, v in edges:
        if u == vertex:
            neighbors.append(v)
        elif v == vertex:
            neighbors.append(u)
    return neighbors

def partition_links(paths, all_links):
    """
    partitions links into those between paths and those within paths\n
    Returns between-path links with form {path i: {path j: {(u, v), ...}, ...} where i < j\n
    Returns within-path links with form {path i: {(u, v), ...}, ...}\n
    \tpaths: list of paths
    \tall_links: list of all links
    """
    # Initialize between-path and within-path structures
    num_paths = len(paths)
    between_path_links = {i: {} for i in range(num_paths)} # form {path i: {path j: {(u, v), ...}, ...} where i < j
    within_path_links = {i: set() for i in range(num_paths)} # form {path i: {(u, v), ...}, ...}
    
    # Collect all vertices in each path
    path_vertices = [set() for _ in range(num_paths)]
    for i, path in enumerate(paths):
        for u, v in path:
            path_vertices[i].add(u)
            path_vertices[i].add(v)
    
    # first identity within-path links
    for i in range(num_paths):
        vertices_in_path_i = path_vertices[i]
        
        for u, v in all_links:
            if u in vertices_in_path_i and v in vertices_in_path_i:
                if u != v:  # Ensure the link is between different vertices within the same path
                    within_path_links[i].add((u, v))
                    all_links.remove((u, v))

    # then identity between-path links
    for i in range(num_paths):
        vertices_in_path_i = path_vertices[i]
        for j in range(i + 1, num_paths):
            vertices_in_path_j = path_vertices[j]
            toRemove = []
            for u, v in all_links:
                if (u in vertices_in_path_i and v in vertices_in_path_j) or (u in vertices_in_path_j and v in vertices_in_path_i):
                    if (u, v) not in between_path_links[i].get(j, set()) and (v, u) not in between_path_links[i].get(j, set()):
                        between_path_links[i][j] = between_path_links[i].get(j, set()) | {(u, v)}
                        toRemove.append((u, v))

            for link in toRemove:
                all_links.remove(link)

    return between_path_links, within_path_links

def main():
    T = tg.lobster_tree(50)
    L = tg.generate_links(T, 0.5)
    print("links", L.edges())
    adjiashvili(T, L, 0.1)

if __name__ == '__main__':
    main()