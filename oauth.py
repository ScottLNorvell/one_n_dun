# import Cookie
# import email.utils
import logging
# import os
# import time
try: import simplejson as json
except ImportError: import json

from foursquare import InvalidAuth

from foursquare_secrets import SECRETS
from model import UserInfo
import utils

from google.appengine.api import taskqueue



from base import BaseHandler
from config import CONFIG, BAD_CHARITIES



##################################################
## Error Classes for OAuth Handler
##################################################
class OAuthConnectErrorException(Exception):
    pass

class OAuthConnectDeniedException(Exception):
    pass


##################################################
## OAuth Handler 
##
## ***We should add pref rendering here!*** 
## (from get_homes functions)
##################################################
class OAuth(BaseHandler):
    """Handle the OAuth redirect back to the service."""
    def post(self):
        logging.info('*** We\'re at the OAuth post() place... ***')
        self.get()

    ##################################################
    ## Let's take a look at this and figure out how to
    ## modify the auth process to back to my site!
    ##################################################
    def get(self):
        logging.info('*** We\'re at the OAuth get() place... ***')
        ##################################################
        ## This raises errors if the request fucked up!
        ##################################################
        try:
            error = self.request.get('error')
            if error == "access_denied":
                raise OAuthConnectDeniedException
            elif error:
                raise OAuthConnectErrorException

            ## Parses code if it exists... Don't change!
            code = self.request.get('code')
            logging.info('*** Code = {} ***'.format(code))
            if not code:
                raise OAuthConnectErrorException

            client = utils.makeFoursquareClient()
            access_token = client.oauth.get_token(code)
            logging.info('*** Access Token = {} ***'.format(access_token))
            if not access_token:
                logging.info('*** this didnt work, no access token! ***')
                raise OAuthConnectErrorException
            client.set_access_token(access_token)
        
        ## Useful handling for different types of errors.
        except OAuthConnectDeniedException:
            self.redirect(CONFIG['auth_denied_uri']) ## where?
            return
        except OAuthConnectErrorException:
            self.render('connect_error.html', name = CONFIG['site_name'])
            return
        
        #=======================================================================
        # Store or update the user in memcache, session, AND Database!
        #=======================================================================
        
        self.store_user(access_token) 
        
        ## Comment out untill we get a mobile url?
        #isMobile = utils.isMobileUserAgent(self.request.headers['User-Agent'])
        redirect_uri = CONFIG['auth_success_uri_desktop']
        logging.info('*** redirect_uri = {} ***'.format(redirect_uri))
        ## This will be where the main page renders!
        self.redirect(redirect_uri)

#===============================================================================
# Depreciated! We can delete this obselete bit of nothingness!
#===============================================================================

class IsAuthd(BaseHandler):
    """Returns whether or not a user has connected their foursquare account"""
    def get(self):
        ##################################################
        ## Clean up to use Sessions and not this Cookie
        ## Shit!!! Basicly write True or False depending
        ## on if we're authed... Maybe we don't need?
        ##################################################
        user = self.current_user
        is_authd = 'false'
        if user:
            client = utils.makeFoursquareClient(user['access_token'])
            try:
                client.users()
                is_authd = 'true'
            except InvalidAuth:
                self.logout()
        logging.info('*** is_authd = {} ***'.format(is_authd))

        self.write(is_authd)


class ProcessCheckin(BaseHandler):
    PREFIX = "/checkin"

    def post(self):
        # Validate against our push secret if we're not in local_dev mode.
        if (self.request.get('secret') != SECRETS['push_secret'] and not CONFIG['local_dev']):
            self.error = 403
            return
        checkin_json = json.loads(self.request.get('checkin'),
                                  parse_float=str)
        if 'venue' not in checkin_json:
                # stupid shouts. skip everything
                return
        logging.debug('received checkin ' + checkin_json['id'])
        taskqueue.add(url='/_checkin',
                      params={'checkin': self.request.get('checkin')})


class HomePage(BaseHandler):
    ##################################################
    ## This is SUPER generic... We can do better!
    ##################################################
    def get(self):
        client_id = CONFIG['client_id']
        params = {'client_id': client_id} #not sure I have to push client id to index... we'll see!
        params['auth_url'] = utils.generateFoursquareAuthUri(client_id)
        params['site_name'] = CONFIG['site_name']
        params['description'] = CONFIG['site_description']
        params['bad_charities'] = BAD_CHARITIES
        
        user = self.current_user
        
        if user:
            params['fs_id'] = user['fs_id']
            params['access_token'] = user['access_token']
            params.update(user['prefs'])
            
            
            params['authed'] = 'true'
        else:
            params['authed'] = 'false'
        
        
        ## Refactor to self.render
        self.render('index.html', **params)
#         path = os.path.join(os.path.dirname(__file__),
#                             'templates/index.html')
#         self.response.out.write(template.render(path, params))