#!/usr/bin/env python

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

def main():
    facebook = facebook_init()

    friends = "SELECT uid2 FROM friend WHERE uid1=%s" % (facebook.uid)
    mutuals = "SELECT uid1, uid2 FROM friend WHERE uid1 IN (%s) AND uid2 IN (%s)" % (friends, friends)

    g = Graph()

    result = facebook.fql.query(mutuals)
    for row in result:
        u, v = row.values()
        g.addedge(u, v)
    
    print 'formed graph'

if __name__ == '__main__':
    main()