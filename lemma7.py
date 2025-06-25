import math
import graph
import networkx as nx
import nagamochi as n

MIN_EDGES = math.inf
LEMMA_EDGES = []

def trimLowestEdges(T, G, r, leaves):
    originalRoot = T.root

    for lf in leaves:
        z = lf
        T.root = z
        zIncident = None

        neighborList = [n for n in nx.all_neighbors(G.graphObj, z)]
        for e in neighborList:
            zIncident.append(G.vertices[e])

        for u in zIncident:
            uu = u
            des = graph.descendants(T, uu)

            while uu in des:
                des.remove(uu)

            for i in zIncident:
                if i in des:
                    if (uu, z) in G.graphObj.edges():
                        G.graphObj.remove_edge(uu, z)
                    elif (z, uu) in G.graphObj.edges():
                        G.graphObj.remove_edge(z, uu)
    
    T.root = originalRoot




def lemma7Helper(T, G_prev, r, approx, rDepth, curEdges):

    global MIN_EDGES
    global LEMMA_EDGES

    # Make copy so that doing the reduction doesn't affect the graph from the previous call
    G = graph.MyGraph()
    G.normalCopy(G_prev)

    cases = True
    while cases:
        cases = False
        # Execute P1 and P2 respectively
        while n.case1(T, G) == True:
            cases = True
        while n.case2(T, G) == True:
            cases = True

    # Add retained list to curEdges
    for e in G.retain:
        curEdges.append((e, rDepth))

    l = (4 / approx) - 1
    r = G.vertices[r]
    curSize = len(curEdges)

    leafs = graph.leaves(T, r)
    nLeaves = len(leafs)

    # Check if the original tree is covered
    neighborList = [n for n in nx.all_neighbors(G.graphObj, leafs[0])]
    if leafs[0] == r or len(neighborList) == 0:
        # If best so far
        if curSize < MIN_EDGES:
            MIN_EDGES = curSize

            if len(LEMMA_EDGES) > 0:
                # Clear the old list
                LEMMA_EDGES.clear()
            LEMMA_EDGES = list(curEdges)
            return
        return
    
    trimLowestEdges(T, G, r, leafs)

    lfArr = [None for x in range(nLeaves)]
    
    # ek will be a list of lists
    ek = [None for x in range(nLeaves)]

    # Initialize each edge
    for i in range(nLeaves):
        if i < len(leafs):
            ll = leafs[i]
            lfArr[i] = ll
            ek[i] = [n for n in nx.all_neighbors(G.graphObj, ll)]
        else:
            break

    # Function to advance an edge
    combinationNumber = 1

    # Recurse on combination after merging edges
    for i in range(l * l):
        # Merge, recurse, then umerge
        if rDepth == 0:
            combinationNumber += 1

        Gnew = graph.MyGraph()
        Gnew.normalCopy(G)

        Tnew = graph.MyGraph()
        Tnew.normalCopy(T)
        
        newEdges = list(curEdges)

        # Merge all paths
        for e in ek:

            if len(e) == 0:
                continue

            
            u = Gnew.vertices[e[0][0]]
            v = Gnew.vertices[e[0][1]]

            if u == v:
                continue

            # Put each edge on new pair with recur depth and pass to new function
            newEdges.append((e, rDepth))

            # Retain the edge (cur, triv), then contract (cur, triv) in both T and G
            graph.retainMergeTrim(Tnew, Gnew, u, v)

            """
            Tnew.vertices[v] = u
            Gnew.vertices[v] = u

            # Delete the edge in Gnew
            if (u, v) in Gnew.graphObj.edges():
                Gnew.retain.append((u, v))
                Tnew.retain.append((u, v))
                Gnew.graphObj.remove_edge(u, v)
            elif (v, u) in Gnew.graphObj.edges():
                Gnew.retain.append((v, u))
                Tnew.retain.append((v, u))
                Gnew.graphObj.remove_edge(v, u)

            # Delete the edge in Tnew
            if (u, v) in Tnew.graphObj.edges():
                Tnew.graphObj.remove_edge(u, v)
            elif (v, u) in Tnew.graphObj.edges():
                Tnew.graphObj.remove_edge(v, u)

            # Check other contracted vertices
            for i in range(len(Tnew.graphObj.nodes())):
                if Tnew.vertices[i] == v:
                    Tnew.vertices[i] = u
                if Gnew.vertices[i] == v:
                    Gnew.vertices[i] = u
            """
                    
        # Recursively call helper            
        lemma7Helper(Tnew, Gnew, r, approx, rDepth+1, newEdges)

        j = nLeaves-1
        while True:

            overflow = False
            
            # Execute ek[j] = ek[j]->next
            ek[j].pop(0)

            if len(ek[j]) == 0:
                ek[j] = [n for n in nx.all_neighbors(G.graphObj, lfArr[j])]
                overflow = True

            #if rDepth == 0:
            #    print(f"lfArr[{j}]: {lfArr[j]} : {overflow}")

            j -= 1

            if (not overflow) or (j < 0):
                break
            
        if j < 0:
            if rDepth == 0:
                print("Combination overflow!")
                break






def lemma7(T, G, r, approx):
    """Let G=(V, E) and T=(V, F) be a graph and a tree rooted at r such that E \cap F = \emptyset 
    holds and T + E = (V, F \cup E) is 2-edge-connected. If |LEAF(r)| <= l for some constant l, 
    then a smallest 2-edge-connected spanning subgraph H = (V, F \cup E') containing T can 
    be found in O(m + n) time, where n = |V| and m = |E \cup F|."""

    global MIN_EDGES
    global LEMMA_EDGES

    l = (4 / approx) - 1

    # Reset max
    MIN_EDGES = math.inf

    if len(LEMMA_EDGES) > 0:
        LEMMA_EDGES = []

    des = graph.descendants(T, r)

    # Make a copy of T and G using desc for V
    G_new = graph.MyGraph(n=des)
    G_new.graphCopy(G)
    #G_new.add_nodes_from(des)
    E_new = []
    for edge in G.graphObj.edges():
        if edge[0] in des and edge[1] in des:
            E_new.append(edge)
    G_new.add_edges_from(E_new)


    T_new = graph.MyGraph(n=des)
    T_new.graphCopy(T)
    #T_new.add_nodes_from(des)
    E_new = []
    for edge in T.graphObj.edges():
        if edge[0] in des and edge[1] in des:
            E_new.append(edge)
    T_new.add_edges_from(E_new)
    
    lemma7Helper(T_new, G_new, r, approx, 0, None)

    #print("Lemma 7 output:")

    # Retain and merge pairs
    for p in LEMMA_EDGES:
        u1 = G.vertices[p[0][0]]
        u2 = G.vertices[p[0][1]]

        if (u1, u2) in G.graphObj.edges() or (u2, u1) in G.graphObj.edges():
            # Retain the edge (u1, u2), then contract (u1, u2) in both T and G
            graph.retainMergeTrim(T, G, u1, u2)

            """
            T.vertices[u2] = u1
            G.vertices[u2] = u1

            # Delete the edge in G
            if (u1, u2) in G.graphObj.edges():
                G.retain.append((u1, u2))
                T.retain.append((u1, u2))
                G.graphObj.remove_edge(u1, u2)
            elif (u2, u1) in G.graphObj.edges():
                G.retain.append((u2, u1))
                T.retain.append((u2, u1))
                G.graphObj.remove_edge(u2, u1)

            # Delete the edge in T
            if (u1, u2) in T.graphObj.edges():
                T.graphObj.remove_edge(u1, u2)
            elif (u2, u1) in T.graphObj.edges():
                T.graphObj.remove_edge(u2, u1) 

            # Check other contracted vertices
            for i in range(len(T.graphObj.nodes())):
                if T.vertices[i] == u2:
                    T.vertices[i] = u1
                if G.vertices[i] == u2:
                    G.vertices[i] = u1
            """

    # lemma7 doesn't return anything
    
    