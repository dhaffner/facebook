#!/usr/bin/env python

from copy import deepcopy
from itertools import product
from collections import defaultdict

# TODO:
# - line graph
# - (if possible, I doubt it:) dual graph
# - powers of a graph
# - cardinality of max clique
# - (edge-)induced subgraph
# - min/max degree
# - add optional weight function paramter to constructor
# - d(u, v) - distance. (may be interesting to have a sort of 'online'
#   all-pairs shortest path)
# - I[u,v] - set of vertices that line on on a u-v geodesic.
# - I[S] - union(I[u,v] where u, v in S)
# - k(G) - # of components. also would be interesting to see if I can
#   have an 'online' algorithm for this as well.
# - C(G) - closure of G.
 
class Graph:
    def __init__(self, V=None, E=None):
        self._edges = set(E or [])
        self._vertices = set(V or [])
        self._neighbors = defaultdict(lambda: set())

        for (u, v) in self._edges:
            self._neighbors[u].add(v)
            self._neighbors[v].add(u)            
    
    def vertices(self):
        return self._vertices
    
    def edges(self):
        return self._edges
    
    def order(self):
        return len(self._vertices)
    
    def size(self):
        return len(self._edges)
    
    def hasedge(self, u, v):
        return (u, v) in self._edges or (v, u) in self._edges
    
    def hasvertex(self, v):
        return v in self._vertices
    
    def addvertex(self, v):
        if self.hasvertex(v):
            return
        
        self._vertices.add(v)
        self._neighbors[v] = set()

    def addedge(self, u, v):
        if u == v or self.hasedge(u, v):
            return
        
        self.addvertex(u)
        self.addvertex(v)
    
        self._edges.add((u, v))
        self._neighbors[u].add(v)
        self._neighbors[v].add(u)
    
    def removeedge(self, u, v):
        if not self.hasedge(u, v):
            return
        
        self._edges.remove((u, v))
        self._neighbors[u].remove(v)
        self._neighbors[v].remove(u)
    
    def removevertex(self, v):
        if not self.hasvertex(v):
            return
        
        for u in self.neighbors(v):
            self.removeedge(u, v)
        
        self._vertices.remove(v)
    
    def popvertex(self, pred=None):
        """
        Pop and return an arbitrary vertex v of G such that pred(v) is true.
        If pred is not specified, an arbitrary vertex is popped.
        """
        if len(self) == 0:
            return
        
        w = None
        if pred:
            for v in self:
                if pred(v):
                    w = v
                    break
            if not w:
                return
        else:
            w = self._vertices.pop()
            
        for u in self.neighbors(w):
            self.removeedge(u, w)
            
        return w
    
    def degree(self, v):
        return len(self.neighbors(v))
        
    def neighbors(self, v):
        return self._neighbors[v]
    
    def complement(self):
        V = self.vertices()
        E = set(product(V, V)) - self.edges()
        return Graph(V, E)
    
    def join(self, H):
        # The join of G + H consists of union(G, H) and all edges joining 
        # a vertex of G and a vertex of H.
        self._vertices |= H.vertices()
        self._edges |= H.edges()
        self._edges |= set(product(self.vertices(), H.vertices()))
    
    def issubgraph(self, other):
        return self.vertices() <= other.vertices() and \
               self.edges() <= other.edges()
        
    def itervertices(self):
        return iter(self._vertices)
    
    def iteredges(self):
        return iter(self._edges)
    
    def __add__(self, other):
        if isinstance(other, Graph):
            # The join of G + H consists of union(G, H) and all edges joining 
            # a vertex of G and a vertex of H.
            U, W = self.vertices(), other.vertices()
            V = U | W
            E = self.edges() | other.edges()
            return Graph(V, E | set(product(U, W)))
        
        H = deepcopy(self)
        for v in other:
            H.addvertex(v)
        return H
    
    def __eq__(self, other):
        return self.vertices() == other.vertices() and \
               self.edges() == other.edges()
    
    def __le__(self, other):
        return self.issubgraph(other)
    
    def __ge__(self, other):
        return other.issubgraph(self)
    
    def __or__(self, other):
        # union(G, H)
        V = self.vertices() | other.vertices()
        E = self.edges() | other.edges()
        return Graph(V, E)

    def __and__(self, other):
        # intersection(G, H)
        V = self.vertices() & other.vertices()
        E = self.edges() & other.edges()
        return Graph(V, E)

    def __sub__(self, other):
        H = deepcopy(self)
        for v in other:
            H.removevertex(v)
        return H
    
    def __mul__(self, other):
        V = product(self.vertices(), other.vertices())
        edge = lambda (u, v), (x, y): u == x and other.hasedge(v, y) or \
                                      v == y and self.hasedge(u, x)
        E = filter(edge, product(V, V))
        return Graph(V, E)
    
    def __iter__(self):
        return self.itervertices()
    
    def __contains__(self, v):
        return self.hasvertex(v)
    
    def __len__(self):
        return self.order()
        
    def __iadd__(self, other):
        if isinstance(other, Graph):
            self.join(other)
        else:
            for v in other:
                self.addvertex(v)
        
    def __isub__(self, other):
        for v in other:
            self.removevertex(v)

    def __iand__(self, other):
        self._vertices &= other.vertices()
        self._edges &= other.edges()
        
    def __ior__(self, other):
        # union(G, H)
        self._vertices |= other.vertices()
        self._edges |= other.edges()

def maximumindepdentset(G):
    # Returns the cardinality of the largest independent set in G.
    # Reference:
    # http://http://books.google.com/books?id=jGD9pNFKI2UC&lpg=PA61&pg=PA62
    if G.size() == 0: # if G has no edges
        return G.order()
    else:
        # "Choose some nonisolated vertex v* of G"
        nonisolated = lambda v: G.degree(v) > 1
        v = G.popvertex(pred=nonisolated)
        
        # Below we write "G" instead of "G - v" since we already popped v.
        i = maximumindependentset(G)
        j = maximumindependentset(G - G.neighbors(v))
        return max(i, 1 + j)