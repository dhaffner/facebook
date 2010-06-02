#!/usr/bin/env python

from __future__ import division
from copy import deepcopy
from itertools import product
from collections import defaultdict
from operator import add

# TODO:
# - d(u, v) - distance. (may be interesting to have a sort of 'online'
#   all-pairs shortest path)
# -- powers of a graph
# -- I[u,v] - set of vertices that line on on a u-v geodesic.
# -- I[S] - union(I[u,v] where u, v in S)
# - cardinality of max clique
# - min/max degree
# - add optional weight function paramter to constructor
# - k(G) - # of components. also would be interesting to see if I can
#   have an 'online' algorithm for this as well.
# - comment code properly.

class Graph:
    def __init__(self, V=None, E=None, w=None):
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

    def density(self):
        m = self.size()
        n = self.order()
        return (2 * m) / (n * (n - 1))

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

    def closure(self):
        getpairs = lambda G: \
                   filter(lambda (u, v): (G.degree(u) + G.degree(v))  >= n,
                          product(G.vertices(), G.vertices()))

        # There's a closure joke hiding in here somewhere.
        def joinpairs(G):
            pairs = getpairs(G)

            # If there are no two vertices whose total degree is greater than
            # the order of G, then G is its own closure.
            if not pairs:
                return G

            for (u, v) in pairs:
                G.addedge(u, v)

            # Recursive call to keep forming the closure of G.
            # The end case is when no pairs are left and is handled above.
            return joinpairs(G)

        return joinpairs(deepcopy(self))

    def linegraph(self):
		"""
		Given a graph G, its line graph L(G) is a graph such that
		- each vertex of L(G) represents an edge of G; and
		- two vertices of L(G) are adjacent if and only if their corresponding
		  edges share a common endpoint ("are adjacent") in G.
		That is, it is the intersection graph of the edges of G, representing
		each edge by the set of its two endpoints.
		"""
		V = self.edges()
		E = filter(lambda (u, v), e: u in e or v in e, product(V, V))
  		return Graph(V, E)

    def inducedsubgraph(self, V):
        """
        A subgraph H of a graph G is said to be induced if, for any pair of
        vertices x and y of H, xy is an edge of H if and only if xy is an edge
        of G.
        """
        # ensure that we're given a subset of vertices in this graph
        if not V <= self.vertices():
            return

        E = filter(lambda e: e in self.edges(), product(V, V))
        return Graph(V, E)

    def edgeinducedsubgraph(self, E):
        """
        An edge-induced subgraph is a subset of the edges of a graph together
        with any vertices that are their endpoints.
        """
        # ensure that we're given a subset of edges in this graph
        if not E <= self.edges():
            return

        # "flatten" the set of edges into a set of vertices (the add operator
        # works on tuples)
        V = set(reduce(add, E))
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