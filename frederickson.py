import sys
import networkx as nx
import random
import time

def frederickson(T, L):
    """
    This function runs the Frederickson Bridge-Connecting Algorithm on a given Tree and Link Set

    """

    S = T.copy()

    # randomly choose a leaf to be the root node
    r = random.choice([r for r in T.nodes() if T.degree(r) == 1])

    diT = nx.reverse(nx.bfs_tree(T, r))

    # build a directed graph
    A = nx.DiGraph()

    # doubly orient the links with weight 1
    for (u, v) in L.edges():
        A.add_edge(u, v, weight=1)
        A.add_edge(v, u, weight=1)

    # tree edges directed towards the root are given weight 0, otherwise infty
    for (u, v) in diT.edges():
        A.add_edge(u, v, weight=0)
        A.add_edge(v, u, weight=A.number_of_nodes() + 1)

    # remove edges incoming to the root
    for u in A.nodes():
        if A.has_edge(u, r):
            A.remove_edge(u, r)

    # find a minimum spanning arborecence with Edmonds' algorithm
    Arb = edmonds(A, r, A.copy(), [])

    # append the edges of the minimum spanning arborecence to the tree
    for (u, v) in Arb.edges():
        S.add_edge(u, v)

    return len(S.edges) - len(T.edges)

def edmonds(digraph, root, original, cycles):
    """
    Finds a minimum spanning arborescence using Edmonds' algorithm quickly.

    digraph: directed graph to find the arborescence on
    root: the root node of the tree & arborescence
    original: the digraph (implementation is recursive)
    cycles: cumulative list to keep track of cycles found (initially empyty)
    """
   
   # Store the incoming edge with minimum weight for each node
    min_in_edges = {}
    for node in digraph.nodes():
        if node == root:
            continue
        min_in_edge = min(digraph.in_edges(node, data=True), key=lambda x: x[2]['weight'])
        min_in_edges[node] = min_in_edge

    # Find a cycle using the created dictionary of min in-edge weights
    cycle_nodes = []
    cycle_node = None
    for node, (source, _, _) in min_in_edges.items():
        # root node has no incoming edge
        if node == root:
            continue

        visited = [node]
        while True:
            node = source
            if node == root:
                break
            if node in visited:
                cycle_node = node
                break
            visited.append(node)

            # try to follow the chain
            source, _, _ = min_in_edges[node]

        if cycle_node is not None:
            # if we found a cycle, move to the next step
            cycle_nodes = visited[visited.index(node):]
            break
    else:
        # If no cycle is found, return the path created by the minimum in-edges
        min_arborescence = nx.DiGraph()
        min_arborescence.add_nodes_from(digraph.nodes())
        for node, (source, _, data) in min_in_edges.items():
            min_arborescence.add_edge(source, node, **data)
        return min_arborescence
    
    # CONTRACT THE CYCLE
    toContract = []

    # build a path to contract
    for i in range(len(cycle_nodes)-1):
        toContract.append([cycle_nodes[i],cycle_nodes[i+1]]) if [cycle_nodes[i],cycle_nodes[i+1]] not in toContract and [cycle_nodes[i+1],cycle_nodes[i]] not in toContract else None

    # we need to keep track of edges incident to the set we contract to build the arborescence back up from base case

    # all of the successors of the set
    common_to = set()

    # all of the predecessors of the set
    common_from = set()

    for c in cycle_nodes:
        common_to = common_to.union(set(digraph.successors(c)))
        common_from = common_from.union(set(digraph.predecessors(c)))

    # maps to keep track of which specific node is incident to which successor/predecessor. Many to one mapping ties broken by min weight
    # FORM: {cycle_node: list of successors/predecessors}

    # for successors of the set
    outcidence = {}

    # for predecessors of the set
    incidence = {}

    for node in common_to:
        if node not in cycle_nodes:
            # find minimum weight edge from cycle to successor
            minimum = int(sys.maxsize)
            winningC = None
            for c in cycle_nodes:
                if node in digraph.successors(c) and digraph[c][node]['weight'] < minimum:
                    minimum = digraph[c][node]['weight']
                    winningC = c

            # the winning pair of cycle node and successor node
            outcidence[winningC] = [node] if winningC not in outcidence else outcidence[winningC] + [node]

            # reassign the pair. After contracting, only cycle_nodes[0] will remain from the cycle
            digraph.add_edge(cycle_nodes[0], node, weight=minimum)


    for node in common_from:
        if node not in cycle_nodes:
            # find the minimum weight pair from predecessor to cycle
            minimum = int(sys.maxsize)
            winningC = None
            for c in cycle_nodes:
                if node in digraph.predecessors(c) and digraph[node][c]['weight'] - digraph[cycle_nodes[(cycle_nodes.index(c) + 1) % len(cycle_nodes)]][c]['weight'] < minimum:
                    minimum = digraph[node][c]['weight'] - digraph[cycle_nodes[(cycle_nodes.index(c) + 1) % len(cycle_nodes)]][c]['weight'] 
                    winningC = c

            # the winning pair if cycle node and predecessor node
            incidence[winningC] = [node] if winningC not in incidence else incidence[winningC] + [node]

            # reassign the pair. After contracting, only cycle_nodes[0] will remain from the cycle
            digraph.add_edge(node, cycle_nodes[0], weight=minimum)

    # contract the cycle
    while(not len(toContract) == 0):

        # contract the first edge in the list
        nx.contracted_edge(digraph,tuple(toContract[0]),self_loops=False, copy=False)

        # if any other edge in our list is adjacent to the "dest" node of contraction, re-index it
        for toFix in toContract[1:]:
            if(toFix[0] == toContract[0][1]):
                toFix[0] = toContract[0][0]
            elif(toFix[1] == toContract[0][1]):
                toFix[1] = toContract[0][0]

        toContract.remove(toContract[0])

    # log the contracted cycle for use later
    cycles.append(cycle_nodes)

    # recurse to identify more cycles. Arb is the minimum spanning arborescence on our contracted graph
    arb = edmonds(digraph, root, original, cycles)

    # NOW we need to build up the arborescence using the contracted cycle

    # landing node = actual cycle node which needs connecting to the arborescence. this is a unique cycle node
    landing = None
    for node in cycles[-1]:
        if len(list(arb.predecessors(cycles[-1][0]))) != 0:
            # can we find an arborescence node which is the predecessor of some cycle node? (always true)
            pred = next(arb.predecessors(cycles[-1][0]))
            if node in incidence and pred in incidence[node]:
                landing = node

                # if the actual cycle node was contracted & renamed, undo it
                if (pred, landing) not in arb.edges():
                    arb.remove_edge(pred, cycles[-1][0])
                    arb.add_edge(pred, landing)
                break

    # correcting the contracted and renamed successors of the cycle node on the arborescence
    substitution = {}
    for succ in arb.successors(cycles[-1][0]):
        for pre in outcidence:
            # if there is a disconnect between the successors of arborescence and cycle representative, log it to correct in a map
            # FORM: {(cycle_representative_node, successor): [(predecessor, successor)]}
            if succ in outcidence[pre] and pre != cycles[-1][0]:
                substitution[(cycles[-1][0], succ)] = [(pre, succ)] if (cycles[-1][0], succ) not in substitution else substitution[(cycles[-1][0], succ)] + [(pre, succ)]

    # fix the logged edges
    for bad in substitution:
        arb.remove_edge(*bad)
        for good in substitution[bad]:
            arb.add_edge(*good)
    
    # add the rest of the cycle to the arborescence

    # remove the landing node's connection to predecessor, but add every other directed cycle edge
    for toAdd in iterate_wrap_around(cycles[-1], cycles[-1].index(landing)):
        src = cycles[-1][(cycles[-1].index(toAdd) + 1) % len(cycles[-1])]
        arb.add_edge(src, toAdd)

    # remove the cycle from the list of cycles
    cycles.remove(cycles[-1])

    return arb

def iterate_wrap_around(lst, start_index):
    """
    Helper function to iterate over a list in a circular fashion
    """
    n = len(lst)
    current_index = (start_index + 1) % n
    stop_index = start_index % n
    while current_index != stop_index:
        yield lst[current_index]
        current_index = (current_index + 1) % n

def main():
    # T = tg.random_tree(10)
    # L = tg.generate_links(T, 0.1)
    T = nx.Graph()
    T.add_edges_from([(7,2),(2,4),(4,1),(1,9),(9,6),(6,0),(1,8),(8,3),(8,5)])
    L = nx.Graph()  
    L.add_edges_from([(0, 1), (0, 2), (8, 7), (3,5)]  )
    
    st = time.time()
    linksAdded = frederickson(T, L)
    et = time.time()
    print("Frederickson:")
    print(f"Links Added: {linksAdded}, Time: {et-st}")


if __name__ == '__main__':
    main()
