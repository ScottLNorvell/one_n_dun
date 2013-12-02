# import random
# import string

from google.appengine.ext import db


#===============================================================================
# User info class!
#===============================================================================
class UserInfo(db.Model): ## UserInfo
    """Contains the user to foursquare_id + oauth token mapping."""
    
    
    fs_id = db.StringProperty()
    token = db.StringProperty()
    
    #gender = db.StringProperty() ## Unnecessary because we get it from client.users() and pass it around in content. We'll store this in prefs for s&g's
    prefs = db.TextProperty() 
    then = db.StringProperty() ##  ***** possibly this gets stored in prefs? also curr_home? *****
    curr_home = db.TextProperty()
    curr_transaction = db.TextProperty() #json.dumps of current transaction --OR-- string of current trans_id?
    content = db.TextProperty() ## this is the content for the session... (home, charity, etc gets set on bar post, cleared on home checkin)
    
    
    #a list of {'trans_id' : trans_id, 'paid' : False or Date, 'amount' : amount, 'charity' : charity, 'due' : due, 'activated' : activated}
    transactions = db.TextProperty() 

    @staticmethod
    def get_by_fs_id(fs_id):
        return UserInfo().all().filter('fs_id =', fs_id).get()
    
#===============================================================================
# Content Main!
#===============================================================================
class ContentInfo(db.Model):
    """Generic object for easily storing content for a reply or post."""
    content_id = db.StringProperty() #poss use google's generated id?
    checkin_id = db.StringProperty()
    venue_id = db.StringProperty()
    fs_id = db.TextProperty()
    content = db.TextProperty()
    reply_id = db.TextProperty()
    post_id = db.TextProperty()



#===============================================================================
# Transactions stored here, fetched by trans_id!
#===============================================================================
class TransactionData(db.Model):
    trans_id = db.StringProperty()
    paid = db.BooleanProperty()
    transaction = db.TextProperty() #json.dumps of transaction data!

    @staticmethod
    def get_by_trans_id(trans_id):
        return TransactionData().all().filter('trans_id =', trans_id).get()

