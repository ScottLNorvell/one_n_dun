# Don't import anything that imports CONFIG here, the circular dependency will not work.
# Instead, import after the definition of CONFIG.

import datetime
import time
import random

CONFIG = {
  # foursquare server to use. You probably don't need to change this.
  'foursquare_server':'https://foursquare.com',
  # The server name for local_dev mode. Make sure the port matches what you use.
  'local_server': 'http://localhost:9088',
  # Server name for your deployed AppEngine instance
  'prod_server': "http://one-n-dun.appspot.com",
  # OAuth client ID. Must match what you set at https://foursquare.com/oauth.
  'client_id': "EPCSOMXHJI20AOHXENO05VXGOPHZXKHUOC3YD3YKWUIY0TUF",
  # OAuth callback/redirect URI. Must match what you set at https://foursquare.com/oauth.
  'redirect_uri': '%s/oauth', # (server)
  # Format string to serve URL content out of. Not necessarily required.
  'content_uri': '%s/content?content_id=%s', # (server, content_id)
  # The foursquare API version string to pass. See: https://developer.foursquare.com/overview/versioning
  'api_version': '20120609',
  # A name for the hompage and titles.
  'site_name': "One 'n' Dun!",
  # A description for the home page
  'site_description': 'Have enough fun to not hate yourself tomorrow. One \'n\' Dun can help you get home at a reasonable hour by wagering money to a charity you <em>HATE</em>!',
  # If true, we use local_server, and log actions instead of POSTing to foursquare
  # Be sure to set this to false when you actually want to deploy.
  'local_dev': False,
  # This allows silly things like friending the robot. Possibly won't use this, but oh well!
  'in_beta' : True,
  # AppEngine debug mode
  'debug': True,
  # These can either be a path (on this server), or an external URI
  'auth_success_uri_desktop': '/', ## *** Decide what i want these to do! How to handle my flow! ***
  'auth_success_uri_mobile': '/',
  'auth_denied_uri': '/',
  # Application Level Configuration
  # Feel free to add new config parameters here...
  # This is my config for session cookies!
  'oneNDun_uid':'55114339',
  'oneNDun_token': 'EC1L5RN5VBYQIYPLGA4E05A2CLW41ATM4OK2ZD3OYADLB2AP',
  'config' : {'webapp2_extras.sessions' : dict(secret_key='foursquizzy_tizzy_91')}
}

## Here we will store all of my messages for rendering posts/replies so that we can edit them all at once!
MSG = {
        ## list of messages for bar checkins/posts!
        'bar_rpl' : ['You\'re checking in to the {} on a school night? This could be a disaster... One \'n\' Dun to the rescue! We can help you have plenty of fun without the regrets'],
        'bar_pst' : ['{name} needs to get to {home} by {human_time} or {human_wager} goes to {charity} a charity {pronoun} HATES!'],
        ## list of messages for home checkins!
        'home_madeit_rpl' : ['Congratulations {name}! You made it to {home} by {human_time}. Now you get to keep your {human_wager}! Screw those guys at {charity}!'],
        'home_fail_rpl' : ['You didn\'t make it to {home} by {human_time}. Now your hard-earned {human_wager} will go to {charity}! Click here to confirm.'],
        'home_madeit_pst' : ['Congratulations {name}! You made it to {home} by {human_time}. Now you get to keep your {human_wager}! Screw those guys at {charity}!'],
        'home_fail_pst' : ['Sorry {name}! You didn\'t make it to {home} by {human_time}. Now your hard-earned {human_wager} will go to {charity}!'],
        ## warning messages
        'w1' : ['You have {mins} minutes to get home!'], #will get more creative with these! Add charity and wager! "oh no, you must really hate money!"
        'w2' : ['You have {mins} minutes to get home!'],
        'w3' : ['You have {mins} minutes to get home!'], #get home safely, etc... Why aren't you home yet?
        'w4' : ['You should be home now! If you aren\'t, kiss your {} goodbye!'],
        ## Other Messages stored here!
        ## For testing purposes!
        'home_shame_pst' : [], ## Used for shaming people if they renegged
        'nobar_rpl' : ["You are not at a bar! If you were, One 'n' Dun could help!"]
        }

# the default prefs to build upon!
DEFAULT_PREFS = {"homes" : None,
                 "charities" : [(u"The Creation Museum", u'2HD60JJT'),
                                (u'Planned Parenthood', u'CUCO6QTR'),
                                (u'P.E.T.A.', u'KFFPA3WC'),
                                (u'The Church of Scientology', u'4PUZXV9X'),
                                (u'The Imus Ranch' , u'NGWPM60B' )],
                 "latlon" : None,
                 "robot_posts" : False, #set to False so that setting to True friends the robot in beta!
                 "friends_with_ond" : "no", #To avoid duplicate posts
                 "name" : None,
                 "gender" : None} 

BAD_CHARITIES = [{"name" : "The Creation Museum",
                  "description" : """What's better than creationism? An interactive 3D walk-through presentation of creationism! Prepare to believe...""" ,
                  "cid" : '2HD60JJT'},
                 {"name" : "Planned Parenthood",
                  "description" : """Help support the scientists who invented abortion.""" ,
                  "cid" : 'CUCO6QTR'},
                 {"name" : "P.E.T.A.",
                  "description" : """Do you like meat? Then you'd <em>HATE</em> for your hard-earned cash to go to these clowns!""" ,
                  "cid" : 'KFFPA3WC'},
                 {"name" : "Church of Scientology",
                  "description" : """It's hard out here for a body thetan. Death to Lord Xenu and his evil ways!""" ,
                  "cid" : '4PUZXV9X'},
                 {"name" : "The Imus Ranch",
                  "description" : """Use your donation to teach kids with cancer how to rope cattle... and be racist.""" ,
                  "cid" : 'NGWPM60B'},
                 {"name" : "Westboro Baptist Church",
                  "description" : """God <em>HATE</em>s Fags! (and probably you as well)... Help spread the word with your donation!""" ,
                  "cid" : 'IDA015BF'},
                 {"name" : "1-877-Kars4Kids",
                  "description" : """...K-A-R-S Kars fer Kids... Anyone who could create a song like that <em>HAS</em> to be evil, right? It's stuck in your head now. Sorry...""" ,
                  "cid" : 'NY24YN4D'},
                 {"name" : "Boy Scouts of America",
                  "description" : "Teaching young boys important life skills... provided they are heterosexual.",
                  "cid" : 'U1816FTB'},
                 {"name" : "The Oprah Winfrey Leadership Academy for Girls",
                  "description" : """Help Oprah help Africa's poor and needy... one yoga studio at a time.""" ,
                  "cid" : 'MLNBW9UA'},
                 {"name" : "Answers in Genesis",
                  "description" : """The earth isn't as <em>OLD</em> as we thought! Science is just something we made up at the bar one night!! Spread the word through your donation!!""" ,
                  "cid" : '65RXDLGX'},
                 {"name" : "The Heartland Institute",
                  "description" : """With a lot of money, you can make even the hardest scientific evidence go away. Why not give The Heartland Institute some today?""" ,
                  "cid" : '8GWS6IPS'},
                 {"name" : "Conservapedia",
                  "description" : """Promoted to homeschoolers and their parents, Conservapedia is a great place to get the wrong answer to just about anything!""" ,
                  "cid" : 'URP1KANL'},
                 {"name" : "The Richard Dawkins Foundation for Reason and Science",
                  "description" : """Your donation will help everyone <em>HATE</em> god. Just like Richard Dawkins!""" ,
                  "cid" : 'B71URKR2'},
                 {"name" : "NaturalNews.com",
                  "description" : """Help Mike "the Health Ranger" Adams wrangle the virtual flora and fauna of the Health Jungle...""" ,
                  "cid" : 'FA2ZFWEO'}]

## For testing purposes
PREFS = {"homes" : [(u"Waterphone Of Dreams (S&T's)", u'4d60a5e4865a224bdd32ae85'),
                    (u'You Did It!!!', u'50e101c1e4b0b93eead6962a'),
                    (u'Gracie Mansion East', u'4f3dc185e4b0248b50e697ac')],
         "charities" : [(u"The Creation Museum", u'23-90876'),
                        (u'Planned Parenthood', u'33-09857'),
                        (u'P.E.T.A.', u'44-09875'),
                        (u'The Imus Ranch' , u'44-09995' )],
         "latlon" : '40.7508390901,-73.9183463601',
         "robot_posts" : True}

#vars for testing!
then = time.time() - 3600
human_time = datetime.datetime.fromtimestamp(then).strftime('%I:%M %p')

DEF_CONTENT = {"charity" : random.choice(BAD_CHARITIES)['name'],
               "name" : "Scott",
               "human_time" : human_time,
               "then" : then,
               "wager" : 150,
               "human_wager" : "$150",
               "made_it" : False,
               "pronoun" : "he",
               "fs_id" : 4091108 }

