import itertools
import random
import string
import urllib
import time
try: import simplejson as json
except ImportError: import json
#import logging
import re


import foursquare

from config import CONFIG, DEFAULT_PREFS
# Does this import fail for you? Fill out foursquare_secrets_template.py, and move it to foursquare_secrets.
from foursquare_secrets import SECRETS

#===============================================================================
# Utils for HomePage etc
#===============================================================================
def getServer():
    if CONFIG['local_dev']:
        return CONFIG['local_server']
    else:
        return CONFIG['prod_server']

def generateContentUrl(content_id):
    return CONFIG['content_uri'] % (getServer(), content_id)


def generateRedirectUri():
    return CONFIG['redirect_uri'] % getServer()


def generateFoursquareAuthUri(client_id):
    redirect_uri = generateRedirectUri()
    server = CONFIG['foursquare_server']
    url = '%s/oauth2/authenticate?client_id=%s&response_type=code&redirect_uri=%s'
    return url % (server, client_id, urllib.quote(redirect_uri))


def makeFoursquareClient(access_token=None):
    redirect_uri = generateRedirectUri()
    return foursquare.Foursquare(client_id = CONFIG['client_id'],
                                 client_secret = SECRETS['client_secret'],
                                 access_token = access_token,
                                 redirect_uri = redirect_uri,
                                 version = CONFIG['api_version'])
    
def makeFoursquareClient2(access_token):
    return foursquare.Foursquare(access_token = access_token)

def generateId(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def fetchJson(url):
    """Does a GET to the specified URL and returns a dict representing its reply."""
#    logging.info('fetching url: ' + url)
    result = urllib.urlopen(url).read()
#    logging.info('got back: ' + result)
    return json.loads(result)

def isMobileUserAgent(user_agent):
    """Returns True if the argument is a User-Agent string for a mobile device.

    Includes iPhone, iPad, Android, and BlackBerry.
    """
    # Split on spaces and "/"s in user agent.
    tokens = itertools.chain.from_iterable([item.split("/") for item in user_agent.split()])
    return "Mobile" in tokens


def wheres_home(client):
    venues = client.users.venuehistory()['venues']['items']
    home_re = re.compile(r'Assisted Living|Home \(private\)|Housing Development|Residential Building')

    homes = []
    for ven in venues:
        venue = ven['venue']
        try:
            category = venue['categories'][0]['name']
        except:
            continue
        if home_re.search(category):
            home_data = (venue['name'],venue['id'])
            if home_data not in homes:
                homes.append(home_data)
    return homes

def make_default_prefs(client,user):
    #===========================================================================
    # This will make default prefs for a given user!
    #===========================================================================
    profile = user['user']
    prefs = DEFAULT_PREFS
    prefs['homes'] = wheres_home(client)
    prefs['latlon'] = get_latlon(user)
    prefs['name'] = profile['firstName']
    prefs['gender'] = profile['gender']
    return prefs

def search_venue(client,query,latlon,n=5):
    results = client.venues.search(params=dict(query = query,
                                               ll = latlon,
                                               limit = n + n))
    been_here = []
    never_here = []
    for venue in results.get('venues'):
        res_dat = {'venue':venue['name'],
                   'venue_id':venue['id'],
                   'been_here': False}
        try:
            been_here_count = venue.get("beenHere").get('count')
        except:
            been_here_count = 0
        if been_here_count > 0:
            res_dat['been_here'] = True
            been_here.append(res_dat)
        else:
            never_here.append(res_dat)
    final_results = been_here + never_here
    return final_results[0:n]

def get_latlon(user): # a fs_user object ret from client.users()
    location = user['user']['checkins']['items'][0]['venue']['location']
    latlon = ','.join([str(location['lat']), str(location['lng'])])
    return latlon


def friend_the_robot(access_token,fs_id):
    client = makeFoursquareClient(access_token)
    one_n_dun = makeFoursquareClient(CONFIG['oneNDun_token'])
    ond_id = CONFIG['oneNDun_uid']
    try:
        client.users.request(ond_id)
        one_n_dun.users.approve(fs_id)
    except:
        return False
    return True
    


#===============================================================================
# Utils for Trivia and Transactions!
#===============================================================================

#for generating human_wager
def to_money(flt):
    if isinstance(flt,int):
        return '${}'.format(flt)
    return '${0:.2f}'.format(flt)

#Make a wagertable for Trivia game!
def gen_question_winnings(wager):
    percent_table = [0.03, 0.06, 0.1, 0.2, 0.15, 0.07, 0.04, 0.25, 0.05, 0.03, 0.02]
    wager_table = []
    new_wager = wager-5
    for percent in percent_table:
        chunk = new_wager * percent
        wager_table.append((chunk,to_money(chunk)))
    return wager_table

#makes a transaction! ****Poss move to BaseHandler?****
def create_transaction(content):
    wager = content['wager']
    human_wager = content['human_wager']
    charity = content['charity']
    created = time.time()
    trans_id = generateId()
    trivia_url = '/trivia?' + urllib.urlencode({'trans_id' : trans_id})
    transaction = dict(trans_id = trans_id,
                       fs_id = content['fs_id'],
                       original_wager = wager,
                       wager = wager, #update with new wager?
                       human_wager = human_wager,
                       charity = charity,
                       due = False,
                       transaction = dict( paid = False,
                                           five_only = False,
                                           receipt = ''),
                       trivia = dict( played = 0,
                                      wager_progress = [[wager,created]]),
                       trivia_url = trivia_url,               
                       created = created,
                       activated = False, #or Date! 
                       updated = created)
    return transaction
   
#For updating after a trivia game!
def trivia_update_trans(new_wager, transaction):
    "Updates transaction after trivia game"
    now = time.time()
    triv_data = [new_wager,now]
    transaction['updated'] = now
    transaction['trivia']['wager_progress'].append(triv_data)
    transaction['trivia']['played'] += 1
    transaction['wager'] = new_wager
    transaction['human_wager'] = to_money(new_wager)


#===============================================================================
# Utils we don't really use!
#===============================================================================
def search_venue_naked(client,query,near):
    results = client.venues.search(params=dict(query = query,
                                               near = near))
    posses = []
    for venue in results.get('venues'):
        posses.append(venue['name'])
    return posses

def search_venue2(client,query,near):
    results = client.venues.search(params=dict(query = query,
                                               near = near))
    posses = []
    for venue in results.get('venues'):
        posses.append((venue['name'] , venue['id']))
    return posses

def search_venue_ll(client,query,lat,lon):
    latlon = str(lat) + ',' + str(lon)
    results = client.venues.search(params=dict(query = query,
                                               ll = latlon))
    posses = []
    for venue in results.get('venues'):
        posses.append((venue['name'] , venue['id']))
    return posses
