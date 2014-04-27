import oauth2 as oauth
import urllib
import urlparse



REQUEST_TOKEN_URI = 'https://api.twitter.com/oauth/request_token'
AUTHORIZE_URI = 'https://api.twitter.com/oauth/authorize'
ACCESS_TOKEN_URI = 'https://api.twitter.com/oauth/access_token'

class TwitterOAuth(object):

    def __init__(self, consumer_key, consumer_secret, callbackURL):
        """
        consumer_key and consumer_secret must be obtained from http://dev.twitter.com
        callbackURL must match the one defined for the app at http://dev.twitter.com
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callbackURL = callbackURL

        # Initialize the OAuth Client
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        self.client = oauth.Client(self.consumer)

    def getAuthURL(self):
        # Get a Request Token
        body = urllib.urlencode({'oauth_callback':self.callbackURL})
        resp, content = self.client.request(REQUEST_TOKEN_URI, "POST", body=body)
        if resp['status'] != '200':
            print resp
            raise Exception("Invalid response %s." % resp['status'])

        self.request_token = dict(urlparse.parse_qsl(content))

        # print "Request Token:"
        # print "    - oauth_token        = %s" % self.request_token['oauth_token']
        # print "    - oauth_token_secret = %s" % self.request_token['oauth_token_secret']

        return "%s?oauth_token=%s" % (AUTHORIZE_URI, self.request_token['oauth_token'])


        # # Redirect to the Provider

        # print "Go to the following link in your browser:"
        # print
        # print

        # accepted = 'n'
        # while accepted.lower() == 'n':
        #     accepted = raw_input('Have you authorized me? (y/n) ')
        # oauth_verifier = raw_input('What is the PIN? ')


    def getAccessToken(self, oauth_verifier):
        # Get the Access Token
        token = oauth.Token(self.request_token['oauth_token'], self.request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(self.consumer, token)

        resp, content = client.request(ACCESS_TOKEN_URI, "POST")
        access_token = dict(urlparse.parse_qsl(content))

        # print "Access Token:"
        # print "    - oauth_token        = %s" % access_token['oauth_token']
        # print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
        # print
        # print "You may now access protected resources using the access tokens above."
        # print

        return access_token