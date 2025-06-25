import graph

# Class to define a chain
class Chain(object):

    def __init__(self, u, u2, uk):
        self.u = u
        self.u2 = u2
        self.uk = uk

        # Vertex associated with upper edge
        self.ua = None

        # Upper edge
        self.ep = None

        self.next = None
        self.prev = None

        self.swings = []

        # Contains list of edges (u, v)
        self.bindingEdges = []
        
        self.swingEdges = []

    def __str__(self):
        return f" u:{self.u} u2:{self.u2} uk:{self.uk} ua:{self.ua}"
    
    def __eq__(self, other):
        #print("Compare:", self, other)
        if self is other:
            return True
        elif type(self) != type(other):
            return False
        else:
            return self.u == other.u and self.uk == other.uk

# Class to define a swing
class Swing(object):

    def __init__(self, T, up, down, e):
        self.up = up
        self.down = down
        #self.pUp = graph.parents[up]
        self.pUp = graph.getParent(T, up)
        #self.pDown = graph.parents[down]
        self.pDown = graph.getParent(T, down)

        self.e = e

        self.isSoloEdge = False
        self.inLower = False

        self.next = None
        self.prev = None

        # Contains list of edges (u, v)
        self.bindingEdges = []

    def __str__(self):
        s =  f"{self.up} {self.down} {self.pUp} {self.pDown}\n"
        s += f"Binding Edges: {self.bindingEdges}"
        return s
        
        
