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

import bottle
from beaker.middleware import SessionMiddleware

import twitteroauth as tauth
from tweets import Tweets
import pprint
pp = pprint.PrettyPrinter(indent=4)

import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)



session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './.data',
    'session.auto': True
}

PORT = 9000
app = SessionMiddleware(bottle.app(), session_opts)

consumer_token = tauth.getTwitterConsumerCreds('twitter_consumer.json')



######################################################
# Bottle server
######################################################

@bottle.error(404)
@bottle.view('error')
def error404(error):
    return {'message':'NOTHING FOR YOU HERE!'}
    # pass

@bottle.route('/static/<path:path>')
def server_static(path):
    return bottle.static_file(path, root='static')


@bottle.route('/')  # default method is GET
@bottle.view('index')
def index():

    session = bottle.request.environ.get('beaker.session')
    if not session.has_key('access_token'):
        return {'signed_in': False}

    return {'signed_in': True,
            'username':session['access_token']['screen_name']}


@bottle.route('/sign_in')  # default method is GET
def sign_in():
    logging.info("Singing in ...")
    session = bottle.request.environ.get('beaker.session')

    # callbackURL = app.get_url('/twitter_callback')
    # FIXME: this is a temporal hack (for some reason get_url doesn't work)
    callbackURL = 'http://127.0.0.1:9000/twitter_callback'

    session['request_token'] = tauth.getRequestToken(consumer_token, callbackURL)
    url = tauth.getAuthURL(session['request_token'])
    session.save()

    logging.debug("redirecting to %s" % url)

    bottle.redirect(url)


@bottle.route('/twitter_callback')  # default method is GET
def twitter_callback():

    # Just make sure that we have a valid session
    session = bottle.request.environ.get('beaker.session')
    if not session.has_key('request_token'):
        bottle.redirect('/')


    access_token = tauth.getAccessToken(consumer_token,
                                        session['request_token'],
                                        bottle.request.query['oauth_verifier'])
    session['access_token'] = access_token
    session.save()
    logging.debug("access token:\n%s" % pp.pformat(access_token))

    bottle.redirect('/')


@bottle.route('/sign_out')
def logout():
    session = bottle.request.environ.get('beaker.session')
    session.clear()
    bottle.redirect('/')


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

    def on_start_stream(self, data):
        logging.info(pprint.pformat(data))
        session = self.environ.get('beaker.session')
        if not session.has_key('access_token'):
            self.emit('failed_stream')
        access_token = session['access_token']
        tweets = Tweets(consumer_token, access_token)
        tweets.startStream([t.strip() for t in data], [], self.tweet_callback)

    def tweet_callback(self, tweet):
        self.emit('new_tweet', tweet)

    # this is here just as a reminder on how to spawn "jobs" in gevent-socketio
    def job_send_heart_beat(self):
        cnt = 0
        while True:
            self.emit('heart_beat', cnt)
            cnt += 1
            sleep(5)  # this is actually gevent.sleep (must be!)



# hook gevent-socketio to bottle
@bottle.route('/socket.io/<path:path>')
def socketio_service(path):
    socketio_manage(bottle.request.environ,
                    {'/tweets': TweetsNamespace},
                    bottle.request)




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

    bottle.run(app=app,
               server='geventSocketIO',
               host='0.0.0.0',
               port=PORT,
               debug=debug_mode,
               reloader=reload_mode)


if __name__ == '__main__':
    main()

