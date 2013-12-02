import logging
try: import simplejson as json
except ImportError: import json

import datetime
import time
import random
import re

from base import BaseHandler
from google.appengine.api import taskqueue
#from google.appengine.ext import webapp

from config import CONFIG, MSG
from model import UserInfo, ContentInfo
import utils


class AbstractApp(BaseHandler):
    def get(self):
        client = utils.makeFoursquareClient()

        content_id = self.request.get('content_id')
        if content_id:
            content_info = ContentInfo.all().filter('content_id =', content_id).get()
            if not content_info:
                self.error(404)
                return
            return self.contentGet(client, content_info)

        return self.appGet(client)


    def post(self):
        if self.request.path.startswith('/_checkin') and self.request.get('checkin'):
            # Parse floats as string so we don't lose lat/lng precision. We can use Decimal later.
            checkin_json = json.loads(self.request.get('checkin'),
                                      parse_float=str)
            user_id = checkin_json['user']['id']
            access_token = self.fetchAccessToken(user_id)
            if not access_token:
                logging.warning('Recieved push for unknown user_id {}'.format(user_id))
                return
            client = utils.makeFoursquareClient(access_token)
            return self.checkinTaskQueue(client, checkin_json)
        if self.request.path.startswith('/_warnings') and self.request.get('content'):
            content = json.loads(self.request.get('content'))
            access_token = content['access_token']
            client = utils.makeFoursquareClient(access_token)
            return self.warningTaskQueue(client, content)
        
        ## if self.this_is_a_homepost():
        ## return self.appHomePost
        ## else 
        ## return self.appBarPost

        client = utils.makeFoursquareClient()
        return self.appPost(client)


    ##################################################
    ## Currently nothing happens when we go Here!
    ## We could fix it...
    ##################################################
    def appGet(self, client):
        """Generic handler for GET requests"""
        logging.warning('appGet stub called')
        self.error(404)
        return


    def homepageGet(self, client):
        """Serves a simple homepage where the user can authorize the app"""


    def contentGet(self, client, content_info):
        """Handler for content related GET requests"""
        logging.warning('contentGet stub called')
        self.error(404)
        return


    def appPost(self, client):
        """Generic handler for POST requests"""
        logging.warning('appPost stub called')
        self.error(404)
        return


    ##################################################
    ## Also add handler for 
    ##################################################
    def checkinTaskQueue(self, authenticated_client, checkin_json):
        """Handler for check-in task queue"""
        logging.warning('checkinTaskQueue stub called')
        return
    
    def warningTaskQueue(self, content):
        """Handler for check-in task queue"""
        logging.warning('checkinTaskQueue stub called')
        return
    
    def wheres_home(self, client):
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
    
    def madeItHome(self,now,then):
        return int(then) > int(now) * 1000

    ## Depreciate in favor of fetchUserInfo
    def fetchAccessToken(self, user_id):
        ## Add attempt to get from session or memcache
        request = UserInfo.all()
        request.filter("fs_id = ", str(user_id))
        user_token = request.get()
        return user_token.token if user_token else None
    
    ## Use for User Queries!
    

    def fetchContentInfo(self, content_id):
        request = ContentInfo.all().filter("content_id = ", content_id)
        return request.get()

    def generateContentUrl(self, content_id):
        return utils.generateContentUrl(content_id)
    
    def gen_reminders(self,then):
        now = int(time.time())
        then_date = int(then)/1000
        w_times = [25,15,10, 0] #we can change this to make it modular
        w1 = (then_date - (w_times[0] * 60)) - now
        w2 = (then_date - (w_times[1] * 60)) - now
        w3 = (then_date - (w_times[2] * 60)) - now
        w4 = (then_date - (w_times[3] * 60)) - now
        return [(w1, w_times[0], 'w1'),
                (w2, w_times[1], 'w2'),
                (w3, w_times[2], 'w3'),
                (w4, w_times[3], 'w4')]
    
    #===========================================================================
    # Sets warnings for Checkins!
    #===========================================================================
    def setWarnings(self, then, content):
        warnings = self.gen_reminders(then)
        
        limit = len(warnings) - 1
        pos = 1
        for secs,mins,i in warnings:
            if secs < 0:
                continue
            content['first'] = False
            content['last'] = False
            content['mins'] = mins
            message = random.choice(MSG[i]).format(**content)
            content['message'] = message
            if pos == 1:
                content['first'] = True
            elif pos == limit:
                content['last'] = True
            
            logging.debug('*** We set a task for {} seconds away! ***'.format(secs))
            
            taskqueue.add(url='/_warnings',
                          params={"content" : json.dumps(content)},
                          countdown = secs)
            pos += 1
    
    def friendOneNDun(self, user, user_id): #user is the authed fs_user
        """Function for friending One-n-Dun! If the User allows in the setPrefs, 
            oneNDun can comment friendly reminders to his/her checkin!"""
        
        oneNDun = utils.makeFoursquareClient(CONFIG['oneNDun_token'])
        try:
            user.users.request(CONFIG['oneNDun_uid'])
            oneNDun.users.approve(user_id)
        except:
            return False
        return True
        
    def getLastComment(self, client, cid, fs_id): #can default these vals to Scoman or OND's
        comments = client.checkins(cid)['checkin']['comments']['items']
        comments.reverse()
        for comment in comments:
            if comment['user']['id'] == fs_id:
                return comment['id']
        return None
    
    def deleteLastComment(self, client, cid, fs_id, lcid=None):
        #lcid = last checkin id!
        if not lcid:
            lastCommentId = self.getLastComment(client,cid,fs_id)
            logging.debug("** lcid was None in deleteLastComment! ***")
        else:
            lastCommentId = lcid
        if lastCommentId:
            client.checkins.deletecomment(cid,{'commentId' : lastCommentId})
            return lastCommentId
        return None
    
    def addRobotComment(self, cid, text, lcid=None, delete = True):
        oneNDun = utils.makeFoursquareClient(CONFIG['oneNDun_token'])
        try:
            if delete:
                self.deleteLastComment(oneNDun, cid, CONFIG['oneNDun_uid'], lcid)
            comment = oneNDun.checkins.addcomment(cid,params = {'text':text})
        except:
            return None
        return comment.get('comment').get('id')
    
    def get_latlon_checkin(self, checkin_json):
        location = checkin_json['venue']['location']
        latlon = ','.join([str(location['lat']), str(location['lng'])])
        return latlon 
           
    def makeContentInfo(self,
                        checkin_json,
                        content,
                        url=None,
                        text=None, photoId=None,
                        reply=False, post=False):
        assert (reply ^ post), "Must pass exactly one of reply or post"
        assert (text or photoId)

        # Avoid posting duplicate content.
        request = ContentInfo.all()
        request = request.filter('checkin_id = ', checkin_json['id'])
        existing_contents = request.fetch(10)
        for existing_content in existing_contents:
            # Check that they're the same type of content
            if existing_content.reply_id and not reply:
                continue
            if existing_content.post_id and not post:
                continue
            # Check if the content payload is the same
            if existing_content.content == content:
                logging.info('Avoided posting duplicate content %s' % content)
                return existing_content

        content_id = utils.generateId()
        checkin_id = checkin_json['id']

        content_info = ContentInfo()
        content_info.content_id = content_id
        content_info.fs_id = checkin_json['user']['id']
        content_info.checkin_id = checkin_id
        content_info.venue_id = checkin_json['venue']['id']
        content_info.content = content
        if not url:
            url = self.generateContentUrl(content_id)

        access_token = self.fetchAccessToken(content_info.fs_id)
        client = utils.makeFoursquareClient(access_token)

        params = {'contentId' : content_id,
                  'url' : url}
        if text:
            params['text'] = text
        if photoId:
            params['photoId'] = photoId

        #logging.info('creating content with params=%s' % params)

        if post:
            if CONFIG['local_dev']:
                content_info.post_id = utils.generateId()
            else:
                response_json = client.checkins.addpost(checkin_id, params)
                content_info.post_id = response_json['post']['id']
        elif reply:
            if CONFIG['local_dev']:
                content_info.reply_id = utils.generateId()
            else:
                response_json = client.checkins.reply(checkin_id, params)
                reply_id = None
                if 'replies' in response_json:
                    reply_id = response_json['replies']['id']
                elif 'reply' in response_json:
                    # Right now we return "replies" but we should probably return "reply"
                    # adding this so I don't have to do it later in the event we rename
                    reply_id = response_json['reply']['id']
                else:
                    logging.error("Could not find reply id in /checkins/reply response: %s" % response_json)

                content_info.reply_id = reply_id

        content_info.put()

        return content_info
