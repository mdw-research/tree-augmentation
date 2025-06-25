import sys
import networkx as nx
import time
import graph
from chain import Chain, Swing
import math
import lemma7
import treegenerator as tg

def case1(T, G):
    """There is an l-closed leaf tree T[D(v)],
    where T[D(v)] is the subgraph of T induced by the descendants of v."""
    
    # Initialize return value to False
    ret = False

    # Get list of all fringe vertices in T or F_leaf
    fringeList = graph.fringes(T, T.root)
    #print("Fringe:", fringeList)

    for v in fringeList:
        v = T.vertices[v]
        if graph.l_closed(T, G, v):
            #print(v, "is l-closed")
            
            des = graph.leaves(T, v)

            # Construct E_leaf, which is the set of edges in E connecting two leaf vertices
            E_leaf = list(filter(lambda x : (x[0] in des) and (x[1] in des), G.graphObj.edges()))

            # Construct graph (Ch(v), E_leaf)
            G_M = nx.Graph()
            G_M.add_nodes_from(des)
            G_M.add_edges_from(E_leaf)

            #print("G_M:", G_M.nodes(), G_M.edges())

            # Compute maximum matching M* for the graph (Ch(v), E_leaf)
            M = list(nx.maximal_matching(G_M))
            #print("M:", M)

            # Get vertices that are in M*
            VM = []
            for edge in M:
                u = edge[0]
                u = T.vertices[u]
                if u not in VM:
                    VM.append(u)
                v2 = edge[1]
                v2 = T.vertices[v]
                if v2 not in VM:
                    VM.append(v2)

            # Find the set of vertices that are not part of matching M*
            Vw = list(filter(lambda x : x not in VM, des))

            # Pick arbitrary edges in G from Vw and add them to M*
            Ew = []
            for edge in G.graphObj.edges():
                if T.vertices[edge[0]] in Vw and T.vertices[edge[1]] not in Vw:
                    Ew.append(edge)
                    Vw.remove(T.vertices[edge[0]])
                elif T.vertices[edge[0]] not in Vw and T.vertices[edge[1]] in Vw:
                    Ew.append(edge)
                    Vw.remove(T.vertices[edge[1]])
            Eopt = M + Ew
            #print(Eopt)
            
            # Eopt is the smallest subset of E that covers F_leaf
            # Add Eopt to retain list
            for e in Eopt:
                #print("Case 1: Retain", e)
                graph.retain(T, G, e)
            #G.retain = G.retain + Eopt
            #T.retain = T.retain + Eopt
            #print("Case 1 Check 1:", T.retain)
                
            if len(Eopt) != 0:
                ret = True

            # Contract all vertices in D(v) for both T and G, and delete any self-loops
            desc = graph.descendants(T, v)
            #print("Desc of", v, ":", desc)
            for curDes in desc:
                u = G.vertices[curDes]
                #print("Compare:", u, "and", T.vertices[v])
                if u != T.vertices[v]:
                    neighbors = [n for n in nx.all_neighbors(G.graphObj, u)]
                    #print("Neighbors of", u, ":", neighbors)
                    if len(neighbors) != 0:
                        u2 = neighbors[0]
                        if u != G.vertices[u2]:
                            #print("Case 1: Retain and trim", u, u2)
                            graph.retainMergeTrim(T, G, u, u2)
                            #print("Case 1 Check 2:", T.retain)
                            #print("T after merge:", T.graphObj.nodes(), T.graphObj.edges())
                            #print("G after merge:", G.graphObj.nodes(), G.graphObj.edges())
                        
            """
            v_dash = desc[0]
            for v in desc:
                # Ensure all vertices have the same "contracted" vertex
                G.vertices[v] = v_dash
                T.vertices[v] = v_dash

                # Delete any edges in T that are part of the contraction
                neighborList = [n for n in nx.all_neighbors(T.graphObj, v)]
                for neighbor in neighborList:
                    if neighbor in desc:
                        T.graphObj.remove_edge(v, neighbor)

                # Delete any edges in G that are part of the contraction
                neighborList = [n for n in nx.all_neighbors(G.graphObj, v)]
                for neighbor in neighborList:
                    if neighbor in desc:
                        G.graphObj.remove_edge(v, neighbor)

                # Check other contracted vertices
                for i in range(len(T.graphObj.nodes())):
                    if T.vertices[i] == v:
                        T.vertices[i] = v_dash
                    if G.vertices[i] == v:
                        G.vertices[i] = v_dash
            """

    #print(T.edges())
    #print(G.edges())
    #print(graph.vertices)
    return ret

def case2(T, G):
    """There is a leaf tree T[D(v)] such that T[D(v)] is not l-closed and there
    is a trivial or isolated leaf vertex u in Ch(v)"""
     
    # Initialize return value to False
    ret = False

    # Get list of all fringe vertices in T or F_leaf
    fringeList = graph.fringes(T, T.root)
    #print("Fringe:", fringeList)

    for v in fringeList:
        parent = T.vertices[v]

        # Check that T[D(v)] is not l-closed
        #print("Is", parent, "l-closed?", graph.l_closed(T, G, parent))
        if graph.l_closed(T, G, parent) == False:
            #print(parent, "is not l-closed")
            
            # Construct Iv, which is the set of isolated vertices in Ch(v)
            Iv = graph.isolated(T, G, parent)

            for cur in Iv:

                # For each trivial leaf vertex u', retain edge (u', parent)
                cur = T.vertices[cur]

                # Vertex u is trivial if E_G(u) contains exactly one non-redundant edge
                triv = graph.trivial(T, G, cur)
                #print("triv of", cur, "is", triv)

                # If cur is trivial, retain (cur, v) and contract into v. If there is
                # a remaining isolated vertex, contract v and parent into a vertex
                if triv != -1 and (cur != G.vertices[parent]):
                    ret = True

                    # Retain the edge (cur, triv), then contract (cur, triv) in both T and G
                    #print("Case 2: Retain and trim", cur, triv)
                    graph.retainMergeTrim(T, G, cur, triv)

                else:
                    # If there remains an isolated vertex in Iv, contract v' = parent(v) and v into a vertex.
                    # Do not retain
                    ret = True

                    # Get parent of parent
                    #grandParent = T.parents[parent]
                    grandParent = graph.getParent(T, parent)

                    # Contract the finge edge f' = (v', v), where v' is p(v)
                    tp = graph.treePath(T, parent, grandParent)
                    graph.mergeList(G, tp)
                    graph.mergeList(T, tp)
                    

    #print(T.edges())
    #print(G.edges())
    #print(graph.vertices)
    return ret

def case3(T, G):
    """There is a leaf tree T[D(v)] such that T[D(v)] is not l-closed, |Ch(v)| = 3,
    and Ch(v) contains no trivial or isolated vertex."""
    
    # Initialize return value to False
    ret = False

    # Get list of all fringe vertices in T or F_leaf
    fringeList = graph.fringes(T, T.root)
    #print("Fringe:", fringeList)

    for v in fringeList:
        parent = T.vertices[v]

        # Check that T[D(v)] is not l-closed
        if graph.l_closed(T, G, parent) == False:
            #print(parent, "is not l-closed")
            #kids = list(T.children[parent])
            kids = list(graph.children(T, parent))
            #print("kids of", parent, ":", kids)

            # Check that |Ch(v)| = 3
            if len(kids) == 3:

                # Check that Ch(v) doesn't have any isolated vertices
                iso = graph.isolated(T, G, parent)
                if len(iso) == 0:

                    isTrivial = False
                    # Check that none of the children are trivial
                    for kid in kids:
                        if graph.trivial(T, G, kid) == -1:
                            isTrivial = True
                            break
                    if isTrivial == False:
                        ret = True

                        # Get parent of parent
                        #grandParent = T.parents[parent]
                        grandParent = graph.getParent(T, parent)

                        # Contract the finge edge f' = (v', v), where v' is p(v)
                        tp = graph.treePath(T, parent, grandParent)
                        graph.mergeList(G, tp)
                        graph.mergeList(T, tp)

                        """
                        T.vertices[parent] = grandParent

                        # Delete the edge in G
                        if (grandParent, parent) in G.graphObj.edges():
                            G.graphObj.remove_edge(grandParent, parent)
                        elif (parent, grandParent) in G.edges():
                            G.graphObj.remove_edge(parent, grandParent)

                        # Delete the edge in T
                        if (grandParent, parent) in T.graphObj.edges():
                            T.graphObj.remove_edge(grandParent, parent)
                        elif (parent, grandParent) in T.graphObj.edges():
                            T.graphObj.remove_edge(parent, grandParent)

                        # Check other contracted vertices
                        for i in range(len(T.graphObj.nodes())):
                            if T.vertices[i] == parent:
                                T.vertices[i] = grandParent
                            if G.vertices[i] == parent:
                                G.vertices[i] = grandParent
                        """
                    

    #print(T.edges())
    #print(G.edges())
    #print(graph.vertices)
    return ret

def case4(T, G):
    """There is a non-pseudo-fringe edge f'=(v'',v') in F and a fringe vertex v
    with a path from v'' to v' to v such that T[D(v')] has exactly three leaf
    vertices u1, u2, and u3, two of     which (say u1, u2) are children of v
    and one of which (say u3) is a child of v', and there's an edge (u2,u3) in E."""

    # Initialize return value to False
    ret = False

    # Get list of all fringe vertices in T or F_leaf
    fringeList = graph.fringes(T, T.root)
    #print("Fringe:", fringeList)

    for v in fringeList:
        f = T.vertices[v]

        # Get children of f
        #kids = list(T.children[f])
        kids = list(graph.children(T, f))
        #print("Children of", f, "are", kids)

        # First check there are exactly two chilren of f, which will be our u1 and u2
        if len(kids) == 2:
            u1 = kids[0]
            u2 = kids[1]
            
            #print("Check if edge (", u1, ",", u2, ") is in G")
            # Check if edge (u1, u2) is in G
            if (u1, u2) in G.graphObj.edges() or (u2, u1) in G.graphObj.edges():
                # Get the parent of f
                #print("Yes")
                #parent = T.parents[f]
                parent = graph.getParent(T, f)

                # Climb up the tree up to the root
                while parent != None:
                    # Get children of parent
                    #curKids = list(T.children[parent])
                    curKids = list(graph.children(T, parent))
                    #print("Children of", parent, ":", curKids)

                    # Check if there are exactly two children
                    if len(curKids) == 2:
                        # edge (parent, f) might be a potential non-pseudo-fringe edge

                        # Store the parent in case we need to stop the while loop
                        parent_temp = parent
                        parent = None
                        #print("Storing parent:", parent_temp, parent)

                        # Make u3 the leaf hanging from non-pseudo-fringe vertex
                        u3 = graph.isLeaf(T, curKids[0])
                        #print("Test u3:", u3)
                        if u3 == None:
                            u3 = graph.isLeaf(T, curKids[1])

                        if u3 != None:
                            #print(u3, "is a leaf")
                            # Check that parent_temp isn't l-closed
                            #print("Check if", parent_temp, "is l-closed")
                            if graph.l_closed(T, G, parent_temp) == False:
                                #print(parent_temp, "is not l-closed")
                                # Check if there are edges between u1 and u3 and between u2 and u3 in G
                                u1_u3 = (u1, u3) in G.graphObj.edges() or (u3, u1) in G.graphObj.edges()
                                u2_u3 = (u2, u3) in G.graphObj.edges() or (u3, u2) in G.graphObj.edges()

                                if u1_u3 == True:
                                    unconnected = None
                                else:
                                    unconnected = u1

                                if unconnected == None:
                                    if u2_u3 == False:
                                        unconnected = u2

                                unconnected_connects_outside = 0

                                # Get the edge of u1 or u2 if it exists
                                if unconnected != None:
                                    neighborList = [n for n in nx.all_neighbors(G.graphObj, unconnected)]

                                    # Get non p-fringe descendants
                                    treeVerts = graph.descendants(T, parent_temp)
                                    
                                    if not (u1_u3 and u2_u3):
                                        for neighbor in neighborList:
                                            current = T.vertices[neighbor]
                                            if current in treeVerts:
                                                # Mark for parent contraction
                                                unconnected_connects_outside = 1
                                                break

                                    if (u1_u3 and u2_u3) or unconnected_connects_outside == 1:
                                        # Prime edge type 2
                                        ret = True

                                        # Get parent of parent
                                        #grandparent = T.parents[parent_temp]
                                        grandparent = graph.getParent(T, parent_temp)
                                        # Contract the edge (v'', v'), where v'' is grandparent and v' is parent_temp
                                        tp = graph.treePath(T, v, grandparent)
                                        #print("Tree path:", tp)
                                        graph.mergeList(G, tp)
                                        graph.mergeList(T, tp)

                                        """
                                        T.vertices[parent_temp] = grandparent
                                        G.vertices[parent_temp] = grandparent

                                        # Delete the edge in G
                                        if (grandparent, parent_temp) in G.graphObj.edges():
                                            G.graphObj.remove_edge(grandparent, parent_temp)
                                        elif (parent_temp, grandparent) in G.graphObj.edges():
                                            G.graphObj.remove_edge(parent_temp, grandparent)

                                        # Delete the edge in T
                                        if (grandparent, parent_temp) in T.graphObj.edges():
                                            T.graphObj.remove_edge(grandparent, parent_temp)
                                        elif (parent_temp, grandparent) in T.graphObj.edges():
                                            T.graphObj.remove_edge(parent_temp, grandparent)

                                        # Check other contracted vertices
                                        for i in range(len(T.graphObj.nodes())):
                                            if T.vertices[i] == parent_temp:
                                                T.vertices[i] = grandparent
                                            if G.vertices[i] == parent_temp:
                                                G.vertices[i] = grandparent
                                        """

                                    else:
                                        # Retaining edge (u1, u2) the contract (u1, u2) in both T and G
                                        ret = True

                                        print("Case 4: Retain and trim", u1, u2)
                                        graph.retainMergeTrim(T, G, u1, u2)

                                        """
                                        T.vertices[u1] = u2

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
                                            if T.vertices[i] == u1:
                                                T.vertices[i] = u2
                                            if G.vertices[i] == u1:
                                                G.vertices[i] = u2
                                        """

                    # Update parent to check if we're at the root
                    if parent != None:
                        #np = T.parents[parent]
                        np = graph.getParent(T, parent)
                        if np == parent:
                            parent = None
                        else:
                            parent = np

    #print(T.edges())
    #print(G.edges())
    #print(graph.vertices)
    return ret

def findChains(T, v):
    """For each branch vertex u, a path P_T(u,u') is called a chain of u if u' is
    a fringe or branch vertex and P_T(u,u') - {u, u'} contains no fringe or
    branch vertex. Any internal vertex u'' in a chain has exactly one non-leaf
    vertex in Ch(u'')."""
    v = T.vertices[v]

    chains = []

    # Get list of branches in T[D(v)]
    branches = graph.branches(T, v)
    #print("Branches of", v, ":", branches)

    # Look at each branch vertex b (u)
    for b in branches:
        u = T.vertices[b]
        #queue = T.children[u]    
        queue = graph.children(T, u)
        #print("Queue:", queue)

        # Traverse through each child of branch b
        # A while loop is used because may need to adjust queue
        index = 0
        while index < len(queue):
            #print("Queue:", queue)
            curQueue = queue[index]
            cv = T.vertices[curQueue]
            #print("Look at", cv)

            # If cv is a leaf vertex, go to the next child
            if graph.isLeaf(T, cv) != None:
                index += 1
                #print(cv, "is a leaf")
                continue

            #print("Index:", index)
            #print("Queue (", len(queue), "):", queue)
            # Check if cv (u') is a branch vertex or fringe vertex
            #print("Is", cv, "a branch?:", graph.isBranch(T, cv))
            #print("Is", cv, "a fringe?:", graph.isFringe(T, cv))
            if graph.isBranch(T, cv) or graph.isFringe(T, cv):
                #u2 = T.parents[cv]
                u2 = graph.getParent(T, cv)
                #while u != T.parents[u2] and u2 != T.vertices[T.root]:
                while u != graph.getParent(T, u2) and u2 != T.vertices[T.root]:
                    u2 = graph.getParent(T, u2)
                    
                newChain = Chain(u, u2, cv)
                #print("Create chain:", newChain)

                chains.append(newChain)
                    
            else:
                # cv (u') is neither a branch vertex nor a fringe vertex
                # Add children of cv to the queue
                #nextList = T.children[cv]
                nextList = graph.children(T, cv)
                queue = queue + nextList

            # Go to next child in branch b
            index += 1

    return chains

def immediateThorns(T, v):
    """A leaf vertex is a thorn vertex if its parent is not a fringe vertex.
    Let THORN(v) denote the set of all thorn vertices in T[D(v)]."""

    #kids = T.children[v]
    kids = graph.children(T, v)

    # Look at each kid
    i = 0
    while i < len(kids):
        # If kid is not a leaf, remove it and return the remaining list
        if graph.isLeaf(T, kids[i]) == None:
            kids.pop(i)
            return kids
        i += 1
    return kids
            

def upperEdge(T, G, chain):
    """Identifies the upper edge in the chain if it exists.
    Returns None if it doesn't exist."""

    # Get instance variables u, uk, and u2 from chain object
    u = G.vertices[chain.u]
    uk = G.vertices[chain.uk]
    u2 = G.vertices[chain.u2]

    #print("u uk u2:", u, uk, u2)

    # Get descendants of u2
    du2 = graph.descendants(T, u2)
    #print("Descendants of", u2, ":", du2)

    # Go up the chain from uk
    v = uk
    while v != u:
        #print("v:", v)
        thornsAndV = None

        if v != uk:
            # Look for edges in the thorns adjacent to v
            thornsAndV = immediateThorns(T,v) + [v]
        else:
            thornsAndV = [v]

        #print("thornsAndV:", thornsAndV)

        for tv in thornsAndV:
            # Check each vertex for one that resides outside the chain's descendants
            neighborList = [n for n in nx.all_neighbors(G.graphObj, tv)]
            #print("Neighbors of", tv, "in G:", neighborList)
            for otherV in neighborList:
                otherV = G.vertices[otherV]
                if otherV not in du2:
                    return (tv, otherV)
        
        #v = T.parents[u]
        v = graph.getParent(T, v)

    return None

def nextInChain(T, v):
    """Gets the next vertex in the chain or None"""
    if v == None:
        return None

    v = T.vertices[v]

    if graph.isBranch(T, v) == True:
        return None

    #kids = T.children[v]
    kids = graph.children(T, v)

    v = None
    for kid in kids:
        v = T.vertices[kid]
        if graph.isLeaf(T, v) == False:
            break

    return v
    
def findSwings(T, G, chain):
    """An edge g is a swing edge if u1 -> p(x1) -> p(x2) -> uk and path P_T(p(x1),p(x2))
    has no thorn vertex other than x1 and x2."""

    # Get instance variables from chain object
    u = chain.u
    uk = chain.uk

    #print("Find Swing for chain:", u, uk, chain.ua)

    #if chain.ua == None:
    #    return
    
    dua = graph.getDepth(T, chain.ua)

    higher = None
    lower = 0

    cu = chain.u2
    # Go through the chain
    while cu != None and cu != uk:
        #print("Look at:", cu)
        thrns = immediateThorns(T, cu)
        #print("Thorns of", cu, ":", thrns)
        if len(thrns) > 2:
            higher = None
        elif len(thrns) == 0:
            pass
        elif len(thrns) == 2:
            higher = None

            # Get the two thorn vertices
            thrn1 = G.vertices[thrns[0]]
            thrn2 = G.vertices[thrns[1]]

            #print("Check for edge (", thrn1, ",", thrn2, ")")
            # Determine if there is an edge between thrn1 and thrn2
            e = None
            if (thrn1, thrn2) in G.graphObj.edges():
                e = (thrn1, thrn2)
            elif (thrn2, thrn1) in G.graphObj.edges():
                e = (thrn2, thrn1)

            # If edge e exists
            if e != None:
                #print("We have edge", e)
                # Create a Swing object
                newSW = Swing(T, e[0], e[1], e)

                # Get the depths of the thorn vertices
                dHigher = graph.getDepth(T, e[0])
                dLower = graph.getDepth(T, e[1])

                # Compare depths of thrn1 and thrn2 with respect to the depths of chain.ua and uk
                if dua < dHigher - 1:
                    newSW.inLower = True
                #if dHigher < graph.getDepth(T, chain.ua) and dLower > graph.getDepth(T, T.parents[uk]):
                if dHigher < graph.getDepth(T, chain.ua) and dLower > graph.getDepth(T, graph.getParent(T,uk)):
                    newSW.inLower = True

                # Add swing edges to chain object
                chain.swings.append(newSW)
                chain.swingEdges.append(e)

        else:
            # len(thrns) == 1
            if higher == None:
                higher = T.vertices[thrns[0]]
            else:
                # If there is a valid thorn above, check for a connection
                currentThorn = T.vertices[thrns[0]]

                # Check if edge (higher, currentThorn) exists in G
                e = None
                if (higher, currentThorn) in G.graphObj.edges():
                    e = (higher, currentThorn)
                elif (currentThorn, higher) in G.graphObj.edges():
                    e = (currentThorn, higher)

                # If edge e exists
                if e != None:
                    # Create a Swing object
                    newSW = Swing(T, e[0], e[1], e)

                    # Get the depths of the vertices in edge e
                    dHigher = graph.getDepth(T, e[0])
                    dLower = graph.getDepth(T, e[1])

                    # Compare depths 
                    if dua < dHigher - 1:
                        newSW.inLower = True

                    # Add swing edges to chain object
                    chain.swings.append(newSW)
                    chain.swingEdges.append(e)
                    higher = None
                else:
                    higher = currentThorn
              
        cu = nextInChain(T, cu)

    # NOTE: Nothing is returned for this function
    

def findBindingEdges(T, G, chain):
    """An edge e_g = (w, y) in E (w in LEAF(r)) such that P_T(p(w),y) contains up(g) is called
    a binding edge of g, if a leaf vertex z_g in LEAF(r) - {x1,x2,w} is contained in the path
    P_T(dwn(g),y) or incident to P_T(dwn(g),y) via the leaf edge (p(z_g),z_g), or if the path
    P_T(p(w),up(g)) has a leaf vertex z_g in LEAF(r) - {x1,x2,w} with (w,z_g) not in E or
    two leaf vertices z_g, z'_g in LEAF(r) - {x1,x2,w}."""

    # Get instance variables from chain object
    ua = chain.ua
    uk = chain.uk
    uaNext = nextInChain(T, ua)

    # ua_next = ua_next ? ua_next : ua;
    if uaNext == None:
        uaNext = ua

    uaToUk = []
    if uaNext != None:
        # Get the path between ua and uk in T that doesn't include ua and uk
        #uaToUk = graph.treePath(T, uaNext, T.parents[uk])
        #print("uk:", uk)
        #print("uaNext:", uaNext)
        uaToUk = graph.treePath(T, uaNext, graph.getParent(T, uk))

    #print("Chain:", chain.u, chain.u2, uk, ua, uaNext)
    #print("uaToUk:", uaToUk)
    # Go through each swing edge
    for swing in chain.swings:
        #print("Swing:", swing)
        upg = swing.pUp
        dng = swing.pDown
        
        #print("Swing:", swing.up, swing.down, swing.pUp, swing.pDown, swing.isSoloEdge)
        #print("uaToUk:", uaToUk)
        #print("upInLower:", upg in uaToUk)
        #print("downInLower:", dng in uaToUk)
        # If upg and dng are both in uaToUk
        if (upg in uaToUk) and (dng in uaToUk):
            #print(upg, "and", dng, "are in", uaToUk)
            #print("u2", chain.u2)
            wCandidates = graph.thorns(T, chain.u2)
            upg_leaves = graph.leaves(T, upg)

            #print("wCandidates:", wCandidates)
            #print("upg_leaves:", upg_leaves)

            # Remove everything in upg_leaves from wCandidates
            for l in upg_leaves:
                if l in wCandidates:
                    wCandidates.remove(l)

            yCandidates = graph.descendants(T, upg)

            # Go through each vertex in wCandidates
            for cw in wCandidates:
                w = T.vertices[cw]

                # Go through neighbors of w in G
                neighborList = [n for n in nx.all_neighbors(G.graphObj, w)]
                for neighbor in neighborList:
                    y = G.vertices[neighbor]
                    if y in yCandidates:
                        zgNot = [w, swing.up, swing.down]

                        # down_G to Y
                        p1 = graph.treePath(T, dng, y)
                        p1List = []
                        for p1c in p1:
                            p1List.append(immediateThorns(T, p1c))

                        # Remove everything in zgNot from p1List
                        for z in zgNot:
                            if z in p1List:
                                p1List.remove(z)

                        # If there's still something ni p1List
                        if len(p1List) > 0:
                            # Add edge (w, neighbor) to swing.
                            swing.bindingEdges.append((w,neighbor))

                            if (w, neighbor) not in chain.bindingEdges and swing.inLower == True:
                                # Add edge (w, neighbor) to chain
                                chain.bindingEdges.append((w,neighbor))

                            continue

                        # P(W) to UP(G)
                        #p2 = graph.treePath(T, T.parents[w], upg)
                        p2 = graph.treePath(T, graph.getPar(T, w), upg)
                        p2List = []
                        for p2c in p2:
                            p2List.append(immediateThorns(T, p2c))

                        # Remove everying in zgNot from p2List
                        for z in zgNot:
                            if z in p2List:
                                p2List.remove(z)

                        # If there are at least 2 vertices in p2List
                        if len(p2List) >= 2:
                            # Add edge (w, neighbor) to swing.
                            swing.bindingEdges.append((w,neighbor))

                            if (w, neighbor) not in chain.bindingEdges and swing.inLower == True:
                                # Add edge (w, neighbor) to chain
                                chain.bindingEdges.append((w,neighbor))

                            continue

                        elif len(p2List) > 0:
                            # Check for a zg with no edge to w
                            l = T.vertices[p2List[0]]
                            if ((l, w) not in G.graphObj.edges()) and ((w, l) not in G.graphObj.edges()):
                                # Add edge (w, neighbor) to swing.
                                swing.bindingEdges.append((w,neighbor))

                                if (w, neighbor) not in chain.bindingEdges:
                                    # Add edge (w, neighbor) to chain
                                    chain.bindingEdges.append((w,neighbor))

                                continue

            #print("Binding Edges:", swing.bindingEdges)
            #print("inLower", swing.inLower)
            if len(swing.bindingEdges) == 0 and swing.inLower == True:
                swing.isSoloEdge = True

    # NOTE: This function doesn't return anything

def processChains(T, G, chains):
    """Identifies the components of each chain."""

    for ch in chains:
        #print("Chain:", ch)
        # Get an upper edge. upperEdge will return the vertex associated with the edge or None
        upEdgeVertex = upperEdge(T, G, ch)
        
        #print("Upper:", upEdgeVertex)
        if upEdgeVertex != None:
            ch.ep = upEdgeVertex
            ch.ua = upEdgeVertex[0]
        findSwings(T, G, ch)           
        findBindingEdges(T, G, ch)            

def A3(T, G, P):
    """Returns True if T[D(v)] has no solo edge (defined in the subtree T[D(v)] rooted at v)"""
    #print("P:", [str(p) for p in P])
    # Look at each chain in P
    for ch in P:
        for sw in ch.swings:
            #print("Swing:", sw.up, sw.down, sw.pUp, sw.pDown, sw.isSoloEdge)
            if sw.isSoloEdge == True:
                return False
    return True

def leafEdges(T, G, v):
    v = T.vertices[v]

    leafEdgeList = []
    leafs = graph.leaves(T, v)

    for leaf in leafs:
        curLf = T.vertices[leaf]

        parentList = []
        # Move up the parents of the tree to construct parentList
        #curV = T.parents[curLf]
        curV = graph.getParent(T, curLf)
        #while curV != T.parents[v]:
        while curV != graph.getParent(T, curLf):
            parentList.append(curV)
            #curV = T.parents[curV]
            curV = graph.getParent(T, curV)

        # Go through the neighbors of curLf
        neighborList = [n for n in nx.all_neighbors(G.graphObj, curLf)]
        for neighbor in neighborList:
            otherV = T.vertices[neighbor]

            # If a neighbor of curLf is in the parent list, add it to leafEdgeList
            if otherV in parentList:
                if (curLf, neighbor) in G.graphObj.edges():
                    leafEdgeList.append((curLf, neighbor))
                else:
                    leafEdgeList.append((neighbor, curLf))

    return leafEdgeList

def leafToLeafEdges(T, G, v):
    v = T.vertices[v]

    leafEdgeList = []
    leafs = graph.leaves(T, v)
    #print("FUNCTION Leafs:", leafs)

    for leaf in leafs:
        curLf = T.vertices[leaf]

        # Go through the neighbors of curLf
        neighborList = [n for n in nx.all_neighbors(G.graphObj, curLf)]
        #print("Neighbors of", curLf, ":", neighborList)
        for neighbor in neighborList:
            otherV = T.vertices[neighbor]

            #print("Is leaf?", graph.isLeaf(T, otherV))
            # Also assert lf-closed
            if graph.isLeaf(T, otherV) != None and (curLf, neighbor) not in leafEdgeList and (neighbor, curLf) not in leafEdgeList:
                if (curLf, neighbor) in G.graphObj.edges():
                    leafEdgeList.append((curLf, neighbor))
                else:
                    leafEdgeList.append((neighbor, curLf))
    

    return leafEdgeList

def primeEdgesType1(T, G, v):
    """For a leaf tree T[D(u)] with exactly two leaf vertices {w, w'} = Ch(u),
    we call an edge g = (w, w') in E a prime edge of type-1."""

    u = T.vertices[v]
    primeEdges = []
    fringe = graph.fringes(T, u)

    for cur in fringe:
        f = T.vertices[cur]
        #kids = T.children[f]
        kids = graph.children(T, f)

        # Check if there are exactly two children
        if len(kids) == 2:
            u1 = kids[0]
            u2 = kids[1]

            # If the children vertices are connected, we have a prime edge of type-1
            if (u1, u2) in G.graphObj.edges():
                primeEdges.append((u1, u2))
            elif (u2, u1) in G.graphObj.edges():
                primeEdges.append((u2, u1))

    return primeEdges
    
def primeEdgesType2(T, G, v):
    """
    Let f = (v'', v') in F be an edge in T such that D(v') contains exactly
    three leaf vertices u1, u2, and u3 with u3 in Ch(v') and {u1,u2} = Ch(v)
    for a fringe vertex v in D(v') - v'. We call edges (u3, u1) and (u3, u2)
    prime edges of type-2 if:

        1. (u1, u2), (u1, u3), (u2, u3) in E holds and
        2. every (ui, w) in E_G(ui), i=1,2,... satisfies w in D(v')

    where (u1,u2) is a prime edge of type-1 by definition.
    """

    u = G.vertices[v]
    primeEdges = []
    fringe = graph.fringes(T, u)

    for cur in fringe:
        f = T.vertices[cur]
        #kids = T.children[f]
        kids = graph.children(T, f)

        # Check if there are exactly two children
        if len(kids) == 2:
            u1 = kids[0]
            u2 = kids[1]

            # Check if the children vertices are connected
            if (u1, u2) in G.graphObj.edges() or (u2, u1) in G.graphObj.edges():
                #parent = T.parents[f]
                parent = graph.getParent(T, f)

                # Climb up the tree to the root
                while parent != None:
                    # Get children of parent
                    #curKids = list(T.children[parent])
                    curKids = list(graph.children(T, parent))

                    # Check if there are exactly two children
                    if len(curKids) == 2:

                        # parent might bea potential pseudo-fringe vertex
                        pFringeCandidate = parent

                        # Set parent to None to stop the while loop if needed
                        parent = None

                        # Make u3 the leaf hanging from pseudo-fringe vertex
                        u3 = graph.isLeaf(T, curKids[0])
                        if u3 == None:
                            u3 = graph.isLeaf(T, curKids[1])

                        if u3 != None:
                            # THIS IS WHERE THE CODE IS DIFFERENT FROM CASE 4 or PSEUDOFRINGES

                            # Check if there are edges between u1 and u3 and between u2 and u3 in G
                            u1_u3 = (u1, u3) in G.graphObj.edges() or (u3, u1) in G.graphObj.edges()
                            u2_u3 = (u2, u3) in G.graphObj.edges() or (u3, u2) in G.graphObj.edges()

                            if u1_u3 == True and u2_u3 == True:
                                # Prime edges of type 2 exist
                                descV = graph.descendants(T, pFringeCandidate)

                                u1_or_u2_badEdge = False

                                # Check neighbors of u1
                                neighborList = [n for n in nx.all_neighbors(G.graphObj, u1)]
                                for neighbor in neighborList:
                                    otherV = T.vertices[neighbor]
                                    if otherV not in descV:
                                        u1_or_u2_badEdge = True
                                        break

                                # Check neighbors of u2
                                neighborList = [n for n in nx.all_neighbors(G.graphObj, u2)]
                                for neighbor in neighborList:
                                    otherV = T.vertices[neighbor]
                                    if otherV not in descV:
                                        u1_or_u2_badEdge = True
                                        break

                                # If u1_or_u2_badEdge is false, then add (u1, u3) and (u2, u3) as prime edges
                                if u1_or_u2_badEdge == False:
                                    if (u1, u3) in G.graphObj.edges():
                                        primeEdges.append((u1, u3))
                                    else:
                                        primeEdges.append((u3, u1))

                                    if (u2, u3) in G.graphObj.edges():
                                        primeEdges.append((u2, u3))
                                    else:
                                        primeEdges.append((u3, u2))
                                        

                    # Update parent to check if we're at the root
                    if parent != None:
                        #np = T.parents[parent]
                        np = graph.getParent(T, parent)
                        if np == parent:
                            parent = None
                        else:
                            parent = np

    return primeEdges

def E(T, G, x):
    ret = []

    for cx in x:
        u = T.vertices[cx]
        neighborList = [n for n in nx.all_neighbors(G.graphObj, u)]
        #print("Neighbors of", u, ":", neighborList)
        for neighbor in neighborList:
            v = G.vertices[neighbor]
            #print("Check (", u, ",", neighbor, ")")
            if v not in x and (u, neighbor) not in ret and (neighbor, u) not in ret:
                ret.append((u, neighbor))

    return ret
        

def high(T, G, x):
    """High(X) is the subset of E_G(X) such that for any e in E_G(X)-High(X), 
    there is an e' in High(X) with lca(e') -> lca(e) and for any two e1,e2 in High(X), 
    neither lca(e1) -> lca(e2) nor lca(e2) -> lca(e1). Thus, High(X) contains those 
    edges e with the highest lca(e)."""
    highest = None

    es = E(T, G, x)
    #print("es:", es)

    leastDepth = math.inf

    for ec in es:
        e = ec

        u = T.vertices[e[0]]
        v = T.vertices[e[1]]

        lc = graph.lca(T, u, v)
        dLc = graph.getDepth(T, lc)

        if dLc < leastDepth:
            highest = e
            leastDepth = dLc
        elif dLc == leastDepth:
            highest = e

    return highest


def cover(T, G, v, P):
    """v must be minimally lf-closed"""
    #print("CALL COVER FOR", v, ", Chains:", P)

    # Leaf edges in T[v] - edges that connect a leaf to an ancestor
    fLeaf = leafEdges(T, G, v)

    # Edges that connect two leaves
    eLeaf = leafToLeafEdges(T, G, v)
    #print("eLeaf:", eLeaf)

    # Get prime edges of type-1
    ePrime1 = primeEdgesType1(T, G, v)
    #print("ePrime1:", ePrime1)

    # Get prime edges of type-2
    ePrime2 = primeEdgesType2(T, G, v)
    #print("ePrime2:", ePrime2)

    # Combine ePrime1 and ePrime2 into a single list
    ePrime = ePrime1 + ePrime2

    # eBind is the set of all e_g's
    eBind = []

    # eUpper is the set of all e_p's
    eUpper = []

    eSwing = []

    # Go through each chain
    for chain in P:
        if len(chain.bindingEdges) > 0:
            eBind = eBind + chain.bindingEdges
        if chain.ep != None:
            eUpper.append(chain.ep)

    # PHASE 1 ---------------------------------------------------------------
    # Covering al leaf edges in T[D(v)]
    vs = graph.leaves(T, v)
    #print("Leaf edges vs:", vs)

    # Remove edges in EPrime from Eleaf
    eMat = []
    for l in eLeaf:
        eMat.append(l)
    for l in ePrime:
        if l in eMat:
            eMat.remove(l)
    #print("eMat:", eMat)

    # Construct graph (LEAF(v), E_leaf - E_prime)
    G_Mstar = nx.Graph()
    G_Mstar.add_nodes_from(vs)
    G_Mstar.add_edges_from(eMat)

    #print("GStar:", G_Mstar.nodes(), G_Mstar.edges())

    # Compute maximum matching for the graph (LEAF(v), E_leaf - E_prime)
    mStar = list(nx.maximal_matching(G_Mstar))
    #print("mStar", mStar)

    matchedV = []

    # Find out which vertices are matched from M*
    for m in mStar:
        u1 = T.vertices[m[0]]
        u2 = T.vertices[m[1]]

        matchedV.append(u1)
        matchedV.append(u2)

    # Let W be the set of unmatched vertices in LEAF(v)
    unmatchedV = list(vs)
    for m in matchedV:
        if m in unmatchedV:
            unmatchedV.remove(m)

    #print("Matched and Unmatced:", matchedV, unmatchedV)

    M1s = []
    M2s = []
    newlyMatchedV = []

    # A prime edge g in E_prime is called an unmatched prime 
    # edge if both end vertices of g are unmatched
    # Build M1s and record the edges that will soon be matched
    for e1 in ePrime1:
        u1 = T.vertices[e1[0]]
        u2 = T.vertices[e1[1]]

        if u1 in unmatchedV or u2 in unmatchedV:
            # This list will be retained
            M1s.append(e1)
            newlyMatchedV.append(u1)
            newlyMatchedV.append(u2)

    for e2 in ePrime2:
        u1 = T.vertices[e2[0]]
        u2 = T.vertices[e2[1]]
        
        if u1 in unmatchedV or u2 in unmatchedV:
            M2s.append(e2)
            newlyMatchedV.append(u1)
            newlyMatchedV.append(u2)
    
    #print("M1s and M2s:", M1s, M2s)

    #m2d should be size m1d/2
    m2d = []
    for m in M1s:
        # Check if a vertex in edge m is in one of the edges in M2s
        for m2 in M2s:
            if m[0] == m2[0] or m[0] == m2[1] or m[1] == m2[0] or m[1] == m2[1]:
                m2d.append(m)
                break
    
    # remove the newly matched vertices from unmatched
    for m in newlyMatchedV:
        if m in unmatchedV:
            unmatchedV.remove(m)

    # W minus m1' and m2'
    Wmmm = list(unmatchedV)
    for m in newlyMatchedV:
        if m in Wmmm:
            Wmmm.remove(m)

    # Retention of unmacthedV
    ew = []

    # For each unmatchedV, w
    for wl in Wmmm:
        w = T.vertices[wl]
        
        continueFlag = False

        # If has binding edge where w is the higher vertex, and it's the lowest such binding edge
        #e = (w, w)
        potentialEw = list(eBind)
        curHighestEw = None

        #print("potentialEw:", potentialEw)

        for p in potentialEw:
            if w == p[0] or w == p[1]:
                u1 = T.vertices[p[0]]
                u2 = T.vertices[p[1]]

                y = u1 ^ u2 ^ w

                # w must be greater than y
                #if graph.getDepth(T, y) < graph.getDepth(T, T.parents[w]):
                if graph.getDepth(T, y) < graph.getDepth(T, graph.getParent(T, w)):
                    if curHighestEw == None:
                        curHighestEw = (p[0], p[1])
                    else:
                        ux1 = T.vertices[w]
                        ux2 = T.vertices[w]
                        y2 = w ^ ux1 ^ ux2

                        # ew must ahve the highest y
                        if graph.getDepth(T, y) < graph.getDepth(T, y2):
                            curHighestEw = p
            else:
                break

        if curHighestEw != None:
            ew.append(curHighestEw)
            continue

        # else if w is incident to a swing, 'ew' = swing
        newEw = None

        # For each chain
        for ch in P:
            sw = ch.swingEdges
            for s in sw:
                if w == s[0] or w == s[1]:
                    u1 = T.vertices[w]
                    u2 = T.vertices[w]

                    if u2 == w:
                        u1, u2 = u2, u1

                    if graph.getDepth(T, u1) <= graph.getDepth(T, u2):
                        newEw = s
                else:
                    break

        if newEw != None:
            ew.append(newEw)
            continue

        ww = [w]
        #print("ww:", ww)
        newEw = high(T, G, ww)
        ew.append(newEw)

    #print("ew:", ew)
    
    # Retain all 'ew'
    p4eg = []

    for cg in M1s:
        p2 = None

        # Check if any of the vertices in cg.e exist in M2s
        for m in M2s:
            if cg[0] == m[0] or cg[0] == m[1] or cg[1] == m[0] or cg[1] == m[1]:
                p2 = m
                break

        if p2 != None:
            w = T.vertices[p2[0]]
            wd = T.vertices[p2[1]]

            if graph.getDepth(T, wd) > graph.getDepth(T, w):
                w, wd = wd, w
            
            desc = graph.descendants(T, w)
            newEg = high(T, G, desc)
            p4eg.append(newEg)

        else:
            u = T.vertices[cg[0]]
            ud = T.vertices[cg[1]]
            #pu = T.parents[u]
            pu = graph.getParent(T, u)
            uupu = [u]
            uupu.append(ud)
            uupu.append(pu)

            newEg = high(T, G, uupu)
            p4eg.append(newEg)
    
    """
    xx = [M1s, m2d, ew, p4eg]
    for ppp in xx:
        for eee in ppp:
            print(eee.e)
    """

    E1 = M1s + m2d + ew + p4eg
    #print("E1:", E1)
    for ec in E1:
        if ec != None:
            # Retain the edge ec, then contract ec in both T and G
            #print("Cover: Retain and trim", ec)
            graph.retainMergeTrim(T, G, ec[0], ec[1])
        
            """
            T.vertices[ec[1]] = ec[0]
            G.vertices[ec[1]] = ec[0]

            # Delete the edge in G
            if (ec[0], ec[1]) in G.graphObj.edges():
                G.retain.append((ec[0], ec[1]))
                T.retain.append((ec[0], ec[1]))
                G.graphObj.remove_edge(ec[0], ec[1])
            elif (ec[1], ec[0]) in G.graphObj.edges():
                G.retain.append((ec[1], ec[0]))
                T.retain.append((ec[1], ec[0]))
                G.graphObj.remove_edge(ec[1], ec[0])

            # Delete the edge in T
            if (ec[0], ec[1]) in T.graphObj.edges():
                T.graphObj.remove_edge(ec[0], ec[1])
            elif (ec[1], ec[0]) in T.graphObj.edges():
                T.graphObj.remove_edge(ec[1], ec[0])

            # Check other contracted vertices
            for i in range(len(T.graphObj.nodes())):
                if T.vertices[i] == ec[1]:
                    T.vertices[i] = ec[0]
                if G.vertices[i] == ec[1]:
                    G.vertices[i] = ec[0]
            """

    #print("T after Phase 1:", T.graphObj.nodes(), T.graphObj.edges())
    #print("G after Phase 2:", G.graphObj.nodes(), G.graphObj.edges()) 
    # PHASE 2 ---------------------------------------------------------------
    # Merging 2-edge-connected components in T + E1

    # Implement MERGE1
    for ch in P:
        for sw in ch.swings:
            # An edge is in a small component if only two vertices in matchedV deref to the edge
            swV = T.vertices[sw.e[0]]
            matches = 0

            for m in matchedV:
                u = T.vertices[m]
                if u == swV:
                    matches += 1

            if matches == 2:
                if sw.inLower == True:
                    retE = sw.bindingEdges[0]
                else:
                    retE = ch.ep
                
                u = T.vertices[retE[0]]
                v2 = T.vertices[retE[1]]

                tp = graph.treePath(T, u, v2)

                components = 0

                for t in tp:
                    # Calculate how many components will be merged by edge
                    for m in matchedV:
                        curM = T.vertices[m]
                        if curM == t:
                            components += 1
                            break
                
                if components >= 3:
                    # Retain the edge (u, v2), then contract (u, v2) in both T and G
                    #print("Cover components >= 3: Retain and trim", u, v2)
                    graph.retainMergeTrim(T, G, u, v2)

                    """
                    T.vertices[v2] = u

                    # Delete the edge in G
                    if (u, v2) in G.graphObj.edges():
                        G.retain.append((u, v2))
                        T.retain.append((u, v2))
                        G.graphObj.remove_edge(u, v2)
                    elif (v2, u) in G.graphObj.edges():
                        G.retain.append((v2, u))
                        T.retain.append((v2,u))
                        G.graphObj.remove_edge(v2, u)

                    # Delete the edge in T
                    if (u, v2) in T.graphObj.edges():
                        T.graphObj.remove_edge(u, v2)
                    elif (v2, u) in T.graphObj.edges():
                        T.graphObj.remove_edge(v2, u)

                    # Check other contracted vertices
                    for i in range(len(T.graphObj.nodes())):
                        if T.vertices[i] == v2:
                            T.vertices[i] = u
                        if G.vertices[i] == v2:
                            G.vertices[i] = u
                    """
                            
    # Implement MERGE2
    for ch in P:
        if ch.ep == None:
            continue

        x = ch.ua
        ua2 = T.vertices[ch.ep[1]]
        ua1 = T.vertices[ch.ep[0]]

        if ua1 == ua2:
            continue

        v1Matched = ch.u in matchedV
        numUpward = 0
        anyInMatching = False

        for sw in ch.swings:
            if sw.inLower == False:
                numUpward += 1
                u1 = T.vertices[sw.e[0]]
                u2 = T.vertices[sw.e[1]]
                if (u1 in matchedV) and (u2 in matchedV):
                    anyInMatching += 1

        # If there are others with upwards, then contract their upper edges
        if (anyInMatching == True and numUpward >= 2) or (v1Matched == True and numUpward > 0):
            uppers = []

            for chc in P:
                if chc == ch:
                    continue

                uhc1 = T.vertices[chc.ep[0]]
                uhc2 = T.vertices[chc.ep[1]]

                if uhc1 == uhc2:
                    continue

                v1MatchedC = chc.u in matchedV
                numUpwardC = 0

                for sw in ch.swings:
                    if sw.inLower == False:
                        numUpwardC += 1
                
                if numUpwardC >= 2:
                    uppers.append(chc.ep)

            if len(uppers) > 0:
                uppers.append(ch.ep)

                for ue in uppers:
                    v1 = T.vertices[ue.e[0]]
                    v2 = T.vertices[ue.e[1]]

                    # Retain the edge (v1, v2), then contract (v1, v2) in both T and G
                    #print("Cover uppers > 0: Retain and trim", v1, v2)
                    graph.retainMergeTrim(T, G, v1, v2)

                    """
                    T.vertices[v2] = v1
                    G.vertices[v2] = v1

                    # Delete the edge in G
                    if (v1, v2) in G.graphObj.edges():
                        G.retain.append((v1, v2))
                        T.retain.append((v1, v2))
                        G.graphObj.remove_edge(v1, v2)
                    elif (v2, v1) in G.graphObj.edges():
                        G.retain.append((v2, v1))
                        T.retain.append((v2, v1))
                        G.graphObj.remove_edge(v2, v1)

                    # Delete the edge in T
                    if (v1, v2) in T.graphObj.edges():
                        T.graphObj.remove_edge(v1, v2)
                    elif (v2, v1) in T.graphObj.edges():
                        T.graphObj.remove_edge(v2, v1)

                    # Check other contracted vertices
                    for i in range(len(T.graphObj.nodes())):
                        if T.vertices[i] == v2:
                            T.vertices[i] = v1
                        if G.vertices[i] == v2:
                            G.vertices[i] = v1
                    """
    #print("T after Phase 2:", T.graphObj.nodes(), T.graphObj.edges())
    #print("G after Phase 2:", G.graphObj.nodes(), G.graphObj.edges()) 
    # PHASE 3 ---------------------------------------------------------------
    # Making T[D(v)] 2-edge-connected

    curDesc = graph.descendants(T, v)
    #print("curDesc of", v, ":", curDesc)

    if v in curDesc:
        curDesc.remove(v)
    lfP = graph.leaves(T, v) + graph.pseudoFringes(T, G, v)
    #print("lfP:", lfP)

    for l in lfP:
        if l in curDesc:
            curDesc.remove(l)

    #print("curDesc without", v, "and", lfP, ":", curDesc)
    for cd in curDesc:
        #print("cd:", cd)
        u = T.vertices[cd]
        ul = [u]
        he = high(T, G, ul)
        #print("He of", ul, ":", he)
        if he != None:
            u1 = T.vertices[he[0]]
            u2 = T.vertices[he[1]]

            uo = u ^ u1 ^ u2

            # Retain the edge (u, uo), then contract (u, uo) in both T and G
            #print("Retain edge (", u, ",", uo, ")")
            #print("Cover he != None: Retain and trim", u, uo)
            graph.retainMergeTrim(T, G, u, uo)

        """
        T.vertices[v2] = v1
        G.vertices[v2] = v1

        # Delete the edge in G
        if (u, uo) in G.graphObj.edges():
            G.retain.append((u, uo))
            T.retain.append((u, uo))
            G.graphObj.remove_edge(u, uo)
        elif (uo, u) in G.graphObj.edges():
            G.retain.append((uo, u))
            T.retain.append((uo.u))
            G.graphObj.remove_edge(uo, u)

        # Delete the edge in T
        if (u, uo) in T.graphObj.edges():
            T.graphObj.remove_edge(u, uo)
        elif (uo, u) in T.graphObj.edges():
            T.graphObj.remove_edge(uo, u)

        # Check other contracted vertices
        for i in range(len(T.graphObj.nodes())):
            if T.vertices[i] == v2:
                T.vertices[i] = v1
            if G.vertices[i] == v2:
                G.vertices[i] = v1
        """

    # Nothing is returned

def lemma9(T, G, v, P, epsilon):
    """Lemma 9: For a minimally lf-closed tree T[D(v)] satisfying conditions (A1) and (A2), 
    let g=(x1,x2) in E be a lowest solo edge, and Fg = E(T*g) for the succeeding tree T*g of g.
    For any fixed epsilon > 0, an edge set E+ subseteq E that covers ~Fg and has size
    |E+| <= (1.875+epsilon) Beta(Fg) can be found in the same time complexity of COVER 
    applied to (T*g, G*g)."""

    uj = 0
    lowSolo = None
    maxDepth = 0
    deepChain = None

    for ch in P:
        for sw in ch.swings:
            if sw.isSoloEdge == True:
                curDepth = graph.getDepth(T, sw.up)
                if curDepth > maxDepth:
                    maxDepth = curDepth
                    uj = sw.up
                    deepChain = ch
                    lowSolo = sw.e

    if deepChain == None:
        print("LEMMA 9 ERROR")
        return
    
    l = (4 / epsilon) - 1
    leafs = graph.leaves(T, uj)
    
    if len(leafs) >= 1:
        chu = findChains(T, deepChain.u)
        processChains(T, G, chu)
        cover(T, G, uj, chu)
    else:
        lemma7.lemma7(T, G, uj, epsilon)

    # The following code selects the two edges to cover ~Fg
    uj = T.vertices[uj]

    d = graph.descendants(T, uj)

    # Must add two edges to cover ~Fg
    eStar = None
    wStar = 0

    #u = T.parents[uj]
    u = graph.getParent(T, uj)
    while (T.vertices[u] != T.vertices[v]) and (u != T.vertices[T.root]):
        if (u, uj) in G.graphObj.edges():
            eStar = (u, uj)
            wStar = u
        elif (uj, u) in G.graphObj.edges():
            eStar = (uj, u)
            wStar = u
        #u = T.parents[u]
        u = graph.getParent(T, u)

    z1 = None
    z2 = None
    z1d = math.inf
    z2d = math.inf

    th = graph.thorns(T, v)

    # Find z1
    for curTh in th:
        thV = T.vertices[curTh]
        dep = graph.getDepth(T, thV)
        if dep < z1d:
            z1 = thV
            z1d = dep
    
    # Find z2
    for curTh in th:
        thV = T.vertices[curTh]
        dep = graph.getDepth(T, thV)
        if dep < z2d and z1 != thV and thV != uj:
            z2 = thV
            z2d = dep

    #print("eStar:", eStar)

    # Cover ~Fg
    if z2 == None:
        if eStar != None:
            # Retain the edge estar, then contract eStar in both T and G
            #print("Lemma9 eStar != None: Retain and trim", eStar)
            graph.retainMergeTrim(T, G, eStar[0], eStar[1])

        # Retain the edge (z1, uj), then contract (z1, uj) in both T and G
        #print("Lemma9: Retain and trim", z1, uj)
        graph.retainMergeTrim(T, G, z1, uj)
        
    elif graph.getDepth(T, wStar) <= graph.getDepth(T, z2) - 1:
        # Retain the edge estar, then contract eStar in both T and G
        #print("Lemma9 depth wStar <= depth z2: Retain and trim", eStar)
        graph.retainMergeTrim(T, G, eStar[0], eStar[1])

        # Retain the edge (z1, z2), then contract (z1, z2) in both T and G
        #print("Lemma9 (z1,z2): Retain and trim", z1, z2)
        graph.retainMergeTrim(T, G, z1, z2)

    else:
        # Retain the edge (z1, uj), then contract (z1, uj) in both T and G
        #print("Lemma9 (z1, uj): Retain and trim", z1, uj)
        graph.retainMergeTrim(T, G, z1, uj)

        # Retain the edge (z1, z2), then contract (z1, z2) in both T and G
        #print("Lemma9 (z1, z2) bottom: Retain and trim", z1, z2)
        graph.retainMergeTrim(T, G, z1, z2)

    # Note that v should now have no children
    print("Children of", v, ":", [n for n in nx.all_neighbors(T.graphObj, v)])
        



def nagamochi(T, G, epsilon):
    
    # Make the "parent" of the root None
    #print("Test root:", T.root)
    T.root = list(T.graphObj.nodes())[0]
    T.parents[T.root] = T.root

    # Use BFS to establish a parent/child relationship within the tree T
    graph.dfs(T, T.root)

    #print("Tree Children:")
    #for i in range(len(T.graphObj.nodes())):
    #   print("Children of", i, ":", graph.children(T, i))

    #print("Tree Parents:", T.parents)
                      
    # While T contains more than one vertex
    #while len(T.children[T.root]) > 0:

 
    while len([n for n in nx.all_neighbors(T.graphObj, T.root)]) > 0 and len(G.graphObj.edges()) > 0:
        # While cases 1, 2, 3, or 4 holds
        cases = True
        while cases:
            cases = False
            # Execute P1, P2, P3, or P4 respectively
            while case1(T, G) == True:
                cases = True
                #print("T1:", T.graphObj.nodes(), T.graphObj.edges())
                #print("G1:", G.graphObj.nodes(), G.graphObj.edges())
                #T.retain = list(set(tuple(sorted(p)) for p in T.retain))
                #print("RETAIN after Case 1:", T.retain)
            while case2(T, G) == True:
                cases = True
                #print("T2:", T.graphObj.nodes(), T.graphObj.edges())
                #print("G2:", G.graphObj.nodes(), G.graphObj.edges())
                #T.retain = list(set(tuple(sorted(p)) for p in T.retain))
                #print("RETAIN after Case 2:", T.retain)
            while case3(T, G) == True:
                cases = True
                #print("T3:", T.graphObj.nodes(), T.graphObj.edges())
                #print("G3:", G.graphObj.nodes(), G.graphObj.edges())
                #T.retain = list(set(tuple(sorted(p)) for p in T.retain))
                #print("RETAIN after Case 3:", T.retain)
            while case4(T, G) == True:
                cases = True
                #print("T4:", T.graphObj.nodes(), T.graphObj.edges())
                #print("G4:", G.graphObj.nodes(), G.graphObj.edges())
                #T.retain = list(set(tuple(sorted(p)) for p in T.retain))
                #print("RETAIN after Case 4:", T.retain)
            # Note that RETAIN contains all edges retained by the above procedures
            
        #print("T:", T.graphObj.nodes(), T.graphObj.edges())
        #print("G:", G.graphObj.nodes(), G.graphObj.edges())   


        # Remove duplicates in RETAIN
        T.retain = list(set(tuple(sorted(p)) for p in T.retain))
        #print("RETAIN thus far:", T.retain)
        

        # Choose a minimally leaf-closed subtree T[D(v)]
        mlfc = graph.minimially_lf_closed(T, G, T.root)
        #print("MLFC", mlfc)

        if len(mlfc) != 0:

            # Find list of chains for mlfc[0]. P will be a list of Chain objects
            P = findChains(T, mlfc[0])
            processChains(T, G, P)

            # If condition A3 holds in T[D(v)]
            #print("Check A3:", A3(T, G, P))
            if A3(T, G, P) == True:
                # Compute an edge set E^apx in E which covers edges in T[D(v)] by procedure COVER
                cover(T, G, mlfc[0], P)
                #T.retain = list(set(tuple(sorted(p)) for p in T.retain))
                #print("RETAIN after Cover:", T.retain)
            else:
                # Compute an edge set E+ subseteq E which covers ~Fg by Lemma 9 with epsilon > 0
                #print("Call lemma9")
                lemma9(T, G, mlfc[0], P, epsilon)
                #T.retain = list(set(tuple(sorted(p)) for p in T.retain))
                #print("RETAIN after Lemma9:", T.retain)
            
        #print("T after iteration:", T.graphObj.nodes(), T.graphObj.edges())
        #print("G after iteration:", G.graphObj.nodes(), G.graphObj.edges())
        #print("Root:", T.root)
        #print("Vertices:", T.vertices)
        #print("Retain:", T.retain)

    # Return E', which is the set of retained edges   

    #Remove any possible duplicates before returning
    T.retain = list(set(tuple(sorted(p)) for p in T.retain))
    return T.retain
 

def main():
    #Tnodes = [n for n in range(10)]
    #Tedges = [(0, 8), (1, 5), (1, 3), (2, 8), (3, 4), (3, 8), (3, 6), (6, 7), (6, 9)]
    #Tedges = [(7,4),(2,4),(4,1),(1,9),(9,6),(6,0),(1,8),(8,3),(8,5),(5,10),(11,9)]
    #Tedges = [(1,11),(11,2),(2,7),(2,3),(3,9),(3,4),(4,10),(4,5),(5,8),(5,6),(6,0),(11,12)]
    #Tedges = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 5), (4, 6)]
    #Tedges = [(0, 1), (1, 2), (1, 4), (1, 7), (2, 3), (3, 5), (3, 6), (3, 8), (5, 11), (8, 9), (8, 10), (8, 12), (8, 13), (8, 14)]
    #Tedges = [(0, 6), (0, 4), (1, 2), (1, 4), (3, 5), (3, 7), (4, 5)]
    #Tedges = [(0, 3), (1, 3), (1, 6), (2, 4), (2, 6), (2, 7), (3, 5)]

    #T = graph.MyGraph(n=Tnodes, e=Tedges)

    #Gnodes = list(Tnodes)
    #Gedges = [(1, 2), (2, 4), (2, 6), (5, 7), (7, 0), (6, 8), (8, 9)]
    #Gedges = [(0, 1), (8, 7), (3,5), (7, 10), (3,11), (1,2)]
    #Gedges = [(1,7),(11,4),(12,2),(7,6),(2,9),(9,10),(3,5),(8,0),(3,10),(1,12),(7,9),(10,5),(10,8),(3,7),(11,7)]
    #Gedges = [(0, 4), (0, 2), (0, 5), (1, 4), (1, 6), (4, 3), (4, 5), (2, 6), (6, 3)]
    #Gedges = [(0, 2), (0, 3), (0, 5), (0, 7), (0, 8), (0, 9), (0, 10), (0, 13), (0, 4), (0, 6), (0, 11), (2, 4), (2, 5), (2, 10), (2, 13), (2, 14), (2, 9), (2, 11), (3, 1), (3, 4), (3, 12), (3, 13), (3, 7), (5, 4), (5, 1), (5, 7), (5, 8), (5, 10), (5, 13), (5, 12), (5, 14), (7, 4), (7, 6), (7, 10), (7, 12), (7, 14), (7, 8), (8, 4), (8, 6), (8, 1), (8, 11), (9, 1), (9, 4), (9, 6), (9, 11), (9, 12), (9, 13), (9, 14), (10, 1), (10, 4), (10, 14), (13, 4), (13, 12), (13, 6), (13, 14), (1, 6), (1, 12), (4, 6), (4, 11), (4, 12), (4, 14), (6, 12), (6, 14), (6, 11), (12, 11), (12, 14), (14, 11)]
    #Gedges = [(7, 5), (6, 2), (2, 0), (4, 3)]
    #Gedges = [(1, 2), (1, 4), (1, 5), (2, 5), (2, 0), (3, 7), (3, 6), (6, 7), (7, 4)]

    #G = graph.MyGraph(n=Gnodes, e=Gedges)

    # Test Tree and Edge List
    #print("T", T.graphObj.edges())
    #print("G", G.graphObj.edges())

    # We will assume that vertex 1 is the root of the tree
    #T.root = 1

    # Test graph generators

    #"""
    Tree = tg.random_tree(100)
    Graph = tg.generate_links(Tree, 0.1)

 
    Tnodes = Tree.nodes()
    Tedges = Tree.edges()
    Gnodes = Tree.nodes()
    Gedges = Graph.edges()

    Gnodes = list(Gnodes)
    Gnodes.sort()

    print(Tnodes, Tedges)
    print(Gnodes, Gedges)
    #"""
    

    T = graph.MyGraph(n=Tnodes, e=Tedges)
    G = graph.MyGraph(n=Gnodes, e=Gedges)
    
    # Make sure T = (V, F + E) is two edge connected
    TestGraph = nx.Graph()
    TestGraph.add_nodes_from(Tnodes)
    TestGraph.add_edges_from(list(Tedges)+list(Gedges))
    #print("Test:", TestGraph.nodes(), TestGraph.edges())

    # For each edge in TestGraph, remove and check if still connected
    for edge in Tedges:
        TestGraph.remove_edge(edge[0], edge[1])
        if not nx.is_connected(TestGraph):
            print("T + G is not two-edge connected")
            return
        TestGraph.add_edge(edge[0], edge[1])

    print(T.graphObj)
    print(G.graphObj)

    result = nagamochi(T, G, .1)
    print(result)
    print("Size:", len(result))
    #print(len(nagamochi(T, G, .5)))
    """
    st = time.time()
    linksAdded = nagamochi(T, L, epsilon)
    et = time.time()
    print("Nagamochi:")
    print(f"Links Added: {linksAdded}, Time: {et-st}")
    """

if __name__ == "__main__":
    main()
