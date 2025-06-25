import networkx as nx
from bisect import bisect_left
import functools
from chain import Chain

# Create a class to represent a graph
class MyGraph(object):

    def __init__(self, n=None, e=None):

        # Create the graph structure
        self.graphObj = nx.Graph()

        self.originalSize = 0

        if n != None:
            self.graphObj.add_nodes_from(n)
            self.originalSize = len(self.graphObj.nodes())

        if e != None:
            self.graphObj.add_edges_from(e)

        # Create lists to track parent and children of the graph
        self.children = []
        self.parents = []

        # Create dictionary to track merge vertices
        self.vertices = {}

        # If the graph is a tree, track the root
        self.root = None

        # Keep track of edges that will be retained
        self.retain = []

        # Used to keep track of Edge objects for contracted vertices
        self.edges = []
        if len(self.graphObj.edges()) > 0:
            for e in self.graphObj.edges():
                self.edges.append(Edge(e[0], e[1]))

        # Initialize children, parents, and vertices
        for v in self.graphObj.nodes():
            self.children.append([])
            self.parents.append(None)
            self.vertices[v] = v

    def normalCopy(self, other):
        self.children = list(other.children)
        self.parents = list(other.parents)
        self.vertices = dict(other.vertices)
        self.root = other.root
        self.originalSize = other.originalSize
        self.graphObj.add_nodes_from(other.graphObj.nodes())
        self.graphObj.add_edges_from(other.graphObj.edges())
        self.edges = list(other.edges)

    def graphCopy(self, other):
        self.children = list(other.children)
        self.parents = list(other.parents)
        self.vertices = dict(other.vertices)
        self.root = other.root
        self.retain = list(other.retain)
        self.originalSize = other.originalSize
        self.edges = list(other.edges)

class Edge(object):

    def __init__(self, u, v):
        self.u = u
        self.v = v
        self.originalu = u
        self.originalv = v

    def __str__(self):
        return f"({self.u}, {self.v}) => ({self.originalu}, {self.originalv})"
    
def dfs(T, v):
    """Run DFS to determine the parent and children of each node."""
    visited = []
    stack = []

    stack.append(v)

    while len(stack):
        #print("Stack:", stack)
        v = stack[-1]
        stack.pop()

        if v not in visited:
            visited.append(v)

        #print("Visited:", visited)

        for neighbor in nx.all_neighbors(T.graphObj, v):
            if neighbor not in visited:
                if T.parents[neighbor] is None:
                    T.parents[neighbor] = v
                    T.children[v].append(neighbor)
                stack.append(neighbor)

"""
def dfsRec(T, v, visited):
    #Recursive call to find parent and children of each node.
    visited.append(v)
    for neighbor in nx.all_neighbors(T.graphObj, v):
        # Check if parent not set
        if T.parents[neighbor] is None:
            T.parents[neighbor] = v
            T.children[v].append(neighbor)
        if neighbor not in visited:
            dfsRec(T, neighbor, visited)
"""

def descendants(T, u):
    """Return list of desendants of vertex u."""
    #print("Call desc for", u)
    result = [u]
    descRec(T, u, result)
    return result

def descRec(T, u, result):
    """Return list of desendants of vertex u."""
    u = T.vertices[u]
    #kids = T.children[u]
    kids = children(T, u)
    #print("Kids of", u, ":", kids)
    
    for child in kids:
        #print("Check if", T.vertices[child], "is in", result)
        if T.vertices[child] not in result:
            result.append(T.vertices[child])
            descRec(T, T.vertices[child], result)
    return 


    """
    print("Check Tree:")
    print("Nodes:", T.graphObj.nodes())
    print("Edges:", T.graphObj.edges())
    print("Children:", T.children)
    print("Merged:", T.vertices)
    print("Visited:", visited)
    u = T.vertices[u]
    myList = [u]
    visited.append(u)

    # If the children list isn't empty
    if T.children[u] != []:
        print("Children of", u, ":", T.children[u])
        for child in T.children[u]:
            # Recursively construct list for each child
            if T.vertices[child] not in visited:
                myList = myList + descRec(T, T.vertices[child], visited)
    return myList
    """

def isFringe(T, u):
    """Returns True if u is a fringe vertex and False otherwise."""
    #print("Called isFringe(T,", u)

    # Get children of u
    #kids = T.children[u]
    kids = children(T, u)

    # Return False if there are no children
    if len(kids) == 0:
        return False

    # Check if each child of u is a leaf vertex
    for v in kids:
        # A vertex is a leaf vertex if it doesn't have any children
        v = T.vertices[v]
        #print("Children of", v, ":", children(T, v))
        #if len(T.children[v]) != 0:
        if len(children(T, v)) != 0:
            return False
    return True

def fringes(T, u):
    """Vertex u is a fringe vertex if all children of u are leaf vertices.
    Return the set of all fringe vertices in the subtree T[D(u)]."""

    # Check if u is combined with other vertices
    u = T.vertices[u]

    # Get descendants of u
    desc = descendants(T, u)
    #print("Descendants of", u, ":", desc)
        
    fringeList = []

    # If the vertex is a fringe vertex, add it to the list
    for v in desc:
        #print("Check if", v, "is fringe")
        if isFringe(T, v):
            fringeList.append(v)
    return fringeList

def binary_search(arr, low, high, x):
 
    # Check base case
    if high >= low:
 
        mid = (high + low) // 2
 
        # If element is present at the middle itself
        if arr[mid] == x:
            return mid
 
        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif arr[mid] > x:
            return binary_search(arr, low, mid - 1, x)
 
        # Else the element can only be present in right subarray
        else:
            return binary_search(arr, mid + 1, high, x)
 
    else:
        # Element is not present in the array
        return -1

def l_closed(T, G, u):
    """A subtree T[D(v)] is l-closed if G doesn't have an edge between
    LEAF(v) and V-D(v)."""

    # Get the descendants and the leaves of T
    desc = descendants(T, u)
    desc.sort()
    #leaves = list(filter(lambda x : (x in desc) and (len(T.children[x]) == 0), range(len(T.children))))
    leafs = leaves(T, u)
    #print("Leaves of", u, leaves)

    for cur in leafs:
        v = T.vertices[cur]
        edges = [n for n in nx.all_neighbors(G.graphObj, v)]

        for curEdge in edges:
            otherV = G.vertices[curEdge]
            index = binary_search(desc,0, len(desc)-1, otherV)
            if index == -1:
                return False

    """
    # We need V - desc and sort it to make searching faster
    descBar = list(set(T.graphObj.nodes()) - set(desc))
    descBar.sort()
    
    # Look at each vertex in leaves
    for v in leafs:
        v = T.vertices[v]

        # Get the neighbors of v in G
        edges = [n for n in nx.all_neighbors(G.graphObj, v)]
        #print("Edges:", edges)
        for otherV in edges:
            otherV = T.vertices[otherV]

            # If otherV is in descBar, there is an edge, so return False
            #print("Search", otherV, "in", descBar, "result=", bisect_left(descBar, otherV))
            index = bisect_left(descBar, otherV)
            if index != len(descBar) and descBar[index] == otherV:
                return False
    """

    return True

def nonRedundant(T, G, u):
    """Returns a list of non-redundant edges of E_G(u)"""
    u = T.vertices[u]
    #parent = T.parents[u]
    parent = getParent(T, u)

    # Keep track of vertices
    v_added = [None for i in range(G.originalSize+1)]
    nonRedundantList = []

    neighbors = [n for n in nx.all_neighbors(G.graphObj, u)]

    # Go through each edge adjacent to u
    for v in neighbors:
        curV = T.vertices[v]
        if curV != parent and curV != u and v_added[curV] == None:
            nonRedundantList.insert(0, curV)
            v_added[curV] = 1

    # Add parent to list if there are only redundant edges
    if len(nonRedundantList) == 0:
        nonRedundantList.insert(0, parent)

    return nonRedundantList   

def trivial(T, G, u):
    """Returns true if vertex u is trivial, which happens if E_G(u) has
    exactly one non-redundant edge."""

    # Get list of non-redundant edges
    nr = nonRedundant(T, G, u)

    # Check if there is exactly one non-redundant edge
    if len(nr) > 1:
        return -1
    else:
        return nr[0]
    
def isolated(T, G, parent):
    """Returns a list of isolated vertices from Ch(parent)"""
    parent = T.vertices[parent]

    # Contains the list if isolated vertices
    isolatedList = []

    #desc = T.children[parent]
    desc = children(T, parent)
    for cur in desc:
        u = T.vertices[cur]

        # Get all edges adjacent to u
        neighbors = [n for n in nx.all_neighbors(G.graphObj, u)]
        #print("Neighbors of", u, list(neighbors))

        isIsolated = True

        for v in neighbors:
            if u != v:
                # Check if the edge (u, v) is in desc
                #print("Check if", v, "is in", desc)
                if v in desc:
                    isIsolated = False
                    break

        # If cur = u is isolated, add it to isolatedList
        if isIsolated:
            #print(u, "is isolated")
            isolatedList.append(cur)

    return isolatedList

def isLeaf(T, u):
    """Returns u if u is a leaf and None otherwise."""
    u = T.vertices[u]

    #print("Children of", u, list(children[u]))

    #if len(list(T.children[u])) != 0:
    if len(list(children(T, u))) != 0:
        return None
    return u

def minimially_lf_closed(T, G, v):
    """Returns a minimally leaf-closed subtree T[D(v)]. A subtree T[D(v)] is called
    minimally lf-closed if T[D(v)] is lf-closed and there is no proper subtree T[D(u)]
    of T[D(v)] which is lf-closed."""

    v = T.vertices[v]
    des = descendants(T, v)
    #print("Desc:", des)

    #lf_close holds all lf-closed vertices
    lf_close = []

    for current in des:
        # Check if the vertex is lf-closed
        if lf_closed(T, G, current) == True:
            lfc = T.vertices[current]
            lf_close.append(lfc)

    # Each element v in lf_closed means T[D(v)] is lf-closed
    #print("lf_closed:", lf_close)
    #print("T.vertices:", T.vertices)

    ret = []

    for u in lf_close:
        desLf = descendants(T, u)

        # Remove u from desLf
        if u in desLf:
            desLf.remove(u)

        #print("des without", u, ":", desLf)

        # Check if any element in desLf is in lf_close
        found = False
        #print("Compare", desLf, "and", lf_close)
        for element in desLf:
            if element in lf_close:
                found = True
                break
            
        # Check if desLf is minimally lf-closed
        if len(desLf) != 0 and found == False:
            ret.append(u)

    return ret
        
    

def lf_closed(T, G, v):
    """Returns True if v is lf-closed and False otherwise. A subtree T[D(v)] is
    lf-closed if G has no edge between LEAF(v) \cup PFRINGE(v) and bar(D(v))."""

    v = T.vertices[v]

    leafList = leaves(T, v)
    fringes = allFringes(T, G, v)

    # Merge leaf list and fringes
    lfs = list(leafList)
    for i in fringes:
        if i not in lfs:
            lfs.append(i)

    # NOTE: lfs = LEAF(v) \cup PFRINGE(v)

    des = descendants(T, v)

    for lfp in lfs:
        u = T.vertices[lfp]
        neighborList = [n for n in nx.all_neighbors(G.graphObj, u)]

        for e in neighborList:
            otherV = T.vertices[e]

            if otherV not in des:
                return False
    
    return True




def leaves(T, u):
    """Returns list of leaf nodes from subtree T[D(u)]"""

    leafList = []

    desc = descendants(T, u)

    for v in desc:
        #if len(T.children[v]) == 0:
        if len(children(T, v)) == 0:
            leafList.append(v)

    return leafList

def allFringes(T, G, v):
    """Returns a list of all pesudo-fringes and fringes
    denoted as PFRINGE(v) in the paper."""

    v = T.vertices[v]

    pf = pseudoFringes(T, G, v)
    f = fringes(T, v)

    return pf + f

def pseudoFringes(T, G, u):
    """Pseudo-fringe vertices are the set of vertices between v' and v
    in Figure 1 from the paper, where v is a fringe vertex."""

    u = T.vertices[u]

    pseudoFringeList = []

    # Get list of all fringe vertices in T[D(u)]
    fringeList = fringes(T, u)

    for v in fringeList:
        f = T.vertices[v]

        # Get children of f
        #kids = list(T.children[f])
        kids = list(children(T, f))

        # First check there are exactly two chilren of f, which will be our u1 and u2
        if len(kids) == 2:
            u1 = kids[0]
            u2 = kids[1]

            # Check if edge (u1, u2) is in G
            if (u1, u2) in G.graphObj.edges() or (u2, u1) in G.graphObj.edges():
                #parent = T.parents[f]
                parent = getParent(T, f)

                # Climb up the tree to the root
                while parent != None:
                    # Get children of parent
                    #curKids = list(T.children[parent])
                    curKids = list(children(T, parent))

                    # Check if there are exactly two children
                    if len(curKids) == 2:

                        # parent might bea potential pseudo-fringe vertex
                        pFringeCandidate = parent

                        # Set parent to None to stop the while loop if needed
                        parent = None

                        # Make u3 the leaf hanging from pseudo-fringe vertex
                        u3 = isLeaf(T, curKids[0])
                        if u3 == None:
                            us = isLeaf(T, curKids[1])

                        if u3 != None:
                            # WE DO NOT CHECK IF pFringeCandidate IS NOT L-CLOSED. THIS IS WHERE
                            # THE CODE IS DIFFERENT FROM CASE 4

                            # Check if there are edges between u1 and u3 and between u2 and u3 in G
                            u1_u3 = (u1, u3) in G.graphObj.edges() or (u3, u1) in G.graphObj.edges()
                            u2_u3 = (u2, u3) in G.graphObj.edges() or (u3, u2) in G.graphObj.edges()

                            if u1_u3 == True and u2_u3 == True:
                                # Prime edges of type 2 exist
                                descV = descendants(T, pFringeCandidate)

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

                                # If u1_or_u2_badEdge is false, then we have a pseudo-fringe vertex
                                if u1_or_u2_badEdge == False:
                                    pseudoFringeList.append(pFringeCandidate)

                    # Update parent to check if we're at the root
                    if parent != None:
                        #np = T.parents[parent]
                        np = getParent(T, parent)
                        if np == parent:
                            parent = None
                        else:
                            parent = np

    return pseudoFringeList

def branches(T, v):
    """Returns a list of branches in T[D(v)]"""
    desc = descendants(T, v)
    b = []

    for cd in desc:
        u = T.vertices[cd]
        if isBranch(T, u):
            b.append(u)

    return b

def isBranch(T, u):
    """A vertex u is called a branch vertex if u = r or Ch(u)
    contains at least two non-leaf vertices."""
    #print("Called isBranch(T,", u)
    u = T.vertices[u]

    # If u is the root of the tree, return True
    if u == T.vertices[T.root]:
        return True

    #kids = T.children[u]
    kids = children(T, u)
    nonLeaves = 0

    #print("Children of", u, ":", kids)
    # Count how many children are leaves
    for kid in kids:
        #print("Check", kid)
        if isLeaf(T, kid) == None:
            #print("Vertex", u, ":", kid, "is not a leaf")
            nonLeaves += 1

        # If there are two or more children, then u is a branch
        if nonLeaves >= 2:
            return True

    # If u has 0 or 1 child, then u isn't a branch
    return False

def getDepth(T, v):
    """Returns the depth of vertex v in tree T"""
    if v == None:
        return 0
    
    v = T.vertices[v]
    d = 0
    #while T.parents[v] != v:
    while getParent(T, v) != v:
        d += 1
        #v = T.parents[v]
        v = getParent(T, v)
        #print("Parent:", v)
    return d

def treePath(T, u, v):
    """Returns a path a vertices between u and v in tree T."""

    u = T.vertices[u]
    v = T.vertices[v]

    uList = [u]
    vList = []

    uDepth = getDepth(T, u)
    vDepth = getDepth(T, v)

    while u != v:
        if uDepth > vDepth:
            #p = T.parents[u]
            p = getParent(T, u)
            uList.append(p)
            #print("Inserted", p)
            u = T.vertices[p]
            uDepth -= 1
        else:
            #p = T.parents[v]
            p = getParent(T, v)
            vList.insert(0, v)
            #print("Inserted", v)
            v = T.vertices[p]
            vDepth -= 1

    return uList + vList
    
def thorns(T, u):
    """Returns THORN(u), which is the set of thorn vertices in T[D(u)]"""

    u = T.vertices[u]
    l = leaves(T, u)
    th = []
    for cur in l:
        #p = T.parents[cur]
        p = getParent(T, cur)

        if not isFringe(T, p):
            th.append(cur)

    return th

def lca(T, u, v):
    """Returns least common ancestor of u and v in T"""

    u = T.vertices[u]
    v = T.vertices[v]

    uDepth = getDepth(T, u)
    vDepth = getDepth(T, v)

    while u != v:
        if uDepth > vDepth:
            #p = T.parents[u]
            p = getParent(T, u)
            u = T.vertices[p]
            uDepth -= 1
        else:
            #p = T.parents[v]
            p = getParent(T, v)
            v = T.vertices[p]
            vDepth -= 1
    
    return u

def retain(T, G, e):
    """Retains edge e from graph G"""
    if e == None:
        print("Error: Trying to retain null edge")
        return

    # Check G.edges for the original edge
    #print("Try to retain", e, T.retain)
    for edge in G.edges:
        # If we find the edge
        if (e[0] == edge.u and e[1] == edge.v) or (e[1] == edge.u and e[0] == edge.v):
            # If the original edge isn't in G.retain, add it
            #print("Found edge (", edge.u, ",", edge.v, "). Original edge (", edge.originalu, ",", edge.originalv, ")")
            if (edge.originalu, edge.originalv) not in G.retain:
                #print("Added", (edge.originalu, edge.originalv))
                G.retain.append((edge.originalu, edge.originalv))
                T.retain.append((edge.originalu, edge.originalv))
                return

def mergeVertices(G, v1, v2):
    """Merge vertices v1 and v2 into v1"""
    v1 = G.vertices[v1]
    v2 = G.vertices[v2]

    #print("MERGE:", v2, "into", v1)

    if v1 == v2:
        return
    
    # Combine vertices
    G.graphObj = nx.contracted_nodes(G.graphObj, v1, v2, False, False)

    # Update root if needed
    if v2 == G.root:
        G.root = v1

    # Update G.vertices to map combined vertices to v1
    for key in G.vertices.keys():
        if G.vertices[key] == v2:
            G.vertices[key] = v1

    # Update children and parents if G is a tree
    if G.root != None:
        for child in G.children[v2]:
            if G.vertices[child] != v1:
                G.children[v1].append(G.vertices[child])

        if v2 in G.children[v1]:
            G.children[v1].remove(v2)

        G.children[v2] = []

        #print("Children of", v1, ":", G.children[v1])
    


def mergeList(G, vs):
    """Merge path vs in G"""
    path = vs
    for index in range(len(path)-1):
        mergeVertices(G, path[index], path[index+1])

    # Update tree properties if G is a tree
    if G.root != None:
        # Reset root
        G.parents[G.root] = G.root

        # Update children list
        for i in range(len(G.children)):
            for j in range(len(G.children[i])):
                G.children[i][j] = G.vertices[G.children[i][j]]

        # Update parent list
        for i in range(len(G.parents)):
            for j in range(len(G.children)):
                if G.vertices[i] in G.children[j]:
                    G.parents[i] = j

        #print("Test vertices:", G.vertices)
        #print("Test children:", G.children)
        #print("Test parents:", G.parents)

    else:
        # Update edges if G is not a tree
        for i in range(len(G.edges)):
            G.edges[i].u = G.vertices[G.edges[i].u]
            G.edges[i].v = G.vertices[G.edges[i].v]
            

        


def retainMergeTrim(T, G, u, v):
    """Retains the edge (u, v) and contracts in both T and G"""
    if u == v or (G.vertices[u] == G.vertices[v]):
        return False
    
    edge = None
    if (u, v) in G.graphObj.edges():
        edge = (u, v)
    elif (v, u) in G.graphObj.edges():
        edge = (v, u)
    
    if edge == None:
        return False
    
    retain(T, G, edge)

    path = treePath(T, u, v)

    mergeList(T, path)
    mergeList(G, path)

    """
    T.vertices[otherVertex] = thisVertex
    G.vertices[otherVertex] = thisVertex

    # Check other contracted vertices
    for i in range(len(T.graphObj.nodes())):
        if T.vertices[i] == otherVertex:
            T.vertices[i] = thisVertex
        if G.vertices[i] == otherVertex:
            G.vertices[i] = thisVertex

    # Delete the edge in G
    if (thisVertex, otherVertex) in G.graphObj.edges():
        G.retain.append((thisVertex, otherVertex))
        T.retain.append((thisVertex, otherVertex))
        G.graphObj.remove_edge(thisVertex, otherVertex)
    elif (otherVertex, thisVertex) in G.graphObj.edges():
        G.retain.append((otherVertex, thisVertex))
        T.retain.append((otherVertex, thisVertex))
        G.graphObj.remove_edge(otherVertex, thisVertex)

    # Delete the edge in T
    if (thisVertex, otherVertex) in T.graphObj.edges():
        T.graphObj.remove_edge(thisVertex, otherVertex)
    elif (otherVertex, thisVertex) in T.graphObj.edges():
        T.graphObj.remove_edge(otherVertex, thisVertex)

    # Reset children and parents of T
    dfs(T, T.root)
    """

    return edge != None

def getParent(T, v):
    """Returns parent of v"""
    if len(T.parents) == 0:
        return None
    v = T.vertices[v]
    #return T.vertices[T.parents[v]]
    return T.vertices[T.parents[v]]

def children(T, u):
    """Returns the list of children of vertex u in T"""
    u = T.vertices[u]
    neighborList = [n for n in nx.all_neighbors(T.graphObj, u)]

    p = getParent(T, u)
    ls = []

    """
    if u == 4:
        print("CHECK 4:")
        print("Neighbors:", neighborList)
        print("Parent:", p)
    """
        
    for e in neighborList:
        notParent = T.vertices[e] != p
        notSelf = T.vertices[e] != T.vertices[u]
        if notParent == True and notSelf == True:
            ls.append(T.vertices[e])

    return ls
