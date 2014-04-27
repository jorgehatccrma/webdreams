import time
from datetime import datetime
import re

from TwitterAPI import TwitterAPI

import logging
logging.basicConfig(level=logging.DEBUG)


STATUS_CODE_MESSAGES = {
    401:"HTTP authentication failed due to either:\n"+
        "\t* Invalid basic auth credentials, or an invalid OAuth request;\n"+
        "\t* Out-of-sync timestamp in your OAuth request (the response body will indicate this);\n"+
        "\t* Too many incorrect passwords entered or other login rate limiting.\n",
    403:"The connecting account is not permitted to access this endpoint.\n",
    404:"There is nothing at this URL, which means the resource does not exist.\n",
    406:"At least one request parameter is invalid. For example, the filter endpoint returns this status if:\n"+
        "\t* The track keyword is too long or too short;\n"+
        "\t* An invalid bounding box is specified;\n"+
        "\t* Neither the track nor follow parameter are specified;\n"+
        "\t* The follow user ID is not valid.\n",
    413:"A parameter list is too long. For example, the filter endpoint returns this status if:\n"+
        "\t* More track values are sent than the user is allowed to use;\n"+
        "\t* More bounding boxes are sent than the user is allowed to use;\n"+
        "\t* More follow user IDs are sent than the user is allowed to follow.\n",
    416:"For example, an endpoint returns this status if:\n"+
        "\t* A count parameter is specified but the user does not have access to use the count parameter;\n"+
        "\t* A count parameter is specified which is outside of the maximum/minimum allowable values.\n",
    420:"The client has connected too frequently. For example, an endpoint returns this status if:\n"+
        "\t* A client makes too many login attempts in a short period of time;\n"+
        "\t* Too many copies of an application attempt to authenticate with the same credentials.\n",
    503:"A streaming server is temporarily overloaded;\n"+
        "Attempt to make another connection, keeping in mind the \n"+
        "connection attempt rate limiting and possible DNS caching in your client.\n"
}

# URL pattern (used to remove URLs from tweets)
URL_PATTERN = re.compile('(https?://)(www\.)?([a-zA-Z0-9_%\.]*)([a-zA-Z]{2})?((/[a-zA-Z0-9_%~]*)+)?(\.[a-zA-Z]*)?(\?([a-zA-Z0-9_%~=&])*)?')



class Tweets(object):

    def __init__(self, consumer_token, access_token):
        self.consumer_key = consumer_token['consumer_key']
        self.consumer_secret = consumer_token['consumer_secret']
        self.access_key = access_token['oauth_token']
        self.access_secret = access_token['oauth_token_secret']



    def startStream(self, global_keywords, local_keywords, callback):

        self.global_keywords = global_keywords
        self.local_keywords = local_keywords

        last_connection = None
        reconnection_pause = 1  # in seconds (used to scale back in case of recurrent connection problems)
        min_recon_pause = 1 # in seconds
        max_recon_pause = 60*10 # 10 minutes!

        receivedTweetIDs = set([])

        while True:
            try:
                logging.info("Starting connection ...\n")

                terms = set(self.global_keywords + self.local_keywords)
                api = TwitterAPI(self.consumer_key, self.consumer_secret,
                                 self.access_key, self.access_secret)
                r = api.request('statuses/filter', {'track':','.join(terms)})

                logging.info("Response Status Code: %d" % (r.status_code))

                # see https://dev.twitter.com/docs/streaming-apis/connecting for details about this code
                if r.status_code == 200:  # Success
                    for tweet in r.get_iterator():
                        if ('id' in tweet) and (tweet['id'] not in receivedTweetIDs):
                            receivedTweetIDs.add(tweet['id'])
                            self._processTweet(tweet)
                            callback(tweet)

                elif STATUS_CODE_MESSAGES.has_key(r.status_code):
                    logging.info(STATUS_CODE_MESSAGES[r.status_code])

                    if r.status_code == 503:
                        time.sleep(60*5)  # wait 5 minutes
                    else:
                        return

                else:
                    logging.info("Received unknown status code: %d" % r.status_code)

            except Exception, e:
                logging.error("Twitter ConnectionError. Reason: %s\n" % (e))
                logging.info("It should reconnect automatically\n")

            # hacky!
            time_from_last_attempt = (datetime.now() - last_connection).seconds
            if time_from_last_attempt > max_recon_pause:
                reconnection_pause = min_recon_pause

            # Pause before trying to reconnect
            # FIXME: this was a quick hack! We should follow the guidelines suggested in
            # https://dev.twitter.com/docs/streaming-apis/connecting
            logging.debug("Will wait %d seconds before attempting to reconnect ..." % (reconnection_pause))
            time.sleep(reconnection_pause)
            if time_from_last_attempt < max_recon_pause:
                reconnection_pause *= 2


        logging.info("Twitter stream stopped\n")


    # handle an incoming tweet
    def _processTweet(self, tweet):

        terms = set(self.global_keywords + self.local_keywords)

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
            tweet['text'] = re.sub(URL_PATTERN, '', tweet['text'])
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
            for term in self.local_keywords:
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

            _printTweet(tweet)


def _printTweet(tweet):
    if 'text' in tweet:
        # logging.info(tweet['text'] + "\n")
        text = tweet['text'].encode('utf-8')
        # remove URLs from tweets
        text = re.sub(URL_PATTERN, '', text)
        if ('user' in tweet) and ('screen_name' in tweet['user']):
            logging.info("Got tweet from '" + tweet['user']['screen_name'].encode('utf-8') + "' : " + text + "\n")
        else:
            logging.info("Got tweet from <anonymous> : " + text + "\n")



