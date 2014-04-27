import oauth2 as oauth
import urllib
import urlparse
import json
import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

REQUEST_TOKEN_URI = 'https://api.twitter.com/oauth/request_token'
AUTHORIZE_URI = 'https://api.twitter.com/oauth/authorize'
ACCESS_TOKEN_URI = 'https://api.twitter.com/oauth/access_token'


def getTwitterConsumerCreds(filename):
    json_data=open(filename)
    data = json.load(json_data)
    json_data.close()
    return {'consumer_key': data.get('consumer_key',''),
            'consumer_secret': data.get('consumer_secret','')}


def getRequestToken(consumer_token, callbackURL):
    """
    consumer_token = {'consumer_key':'<key>',
                      'consumer_secret':'<secret>')
    (provided by dev.twitter.com)

    callbackURL: URL that twitter will redirect to after authorization
    """

    if not consumer_token.has_key('consumer_key'):
        raise Exception("No consumer_key provided")

    if not consumer_token.has_key('consumer_secret'):
        raise Exception("No consumer_secret provided")

    consumer = oauth.Consumer(consumer_token['consumer_key'],
                              consumer_token['consumer_secret'])
    client = oauth.Client(consumer)

    # Get a Request Token
    body = urllib.urlencode({'oauth_callback':callbackURL})
    resp, content = client.request(REQUEST_TOKEN_URI, "POST", body=body)
    if resp['status'] != '200':
        print resp
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))
    logging.debug("oauth_token: %s" % request_token['oauth_token'])
    logging.debug("oauth_token_secret = %s" % request_token['oauth_token_secret'])

    return request_token


def getAuthURL(request_token):
    return "%s?oauth_token=%s" % (AUTHORIZE_URI, request_token['oauth_token'])


def getAccessToken(consumer_token, request_token, oauth_verifier):
    # Get the Access Token
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    consumer = oauth.Consumer(consumer_token['consumer_key'],
                              consumer_token['consumer_secret'])
    client = oauth.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URI, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    logging.debug("oauth_token: %s" % access_token['oauth_token'])
    logging.debug("oauth_token_secret: %s" % access_token['oauth_token_secret'])

    return access_token

