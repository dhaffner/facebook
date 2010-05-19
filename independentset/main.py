#!/usr/bin/env python

# Consider the graph G = (V, E) formed letting:
# - V = {me and the people I'm Facebook friends with}
# - E = {(u, v): u and v are Facebook friends}
# 
# I want to determine the cardinality of the maximum independent set in G,
# and possibly find a maximum set. This problem is NP-hard, so an 
# approximation will most likely be used.

from __future__ import division
from time import time
from itertools import product

from facebook import Facebook
from graph import Graph
from info import API_KEY, SECRET

def facebook_init():
    facebook = Facebook(API_KEY, SECRET)

    facebook.auth.createToken()
    facebook.login()
    
    print 'After logging in, press any key...'
    raw_input()
    
    facebook.auth.getSession()
    return facebook

def maximalindependentset(G):
    M = set()
    for v in G:
        S = M & G.neighbors(v)
        if not S:
            M.add(v)
    return M 

def main():
    facebook = facebook_init()
    me = facebook.uid
    
    # To overcome the 5000-result limit of FQL, we'll ask for at most
    # at most (100 choose 2) == 4950 rows at once time.
    blocksize = 100 

    # Get my total friends count. Why does Facebook not have a simple
    # API call for this?
    count = len(facebook.fql.query(("SELECT '' FROM friend" 
                                    " WHERE uid1=%s" % (me))))
    # FQL querys
    # friends - Get all UIDs of everyone I'm friends with.
    # mutuals - Get all UID-pairs (u, v) such that u & v are both friends of
    #           mine and friends of each other. In a functional way this may
    #           be expressed like "filter(areFriends, zip(friends, friends))"
    friends = lambda i: ("SELECT uid2 FROM friend WHERE"
                         " uid1=%s"
                         " LIMIT %d,%d" % (me, i * blocksize, blocksize))
    mutuals = lambda i, j: ("SELECT uid1, uid2 FROM friend WHERE"
                            " uid1 IN (%s) AND " 
                            " uid2 IN (%s)" % (friends(i), friends(j))) 
                                  
    F = Graph([me])  # Create a graph whose sole vertex is me
    H = Graph()  # Create an empty graph which we'll use as my social graph.
    
    blocks = range(int(round(count / blocksize)))
    blockpairs = filter(lambda (i, j): i <= j, product(blocks, repeat=2))
    
    print "Building your social graph among %d vertices (friends)." % (count)
    
    t1 = time()
    
    for (i, j) in blockpairs:
        result = facebook.fql.query(mutuals(i, j))
        edges = (row.values() for row in result)
        for (u, v) in edges:
            H.addedge(u, v)
    
    G = F + H  # Let G be the join of graphs F & H. 
               # (This is the social graph.) 
    
    t2 = time()
    
    print "Graph built in %.3fs." % (t2 - t1)
    
    M = maximalindependentset(G)
    names = (row["name"] for row in 
             facebook.users.getInfo(",".join(map(str, M)), "name"))
    
    print "Graph order: %d, size: %d" % (G.order(), G.size())
    print
    print "A maximal independent set of cardinality %d:" % (len(M))
    for name in sorted(names):
        print "\t%s" % (name)

if __name__ == '__main__':
    main()
