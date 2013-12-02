import logging
# import os
import re
import random
from config import MSG, PREFS
from google.appengine.api import memcache
# import jinja2
# from google.appengine.ext.webapp import template

try: import simplejson as json
except ImportError: import json

from abstract_app import AbstractApp
import utils



#===============================================================================
# This is where the magic happens in my app!
#===============================================================================
class OneNDunHandler(AbstractApp):
    
    ##################################################
    ## Endpoint for rendering templates if we get here
    ## from a post or reply. If from reply, we will
    ## set a timer, via the template! If post, We will
    ## render the posted template!
    ##################################################
    
    def contentGet(self, client, content_info):
        ## content_info is from the database. SOOOO we can pull homes, charities, etc from here?
        ## Each content db entry will be diff, so we can add error handling for home/bar replies
        ## ...
        
        content_json = json.loads(content_info.content)
        fsqCallback = self.request.get('fsqCallback')
        
        # when we follow link from the app's reply
        if content_info.reply_id:
            # in this case, content_json got handed to us from checkin
            content_json["content_id"] = content_info.content_id
            content_json["fsqCallback"] = fsqCallback
            if content_json.get('its_a_bar'):
                logging.info('*** This is a bar! ***')
                self.render('set-info.html', **content_json) ## *** homes and charities in content_json! ***
                
                
            else:
                ## Need ALL content, so that we can post it on OKAY button...
                ## currently we are NOT set up to post ANYTHING and that's OKAY for now!
                self.render('home-now.html', **content_json) ## content json has posted data AND madeit = 'y' or ''
                 
            return
        
        # when we follow link from post reply...
        if content_info.post_id:
            # Here content json will include EVERYTHING we need to render post string. AND the timer!
            # Here content_json was handed to us from appPost
            if content_json.get('its_a_bar'):
                logging.debug('** We\'re at timer-post! it worked! **')
            
                self.render('timer-post.html', **content_json)
            
            else:
                #this link to be followed if user clicks "okay" to posted link... (poss an ajax post... and some functionality about making it or not...)
                logging.debug('** timer-post, should have been home-post! **') 
                self.render('timer-post.html', **content_json)
            
    
    ##################################################
    ## This will handle posting to someone's checkin!
    ## Something "like Mike pledged $50 to be home by
    ## midnight!" Also a link to buy Mike out!
    ##################################################
    def appPost(self, client): ## Change this to appBarPost and add an appHomePost for home?
        ## ID for looking up content info from db (added to post url)
        sci = self.request.get('source_content_id')
        ## info that was stored on reply. We can store its_a_bar = True or False or it's home
        source_content_info = self.fetchContentInfo(sci)
        fs_id = source_content_info.fs_id
        
        user_info = self.fetchUserInfo(fs_id)
        access_token = user_info.token
        
        client.set_access_token(access_token)
        checkin_json = client.checkins(source_content_info.checkin_id)['checkin']
        
        
        now = self.request.get('now')
        then = self.request.get('then')
        human_time = self.request.get('human_time')
        charity = self.request.get('charity')
        charity_id = self.request.get('charity_id')
        wager = self.request.get('wager')
        human_wager = self.request.get('human_wager')
        home = self.request.get('home')
        home_id = self.request.get('home_id')
        
        user = client.users()['user']
        name = user['firstName']
        gender = user['gender']
        if gender == 'male':
            pronoun = 'he'
        else:
            pronoun = 'she'
        
        
        content = dict(wager = wager,
                       fs_id = fs_id,
                       human_wager = human_wager,
                       now = now, #poss to delete?
                       then = then,
                       human_time = human_time,
                       home = home,
                       charity = charity,
                       charity_id = charity_id,
                       home_id = home_id,
                       name = name,
                       pronoun = pronoun)
        
        
        
        fsqCallback = self.request.get('fsqCallback')
        logging.debug('fsqCallback = %s' % fsqCallback)
        
        ## Here we are going to see if this came from a bar or Home
        bar_check_json = json.loads(source_content_info.content)
        if not bar_check_json.get('its_a_bar'):
            content['made_it'] = self.request.get('made_it')
            content['fsqCallback'] = fsqCallback
            ## Currently this won't happen because we aren't posting anything from the home-now page!
            return self.appHomePost(client, checkin_json, content)
        else:
            content['its_a_bar'] = True
        
        content_dump = json.dumps(content)
        
        #=======================================================================
        # Here we make some transactions and put() them to user_info! 
        transaction = utils.create_transaction(content)
        self.store_curr_transaction(transaction)
        
        trans_id = transaction['trans_id']
        
        content['trans_id'] = trans_id
        #
        #=======================================================================
        
        content_dump = json.dumps(content)
        
        ## Set vals in user_info! We can retrieve them when user checks back in!
        
        user_info.curr_transaction = json.dumps(transaction)
        user_info.curr_home = home_id
        user_info.then = then
        user_info.content = content_dump
        user_info.put()

        
        #item = json.loads(source_content_info.content)['item']
        message = random.choice(MSG['bar_pst']).format(**content)
        
        #change to content_info = , and use content_info.content_id to pass content_id to setWarnings!
        content_info = self.makeContentInfo( checkin_json = checkin_json, 
                                             content = content_dump,
                                             text = message,
                                             post = True)
        
        
        
        #=======================================================================
        # This will gen reminders if user has authorized them!
        #
        let_the_robot_post = self.request.get('robot_pref') # string or empty strig
        if let_the_robot_post: 
            #Let the Robot Post!
                    
            content['content_id'] = content_info.content_id
            content['access_token'] = access_token
            content['checkin_id'] = checkin_json['id']
            
            self.setWarnings(then, content) 
        # 
        #=======================================================================
        

        # redirects back to foursquare after post!
        self.redirect(str(fsqCallback))
                
    def appHomePost(self, client, checkin_json, content):
        "This will make handle ShamePosts!"
        content['its_home'] = True
        
        content_dump = json.dumps(content)
        
        if content.get('made_it') == 'y':
            message = random.choice(MSG['home_madeit_pst']).format(**content)
        else:
            message = random.choice(MSG['home_fail_pst']).format(**content)
            
        
        
        self.makeContentInfo( checkin_json = checkin_json,
                              content = content_dump,
                              text = message,
                              post = True)
        
        
        
        ## Redirect unnecessary if we post via ajax...
        self.redirect(content['fsqCallback'])
    
    ##################################################
    ## Content has come in and it's a push checkin!
    ## This will parse and handle it!
    ## 
    ## This will process if the checkin is from "Home" 
    ## -or- a bar! (do nothing if not!)
    ##################################################
    def checkinTaskQueue(self, client, checkin_json):
        ## This is where we parse the code from the Checkin Json!
        
        #=======================================================================
        # Can make this faster!!
        # store prefs in memcache?
        # session?
        # ***self.store_user puts udic in memchache by "user_" + fs_id***
        # * pull latlon from checkin_json and add to content and DB for rendering set-info.html
        # * if user.curr_home, and user.curr_home != venue_id, add reply taunt...
        #=======================================================================
        
        
        user_id = checkin_json['user']['id']
        user = self.fetchUserInfo(user_id) # *** add a memcache query here? ***
        venue_id = checkin_json['venue']['id']
        
        
        its_home = False #a function will determine this 
        its_a_bar = False 
        
        if user.curr_home == venue_id:
            its_home = True
            then = user.then
        
        if not its_home:
            # if it's not home, check to see if its a bar
            venue_json = client.venues(venue_id)['venue']
            categories = venue_json['categories']
            
            
            barword = 'Bar'
            
            for category in categories:
                name = category.get('name')
                bar_re = re.compile(r'Bar|Beer Garden|Lounge|Brewery|Gastropub|Pub|Speakeasy|Strip Club|Wine')
                if bar_re.search(name):
                    its_a_bar = True
                    barword = name
                    break
        
        content = {"fs_id" : user_id}       
        if its_a_bar:
            ## A function for determining diff messages for different times...
            message = random.choice(MSG['bar_rpl']).format(barword)
            latlon = self.get_latlon_checkin(checkin_json)
            content['its_a_bar'] = True
            
            
            ## For Now. 
            if user.prefs:
                prefs = json.loads(user.prefs)
            else:
                prefs = PREFS
            #logging.info('prefs = ', prefs)
            ## Eventually
            # prefs = json.loads(user.prefs) # we can even create more prefs!
            
            content.update(prefs)
            content['latlon'] = latlon
            #logging.info('content = ', content)
            
        elif its_home:
            # This contentInfo posts to home-now.html
            now = checkin_json['createdAt']
            made_it = self.madeItHome(now,then)
            content = json.loads(user.content)
            
            content['its_a_bar'] = False
            if made_it:
                message = random.choice(MSG['home_madeit_rpl']).format(**content)
                content['made_it'] = 'y'
                ## We'll add charity, wager and date info to user.transactions at this time
                # transactions = json.loads(user.transactions)
                # transactions.append( - THE RELEVANT INFO - ) --- charity, wager, date... (maybe auth info)
                # user.transactions = json.dumps(transactions)
            else:
                message = random.choice(MSG['home_fail_pst']).format(**content)
                
                #===============================================================
                # Here we manipulate the transaction
                #===============================================================
                transaction = json.loads(user.curr_transaction)
                user_transaction = self.update_transaction(transaction, activate = True)
                
                transactions = self.update_user_transactions(user, user_transaction)
                user.transactions = json.dumps(transactions)
                content['made_it'] = ''
                content['trivia_url'] = transaction['trivia_url']
                
            #===================================================================
            # This seems to be the only time we need to put() the user. Maybe
            # todo, we could call fetch_user_info (user db) here and try to use
            # memcache any other time...
            #===================================================================
            
            ## Clears values of home and then so that we don't post every time we check in
            user.curr_home = ''
            user.then = ''
            user.put()
        else:
            ## this will eventually return if we aren't at home or a bar
            ## ie: message = None
            
            message = random.choice(MSG['nobar_rpl'])
            content['its_a_bar'] = True #for now (testing purposes...) that way we can ond all the time!
            ## For Now
            if user.prefs:
                prefs = json.loads(user.prefs)
            else:
                prefs = PREFS
            
            ## Eventually
            # prefs = json.loads(user.prefs) # we can even create more prefs!
            
            content.update(prefs)
            content['latlon'] = self.get_latlon_checkin(checkin_json)
            
        
        if message:
            #===================================================================
            # puts content in the db and posts a reply to the checkin!
            #===================================================================
            self.makeContentInfo( checkin_json = checkin_json,
                                  content = json.dumps(content),
                                  text = message,
                                  reply = True )
        
    def warningTaskQueue(self, client, content):
        #=======================================================================
        # Eventually we'll have a way to tell if you've made it home or not...
        #=======================================================================
        
        checkin_id = content['checkin_id']

        # possibly abandoned in favor of robotComment? also we'd never hit this page if robot comment pref wasn't set!
        #=============================================================================        
        #content_id = content['content_id']
        #url = self.generateContentUrl(content_id)
        

#         params = {'contentId' : content_id,
#                   'url' : url,
#                   'text' : content['message']}
#         client.checkins.addpost(checkin_id, params)
        #=============================================================================
        
        
        # Adds robot Posts!
        #=============================================================================
        lcid = memcache.get('lcid_' + checkin_id)
        
        delete = True
        
        if content['first']:
            delete = False
        
        try:
            comId = self.addRobotComment(checkin_id, content['message'], lcid, delete)
            
            memcache.set('lcid_' + checkin_id, comId)
        
        except:
            #===================================================================
            # Here we would error handle. If user has defriended OneNdun, reset
            # User prefs to no-Robot warnings.
            #===================================================================
            logging.error('*** Couldn\'t Robot Post! ***')
            return
        #=============================================================================
        
        logging.debug("*** Made a robot post with comment_id {} ***".format(comId))
        
        
        return
