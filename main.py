#!/usr/bin/python


from oauth import OAuth, ProcessCheckin, IsAuthd, HomePage
from config import CONFIG
from one_n_dun import OneNDunHandler
from base import TestHandler, AutoCompHomesHandler, PostPrefsHandler, TriviaHandler, PayUpHandler

import webapp2 as webapp


app = webapp.WSGIApplication([('/oauth.*', OAuth),
                              ('/checkin', ProcessCheckin),
                              ('/isAuthd', IsAuthd),
                              ('/test', TestHandler),
                              ('/autocomp_homes', AutoCompHomesHandler),
                              ('/post_prefs', PostPrefsHandler),
                              ('/trivia', TriviaHandler),
                              ('/payup', PayUpHandler),
                              ('/', HomePage),
                              ('/_trivia', TriviaHandler),
                              ('/_checkin', OneNDunHandler),
                              ('/_warnings', OneNDunHandler),
                              ('/.*', OneNDunHandler)],
                               debug=CONFIG['debug'],
                               config=CONFIG['config'])


