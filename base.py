import webapp2

import foursquare
import os
import jinja2
import logging
import random
import time
import datetime
import urllib

import utils




from webapp2_extras import sessions
from google.appengine.api import memcache
import json
from config import CONFIG, DEFAULT_PREFS, BAD_CHARITIES, PREFS, DEF_CONTENT
from trivia_questions import tq
from model import UserInfo, TransactionData


def render_str(template, **params):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    
    
    # check if post session is current
#    def updated_post_session(self,name):
#        post = self.session.get('post')
#        if post and post['name'] == name:
#            return True
#        else:
#            return False
    
    # ## Don't know if we need these...
    @property
    def current_user(self):    
        if self.session.get("user"):
            # User is logged in 
            # Let's modify to get from model as well!
            logging.info('****Got User from Session!****')
            return self.session.get("user")
        else:
            return None
    
    def store_user(self, access_token, reset=False): #we might need something that 
        #=======================================================================
        # Function for storing user on first oauth. Oauth will check to see if 
        # user is in db, and if not, store them. This should happen ONLY once
        # so as not to overwrite set prefs! We'll use Memcache AND Session to 
        # Store! Update will update access token in all params! (??)
        #=======================================================================
        curr_client = utils.makeFoursquareClient(access_token)
        current_user = curr_client.users()
                
        if current_user:
            # Not an existing user so get user info
            # Store fs_id, token and prefs!
            profile = current_user['user']
            fs_id = profile["id"]
            
            existing_user_info = UserInfo.get_by_fs_id(fs_id)
            if existing_user_info and not reset:
                # User in DB we'll just update his/her access token!
                logging.info('*** There was an existing user with fs_id = {} ***'.format(fs_id))
                user = existing_user_info
                user.token = access_token
                prefs = json.loads(user.prefs)
                
                if not prefs.get('name'):
                    prefs['name'] = profile['firstName']
                    prefs['gender'] = profile['gender']
                    if not prefs.get('latlon'):
                        prefs['latlon'] = utils.get_latlon(current_user)
                    user.prefs = json.dumps(prefs)
            
            elif existing_user_info and reset:
                #user in db, but we want to reset to default prefs
                user = existing_user_info
                prefs = utils.make_default_prefs(curr_client,current_user)
                user.transactions = json.dumps([])
                user.prefs = json.dumps(prefs)
                user.token = access_token
                      
                
            else:
                logging.info('*** Creating a new user for fs_id = {} ***'.format(fs_id))
                user = UserInfo(fs_id = fs_id,
                                token = access_token)
                # store default prefs in user that can be reset later!
                prefs = utils.make_default_prefs(curr_client, current_user)
                
                
                user.transactions = json.dumps([])
                user.prefs = json.dumps(prefs)
                
            user.put() #make new user or update token of existing user!
            logging.info('****Added or updated User {} to DataBase!****'.format(user.fs_id))
            
            # Now store in Memcache and Session for later retrieval!
            udic = dict(fs_id = user.fs_id,
                        access_token = user.token,
                        gender=profile['gender'],
                        prefs = prefs)
            
            self.session["user"] = udic
            memcache.set('user_' + user.fs_id, udic)
            
        
        return self.session.get("user")
    
    def fetchUserInfo(self, user_id):
        ## *****Add attempt to get from session or memcache*****
        request = UserInfo.all().filter("fs_id = ", str(user_id))
        user = request.get()
        return user if user else None
    
    #===========================================================================
    # Functions for manipulating transactions!
    #===========================================================================
    def get_transaction(self, trans_id):
        #get a transaction from a trans_id or possibly fs_id
        pass
    
    def get_trans_data(self,trans_id):
        "gets TransactionData from model, existing or otherwise!"
        trans_data = TransactionData().all().filter("trans_id = ", trans_id).get()
        
        return trans_data
    
    def update_transaction(self, transaction, store_user = False, activate = False, elapse = 86400):
        "Activates or updates transaction to be ready for paying! "
        trans_id = transaction['trans_id']
        paid = transaction['transaction']['paid'] #False or Date
        wager = transaction['wager']

        now = time.time()
        
        if activate:
            activated = now
            due = now + elapse #due one day from now!
            transaction['due'] = due
            transaction['activated'] = activated    
        else:
            activated = transaction['activated']
            due = transaction['due']
        
        transaction['updated'] = now
        
        user_transaction = {'trans_id' : trans_id, 
                             'paid' : paid,
                             'amount' : wager,
                             'charity' : transaction['charity'],
                             'due' : due,
                             'activated' : activated}
        
        #get trans data from TransactionData model (existing or otherwise)!
        trans_data = self.get_trans_data(trans_id)
        
        if not trans_data:
            trans_data = TransactionData(trans_id = trans_id)
            
        
        trans_data.paid = paid
        trans_data.transaction = json.dumps(transaction)
        trans_data.put()
        
        if store_user:
            
            user = self.fetchUserInfo(transaction['fs_id'])
            
            transactions = self.update_user_transactions(user, user_transaction)
            user.transactions = json.dumps(transactions)
            user.put()
            
#             stored_user = self.fetchUserInfo(transaction['fs_id'])
#             logging.info("Here are my UNstored? transactions! " + user.transactions)
#             logging.info("Here are my stored transactions! " + stored_user.transactions)
            
        else:
            #trans is updated, return this for appending and put()-ing into db
            return user_transaction
    
    def update_user_transactions(self, user, user_transaction):
        if user.transactions:
            transactions = json.loads(user.transactions)
        else:
            transactions = []
        transactions.append(user_transaction)
        return transactions
    
    def five_only_transaction(self, transaction, update = False):
        "Updates transaction to a 5 dollar donation to OneNDun!"
        wager = 5
        
        transaction['transaction']['five_only'] = True
        transaction['wager'] = wager
        transaction['human_wager'] = utils.to_money(wager)
        
        if update:
            activate = False
            if not transaction['activated']:
                #Activate the transaction if it hasn't already been activated!
                activate = True
            
            self.update_transaction(transaction, activate = activate)
        
    def store_curr_transaction(self, transaction, db = False):
        self.session['trans'] = transaction
        memcache.set('trans_' + transaction['trans_id'], transaction)
        if db:
            user = self.fetchUserInfo(transaction['fs_id'])
            user.curr_transaction = json.dumps(transaction)
            user.put()
    
    def get_curr_transaction(self, trans_id, db = False):
        trans = self.session.get('trans') 
        if not trans:
            trans = memcache.get('trans_' + trans_id)
        return trans
    
    def update_curr_transaction(self, trans_id, q_winnings, db = False):
        transaction = self.get_curr_transaction(trans_id)
        
        self.store_curr_transaction(transaction, db = db)
       
    def logout(self):
        if self.current_user is not None:
            self.session['user'] = None

        
    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()
    


class TestHandler(BaseHandler):   
    def get(self):
        # # to be rendered from UserInfo
        # # poss add param of rank to tuples? To sort by most used?
        sets = ''
#         homenow = ''
#         setprefs = ''
        check_session = ''
        check_store_user = ''
        reset_user = ''
        logout_user = ''
        trivtest = ' '
        transtest = ''
        
        #this tests set-info page!
        if sets:
            user = self.session.get('user')
            content = {'its_a_bar' : True}
            prefs = user['prefs']
            content.update(prefs)
            self.render('set-info.html', **content)
        
        #Test trivia game page!
        elif trivtest:
            content = DEF_CONTENT
            
            #this happens when user checks in to home!
            transaction = utils.create_transaction(content)
            self.update_transaction(transaction, activate= True)
            self.store_curr_transaction(transaction, db= True)
            
            
            ## *** Will need to do this on before home-now post! ***
            content['trivia_url'] = transaction['trivia_url']
            content['trans_id'] = transaction['trans_id']
            
            self.render('home-now.html', **content)
        
        #Test transaction functions on real database!
        elif transtest:
            content = DEF_CONTENT
            user = self.fetchUserInfo(content['fs_id'])
            transaction = json.loads(user.transaction)
        
        #Logs out user so they can go through process again!
        elif logout_user:
            self.logout()
            self.write('You are logged out!<br><br><br>')
            self.write('Why not go <a href="/">HERE</a> now?')
        
        #Tests if Store User worked!
        elif check_store_user:
            access_token = '0T0ETAYAS3ZET51DJW01U1LFBSVMLF0BCJ3ONWINO3YVEWRX'
            udic = self.store_user(access_token)
            self.write('udic = <br><br>')
            self.write(udic)
            self.write('<br><br><br>')
            self.write('session_user = <br><br>')
            self.write(self.session.get('user'))
            self.write('<br><br><br>')
            self.write('memcached_user = <br><br>')
            self.write(memcache.get('user_' + udic['fs_id']))
            
        #resets a user's prefs
        elif reset_user:
            access_token = '0T0ETAYAS3ZET51DJW01U1LFBSVMLF0BCJ3ONWINO3YVEWRX'
            udic = self.store_user(access_token, reset=True)
            self.write('user reset!<br>')
            self.write('udic = <br><br>')
            self.write(udic)
            self.write('<br><br><br>')
            self.write('session_user = <br><br>')
            self.write(self.session.get('user'))
            self.write('<br><br><br>')
            self.write('memcached_user = <br><br>')
            self.write(memcache.get('user_' + udic['fs_id']))
        
        #compares session to user!
        elif check_session:
            #see what's in my session cookie!
            user = self.current_user
            
            user_info = UserInfo.all().filter('fs_id = ','4091108').get()
                        
            self.write('user = <br><br>')
            self.write(user)
            self.write('<br><br><br>')
            self.write('user_info.prefs = <br><br>')
            self.write(user_info.prefs)
           
#         elif homenow:
#             content = {"human_time": "4:55:50 PM",
#                        "human_wager": "$420",
#                        "charity_id": "23-90876",
#                        "pronoun": "he",
#                        "then": "1366836950018",
#                        "home_id": "4d60a5e4865a224bdd32ae85",
#                        "charity": "The Creation Museum",
#                        "its_a_bar": True,
#                        "made_it": "y",
#                        "home": "Waterphone Of Dreams (S&T's)",
#                        "name": "Scott",
#                        "now": "1366661436381",
#                        "wager": "420"}
#             
#             # right_now = time.time()
#             
#             
#             self.render('home-now.html', **content)
#         elif setprefs:
#             user = UserInfo()
#             user.fs_id = '4091108'
#             user.prefs = json.dumps({'homes' : [] , 'charities' : []})
#             user.token = "0T0ETAYAS3ZET51DJW01U1LFBSVMLF0BCJ3ONWINO3YVEWRX"
#             user.put()
#             
#             
#             self.write(user.fs_id)
        else:
            #self.logout() ##uncomment to debug! (ie set new prefs!)
            user = self.current_user
            
            #===================================================================
            # can put in an authed param to speed up the render!
            # 
            #===================================================================
            
            if not user:
                #udic = me! (for testing) Will update handling to create say['authed = false']
                udic = dict(name = 'Scott',
                            fs_id = '4091108',
                            access_token = "0T0ETAYAS3ZET51DJW01U1LFBSVMLF0BCJ3ONWINO3YVEWRX",
                            gender = 'male',
                            prefs = PREFS)
                self.session["user"] = udic
                logging.info("*** Set a User! ***")
                user = udic
            client_id = CONFIG['client_id']
            params = {'client_id': client_id}
            params['auth_url'] = utils.generateFoursquareAuthUri(client_id)
            params['site_name'] = CONFIG['site_name']
            params['description'] = CONFIG['site_description']
            params['fs_id'] = user['fs_id']
            params.update(user['prefs'])
            params['bad_charities'] = BAD_CHARITIES
            
            #This will be added and set to false if not self.current_user!
            params['authed'] = 'true'
            
            self.render('index.html', **params)
        
    def post(self):
        sets = ''
        setprefs = ' '
        
        
        if setprefs:
            homes = self.request.get_all('homes')
#             home = json.loads(homes)
#             test_obj = self.request.get('testobj')
#             test_obj = json.loads(test_obj)
            self.write(homes)
            
        
        elif sets:
            #sci = self.request.get('source_content_id')
    #         source_content_info = self.fetchContentInfo(sci)
            
            client = foursquare.Foursquare(access_token='0T0ETAYAS3ZET51DJW01U1LFBSVMLF0BCJ3ONWINO3YVEWRX')
            
            
            
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
            
            
            content = dict(wager=wager,
                           human_wager=human_wager,
                           now=now,
                           then=then,
                           human_time=human_time,
                           home=home,
                           charity=charity,
                           charity_id=charity_id,
                           home_id=home_id,
                           name=name,
                           pronoun=pronoun,
                           its_a_bar=True)
            
            content_dump = json.dumps(content)
    
            
            # item = json.loads(source_content_info.content)['item']
            message = '{name} needs to get to {home} by {human_time} or {human_wager} goes to {charity} a charity {pronoun} HATES!'.format(**content)
    #         self.makeContentInfo( checkin_json = checkin_json,
    #                               content = content_dump,
    #                               text = message,
    #                               post = True)
    
            # redirects back to foursquare after post!
            fsqCallback = self.request.get('fsqCallback')
            logging.debug('fsqCallback = %s' % fsqCallback)
            self.render('timer-post.html', **content)
            self.write(content_dump)
            self.write('_____________________________________')
            self.write('_____________________________________')
            self.write('_____________________________________')
            self.write(message)
        



            


#===============================================================================
# Handle processing of Trivia Questions!
#===============================================================================
class TriviaHandler(BaseHandler):
    def get(self):
        if self.request.path.startswith('/_trivia'):
            return self.tq_get()
        else:
            #===================================================================
            # to go away in favor of self.get_transaction(fs_id)
            #===================================================================
            trans_id = self.request.get('trans_id')
            transaction = self.get_curr_transaction(trans_id)
            wager_table = utils.gen_question_winnings(float(transaction['wager']))    
            self.render('trivia-game.html', wager_table = json.dumps(wager_table),  **transaction)
        
    
    def post(self):
        if self.request.path.startswith('/_trivia'):
            return self.tq_post()
        else:
            trans_id = self.request.get("trans_id")
            new_wager = float(self.request.get("curr_wager"))
            transaction = self.get_curr_transaction(trans_id)
            utils.trivia_update_trans(new_wager, transaction)
            self.store_curr_transaction(transaction)
            self.write(json.dumps(transaction))
        
    
    def tq_get(self):
        cats = tq.keys()
        cat = random.choice(cats)
        question = random.choice(tq[cat])
        
        answer_hash = utils.generateId(size=8)
        memcache.set('ans_' + answer_hash, question['a'])
        
        question['category'] = cat
        question['answer_hash'] = answer_hash
        
        self.render('trivia.html', **question)
        
    
    def tq_post(self):
        
        choice = self.request.get('choice')
        answer_hash = self.request.get('answer_hash')
        #question_winnings = self.request.get('question_winnings')
        #trans_id = self.request.get('trans_id')
        
        answer = memcache.get('ans_' + answer_hash)
        correct = choice == answer[0]
        
#         if correct:
#             self.update_curr_transaction(trans_id)
            
        
        answer_data = dict(choice = choice,
                           answer = answer,
                           correct = correct)
        
        self.write(json.dumps(answer_data))


#===============================================================================
# Handler for Paying... Move to one_n_dun!
#===============================================================================
class PayUpHandler(BaseHandler):     
    def get(self):
        trans_id = self.request.get('trans_id')
        transaction = self.get_curr_transaction(trans_id)
        #==================================================
        # Perhaps store in transaction initially?
        human_due = datetime.datetime.fromtimestamp(float(transaction['due'])).strftime('%A, %b %d at %I:%M %p')
        transaction['human_due'] = human_due
        #==================================================
        self.render('payup.html', **transaction)
        #self.write(transaction)

class AutoCompHomesHandler(BaseHandler):
    def get(self):
        logging.info("I'm at AutoCompHomes")
        term = self.request.get('term')
        latlon = self.request.get('latlon')
        client = utils.makeFoursquareClient("IQBCPBQ5U3CFQI4DZCL3IC3TAAZMZXRUPJBHI0ZTG4B4LDLL")
        res = utils.search_venue(client, term, latlon)
        data = json.dumps(res)
        self.write(data)
        

class PostPrefsHandler(BaseHandler):
    def get(self):
        
        #=======================================================================?
        # ** create dic, and then compare to session. If different, rewrite session
        # and UserInfo. If not, return session! Saves time if button was hit 
        # without updating! 
        #=======================================================================?
        fs_id = self.request.get('fs_id')
        
        access_token = self.request.get('access_token')
        
        if self.request.get('reset'):
            #reset to defaults... (possibly store these in UserInfo)
            
            self.store_user(access_token, reset=True)
        
        
        logging.info('*** fs_id = {} ***'.format(fs_id))
        homes = self.request.get_all('homes')
        charities = self.request.get_all('charities')
        latlon = self.request.get('latlon')
        home_prefs = []
        char_prefs = []
        
        robot_pref = self.request.get('robot_pref')
        
        user = UserInfo().all().filter('fs_id =', fs_id).get()
        #logging.info('*** user = {} ***'.format(user))
        prefs = json.loads(user.prefs)
        prefs['latlon'] = latlon # for debuggin, shouldn't need to change this...
        
        if homes:
            for home in homes:
                h_tup = home.split('|||')
                home_prefs.append(h_tup)
            
            prefs['homes'] = home_prefs
        
        if charities:
            for charity in charities:
                c_tup = charity.split('|||')
                
                char_prefs.append(c_tup)
            prefs['charities'] = char_prefs
        
        if robot_pref:
            friends = self.request.get('friends')
            if robot_pref == 'robot':
                #here we add a function to friend the robot if not already friends!
                
                if friends == 'no':
                    
                    friend = utils.friend_the_robot(access_token, fs_id)
                    #returns True or False if the friending worked!
                    if friend:
                        prefs['friends_with_ond'] = 'yes'
                
                prefs['robot_posts'] = True
            
            else:
                prefs['robot_posts'] = False
        
        udic = self.session.get('user')
        udic['prefs'] = prefs
        
        #Store 3-ways!
        self.session['user'] = udic
        memcache.set('user_' + fs_id, udic)
        
        pref_dump = json.dumps(prefs)
        
        user.prefs = pref_dump
        user.put()
        
        self.write(pref_dump)
            
        
#===============================================================================
# No longer Necessary
#===============================================================================
class AuthedHandler(BaseHandler):
    def get(self):
        logging.info('**JUST HIT AUTHED PAGE!**')
        user = self.current_user
        if user:
            logging.info('**USER FOUND! REDIRECTING TO RENDER**')
            self.redirect('/render')
        else:
            code = self.request.get('code')
            logging.info('**CODE FOUND! IT\'S THIS {}!**'.format(code))
            if code:
                access_token = self.get_access_token(code)
                self.store_user(access_token)
                logging.info('**USER STORED! REDIRECTING TO RENDER**')
                self.redirect('/render')
            else:
                self.login()
                
#===============================================================================
# Don't need anymore!
#===============================================================================
class DataRender(BaseHandler):
    def get(self):
        userdic = self.current_user
        if userdic:
            self.render('foursquare-test2.html', **userdic)
        else:
            self.write('sorry')        
        
        
        
        
        
