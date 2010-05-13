#!/usr/bin/env python

from copy import deepcopy
from itertools import product, starmap
from collections import defaultdict

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
    
    def edges():
        return self._edges
    
    def order(self):
        return len(self._vertices)
    
    def size(self):
        return len(self._edges)
    
    def has_edge(self, u, v):
        return set([u, v]) in self._edges
    
    def has_vertex(self, v):
        return v in self._vertices
    
    def add_vertex(self, v):
        if self.has_vertex(v):
            return
        
        self._vertices.add(v)
        self._neighbors[v] = set()

    def add_edge(self, u, v):
        if u == v:
            return
        
        self.add_vertex(u)
        self.add_vertex(v)
    
        self._edges.add(set([u, v]))
        self._neighbors[u].add(v)
        self._neighbors[v].add(u)
    
    def remove_edge(self, u, v):
        if not self.has_edge(u, v):
            return
        
        self._edges.remove((u, v))
        self._neighbors[u].remove(v)
        self._neighbors[v].remove(u)
    
    def remove_vertex(self, v):
        if not self.has_vertex(v):
            return
        
        for u in self.neighbors(v):
            self.remove_edge(u, v)
        
        self._vertices.remove(v)
        del self._neighbors[v]
    
    def degree(self, v):
        return len(self.neighbors(v))
        
    def neighbors(self, v):
        return self._neighbors[v]
    
    def issubgraph(self, other):
        return self.vertices() <= other.vertices() and \
               self.edges() <= other.edges()
    
    def iter_vertices(self):
        return iter(self._vertices)
    
    def iter_edges(self):
        return iter(self._edges)
    
    def __add__(self, other):
        if isinstance(other, Graph):
            # The join of G + H consists of union(G, H) and all edges joining 
            # a vertex of G and a vertex of H.
            V = self.vertices() | other.vertices()
            E = self.edges() | other.edges()
            return Graph(V, E | set(product(U, V)))
        
        H = deepcopy(self)
        map(H.add_vertex, other)
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

    def __sub__(self, other):
        H = deepcopy(self)
        map(H.remove_vertex, other)
        return H
    
    def __mul__(self, other):
        V = product(self.vertices(), other.vertices())
        edge = lambda (u, v), (x, y): u == x and other.has_edge(v, y) or \
                                      v == y and self.has_edge(u, x)
        E = filter(edge, product(V, V))
        return Graph(V, E)
    
    def __iter__(self):
        return self.iter_vertices()
    
    def __contains__(self, v):
        return self.has_vertex(v)
    
    def __len__(self):
        return self.order()