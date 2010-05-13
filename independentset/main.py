#!/usr/bin/env python

# Consider the graph G = (V, E) formed letting:
# - V = {me and the people I'm Facebook friends with}
# - E = {(u, v): u and v are Facebook friends}
# 
# I want to determine the cardinality of the maximum independent set in G,
# and possibly find a maximum set. This problem is NP-hard, so an 
# approximation will most likely be used.

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
            print v, S
            M.add(v)
    return M 

def main():
    facebook = facebook_init()

    friends = "SELECT uid2 FROM friend WHERE uid1=%s" % (facebook.uid)
    mutuals = ("SELECT uid1, uid2 FROM friend WHERE uid1 "
               "IN (%s) AND uid2 IN (%s)" % (friends, friends))
               
    me = int(facebook.uid)
    F = Graph([me])  # Create a graph whose sole vertex is me
    H = Graph()

    # Problem: the FQL result on the next line only returns 5000 rows.
    # We need a limit of (|friends| choose 2).
    result = facebook.fql.query(mutuals)
    for row in result:
        u, v = map(int, row.values())
        H.addedge(u, v)
    
    G = F + H  # Let G be the join of graphs F & H. 
               # (This is the social graph.) 
    
    M = maximalindependentset(G)
    names = (row["name"] for row in facebook.users.getInfo(",".join(map(str, M)), "name"))
    
    for name in names:
        print name

if __name__ == '__main__':
    main()