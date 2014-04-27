#!/usr/bin/env python
# encoding: utf-8

"""
Web version of TweetDreams

by jorgeh@ccrma
"""


# Bottle requires gevent.monkey.patch_all() even if you don't like it.
from gevent import monkey; monkey.patch_all()
from gevent import sleep
from socketio.namespace import BaseNamespace
from socketio import socketio_manage
from socketio.mixins import BroadcastMixin

from bottle import Bottle, request, redirect, static_file, view, run, route

from TwitterAPI import TwitterAPI
import twitteroauth as oauth

import time
from datetime import datetime
import re

import json

import pprint
pp = pprint.PrettyPrinter(indent=4)

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


app = Bottle()

PORT = 9000


def getTwitterConsumerCreds(filename='twitter_consumer.json'):
    json_data=open(filename)
    data = json.load(json_data)
    json_data.close()
    return (data.get('consumer_key',''), data.get('consumer_secret',''))

(consumer_key, consumer_secret) = getTwitterConsumerCreds()


# BIG HACK!!!
OA = None


######################################################
# Bottle server
######################################################

@app.error(404)
@view('error')
def error404(error):
    return {'message':'NOTHING FOR YOU HERE!'}
    # pass

@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')



# @route('/distance', method='POST')
# def post_distance():
#     distance = request.json
#     GeometryCommNamespace.broadcast('new_distance', distance);
#     return "Got it! (the distance, I mean)"


# @route('/node', method='POST')
# def post_node():
#     node = request.json
#     print node
#     if not nodeExists(node['ip']):
#         NODES.append(node)
#         GeometryCommNamespace.broadcast('new_node', node)

#     return "Got it! (the node, I mean)"



@app.route('/')  # default method is GET
@view('index')
def do_root():
    # return {'size':{'width':960, 'height':600}}
    pass


@app.route('/sign_in')  # default method is GET
def do_sign_in():
    logging.info("Singing in ...")
    # print self.environ['HTTP_ORIGIN']
    # print self.environ['bottle.app']
    # a = self.environ['bottle.app']
    # print a.get_url('/vis')
    # print self.environ
    # callbackURL = self.environ['bottle.app'].get_url('/vis')

    # FIXME: this is a temporal hack (for some reason get_url doesn't work)
    callbackURL = 'http://127.0.0.1:9000/vis'

    global OA
    OA = oauth.TwitterOAuth(consumer_key, consumer_secret, callbackURL)
    url = OA.getAuthURL()
    print "redirecting to", url
    redirect(url)


@app.route('/vis')  # default method is GET
@view('vis')
def do_vis():
    print "GOT A CALL TO VIS!!!"
    global OA
    if OA:
        # print request.query
        # for k in request.query:
        #     print k, request.query[k]

        access_token = OA.getAccessToken(request.query['oauth_verifier'])

        # print "Access Token:"
        # print "    - oauth_token        = %s" % access_token['oauth_token']
        # print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']

    pass

######################################################
# gevent-socketio stuff
######################################################

class TweetsNamespace(BaseNamespace, BroadcastMixin):

    # this will allow to broadcast events triggered from outside gevent-socketio
    # (e.g. when getting a message from the iOS app)
    __all__ = set()
    def __init__(self, *args, **kwargs):
        super(TweetsNamespace, self).__init__(*args, **kwargs)
        self.__class__.__all__.add(self)

    @classmethod
    def broadcast(cls, msg, data):
        for socket in cls.__all__:
            socket.emit(msg, data)


    def initialize(self):
        self.emit('hello', {'msg':'alright!'})
        # self.spawn(self.job_send_heart_beat)  # this is here just as a reminder on how to spawn "jobs" in gevent-socketio


    # this is here just as a reminder on how to spawn "jobs" in gevent-socketio
    def job_send_heart_beat(self):
        cnt = 0
        while True:
            self.emit('heart_beat', cnt)
            cnt += 1
            sleep(5)  # this is actually gevent.sleep (must be!)



# hook gevent-socketio to bottle
@app.route('/socket.io/<path:path>')
def socketio_service(path):
    socketio_manage(request.environ,
                    {'/tweets': TweetsNamespace},
                    request)




######################################################
# Twitter stuff
######################################################


def searchTweets(consumer_key, consumer_secret, access_token, access_token_secret, global_keywords, local_keywords):

    last_connection = None
    reconnection_pause = 1  # in seconds (used to scale back in case of recurrent connection problems)
    min_recon_pause = 1 # in seconds
    max_recon_pause = 60*10 # 10 minutes!

    receivedTweetIDs = set([])

    while True:
        try:
            terms = set(global_keywords+local_keywords)

            print("Starting connection ...\n")
            api = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)
            r = api.request('statuses/filter', {'track':','.join(terms)})
            print("Response Status Code: %d" % (r.status_code))

            # see https://dev.twitter.com/docs/streaming-apis/connecting for details about this code
            if r.status_code == 200:  # Success
                for tweet in r.get_iterator():
                    if ('id' in tweet) and (tweet['id'] not in receivedTweetIDs):
                        receivedTweetIDs.add(tweet['id'])
                        parseTweet(tweet, global_keywords, local_keywords)
            elif r.status_code == 401:  # Unauthorized
                print(("HTTP authentication failed due to either:\n"
                            "\t* Invalid basic auth credentials, or an invalid OAuth request;\n"
                            "\t* Out-of-sync timestamp in your OAuth request (the response body will indicate this);\n"
                            "\t* Too many incorrect passwords entered or other login rate limiting.\n"))
                return
            elif r.status_code == 403:  # Forbidden
                print("The connecting account is not permitted to access this endpoint.\n")
                return
            elif r.status_code == 404:  # Unknown
                print("There is nothing at this URL, which means the resource does not exist.\n")
                return
            elif r.status_code == 406:  # Not Acceptable
                print(("At least one request parameter is invalid. For example, the filter endpoint returns this status if:\n"
                            "\t* The track keyword is too long or too short;\n"
                            "\t* An invalid bounding box is specified;\n"
                            "\t* Neither the track nor follow parameter are specified;\n"
                            "\t* The follow user ID is not valid.\n"))
                return
            elif r.status_code == 413:  # Too Long
                print(("A parameter list is too long. For example, the filter endpoint returns this status if:\n"
                            "\t* More track values are sent than the user is allowed to use;\n"
                            "\t* More bounding boxes are sent than the user is allowed to use;\n"
                            "\t* More follow user IDs are sent than the user is allowed to follow.\n"))
                return
            elif r.status_code == 416:  # Range Unacceptable
                print(("For example, an endpoint returns this status if:\n"
                            "\t* A count parameter is specified but the user does not have access to use the count parameter;\n"
                            "\t* A count parameter is specified which is outside of the maximum/minimum allowable values.\n"))
                return
            elif r.status_code == 420:  # Rate Limited
                print(("The client has connected too frequently. For example, an endpoint returns this status if:\n"
                            "\t* A client makes too many login attempts in a short period of time;\n"
                            "\t* Too many copies of an application attempt to authenticate with the same credentials.\n"))
                return
            elif r.status_code == 503:  # Service Unavailable
                print(("A streaming server is temporarily overloaded;\n"
                            "Attempt to make another connection, keeping in mind the \n"
                            "connection attempt rate limiting and possible DNS caching in your client.\n"))
                time.sleep(60*5)  # wait 5 minutes
        except Exception, e:
                print("Twitter ConnectionError. Reason: %s\n" % (e))
                print("It should reconnect automatically\n")

        # hacky!
        time_from_last_attempt = (datetime.now() - last_connection).seconds
        if time_from_last_attempt > max_recon_pause:
            reconnection_pause = min_recon_pause

        # Pause before trying to reconnect
        # FIXME: this was a quick hack! We should follow the guidelines suggested in
        # https://dev.twitter.com/docs/streaming-apis/connecting
        print("Will wait %d seconds before attempting to reconnect ..." % (reconnection_pause))
        time.sleep(reconnection_pause)
        if time_from_last_attempt < max_recon_pause:
            reconnection_pause *= 2


    print("Twitter stream stopped\n")


# handle an incoming tweet
def parseTweet(tweet, global_keywords, local_keywords):

    terms = set(global_keywords+local_keywords)

    # URL pattern (used to remove URLs from tweets)
    url_pattern = re.compile('(https?://)(www\.)?([a-zA-Z0-9_%\.]*)([a-zA-Z]{2})?((/[a-zA-Z0-9_%~]*)+)?(\.[a-zA-Z]*)?(\?([a-zA-Z0-9_%~=&])*)?')

    # ignore retweeted messages
    if 'retweeted' in tweet:
        if tweet['retweeted']:
            return

    # TODO: should we filter out non-english messages?
    # in theory we could use the 'lang' attibute, but many non-english
    # tweets use lang=en anyways, so is not very robust.
    # A more scientific was is to use a language detection tool, such as https://github.com/saffsd/langid.py

    if 'text' in tweet:
        # filter out any URL in the tweet
        tweet['text'] = re.sub(url_pattern, '', tweet['text'])
        #replace &gt and &lt (TODO: are there other special characters for Twitter? Should we use some generic HTML decoding?)
        tweet['text'] = tweet['text'].replace('&lt;', '<')
        tweet['text'] = tweet['text'].replace('&gt;', '>')

        if ('user' in tweet) and ('screen_name' in tweet['user']):
            tweet['text'] = tweet['user']['screen_name'].encode('utf-8') + ": " + tweet['text']
        else:
            tweet['text'] = "anonymous: " + tweet['text']

        # For some reason, sometimes we get tweets without any relevant word (why?).
        # We need to check for that case. Also, we need to distinguish "local" tweets from "world"
        # tweets
        irrelevant = True
        for term in terms:
            if tweet['text'].lower().find(term.lower()) >= 0:
                irrelevant = False
                break

        tweet['local'] = 0
        for term in local_keywords:
            if tweet['text'].lower().find(term.lower()) >= 0:
                irrelevant = False
                tweet['local'] = 1
                break

        if irrelevant:
            return

        if tweet['local']:
            print("Local Tweet Received", tweet)
        else:
            print("Global Tweet Received", tweet)

        # printTweet(tweet)




######################################################
# entry point
######################################################


def main():

    # local_keywords = ['#chile']
    # global_keywords = ['tech', 'love', 'music']

    # searchTweets(consumer_key,
    #              consumer_secret,
    #              access_token,
    #              access_token_secret,
    #              global_keywords,
    #              local_keywords)

    debug_mode = True;
    reload_mode = True;

    run(app=app,
        server='geventSocketIO',
        host='0.0.0.0',
        port=PORT,
        debug=debug_mode,
        reloader=reload_mode)


if __name__ == '__main__':
    main()

