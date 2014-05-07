# Adapted from https://developer.linkedin.com/documents/getting-oauth-token-python

import oauth2 as oauth
import urllib
import urlparse


# Initialize the OAuth Client

consumer_key = ''
consumer_secret = ''
consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)



# Get a Request Token

request_token_url = 'https://api.twitter.com/oauth/request_token'
callbackURL = 'http://127.0.0.1:8000/vis'
body = urllib.urlencode({'oauth_callback':callbackURL})
resp, content = client.request(request_token_url, "POST", body=body)
if resp['status'] != '200':
    print resp
    raise Exception("Invalid response %s." % resp['status'])


request_token = dict(urlparse.parse_qsl(content))

print "Request Token:"
print "    - oauth_token        = %s" % request_token['oauth_token']
print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
print




# Redirect to the Provider

authorize_url = 'https://api.twitter.com/oauth/authorize'
print "Go to the following link in your browser:"
print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
print

accepted = 'n'
while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
oauth_verifier = raw_input('What is the PIN? ')





# Get the Access Token

access_token_url = 'https://api.twitter.com/oauth/access_token'
token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, "POST")
access_token = dict(urlparse.parse_qsl(content))

print "Access Token:"
print "    - oauth_token        = %s" % access_token['oauth_token']
print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
print
print "You may now access protected resources using the access tokens above."
print
