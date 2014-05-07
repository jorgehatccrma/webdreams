WebDreams
=========

Pure web implementation of TweetDreams

This is a work-in-progress. See [TweetDreams][1] for more info.


Installation
------------

**BEFORE YOU START: install `virtualenv`**


 1. Clone this repo
 2. Create the virtual environment (e.g. `$ virtualenv --no-site-packages vEnv`, where `vEnv` can be whatever)
 3. Activate the virtualenv: `$ source vEnv/bin/activate`
 4. Install dependencies: `(vEnv)$ pip install -r requirements.txt`

That should set up everything you need to run the server side. Now you can start the server:
`(vEnv)$ python server.py`

... and that's it! Now open a browser and go to http://127.0.0.1:9000/ and have fun.


**NOTE**
As is, the code will only run on a browser running on the same machine as the server. This is because to use browser based OAuth, twitter requires a callback URL, which should be defined by the app when creating it at https://dev.twitter.com/.
Since this is a work in progress and not planned to be hosted anywhere yet, the URL defined in https://dev.twitter.com/ is http://127.0.0.1:9000/twitter_callback. 

If you want to host this somewehere, then you'll need to do 2 things:

 1. Specify the callback URL for your twitter app in https://dev.twitter.com
 2. Change `server.py`'s *sign_in()* method (line 79 or thereabouts) to match the callback URL



Configuration
-------------

To run the server, you will need a consumer_key and consumer_secret provided by Twitter ([dev.twitter.com][2]). Once you have them, create a JSON file named `twitter_consumer.json` in the root folder (where this README is). Its contents should look like:

    {
      "consumer_key": "<your_key>",
      "consumer_secret": "<your_secret>"
    }

[1]: https://github.com/jorgehatccrma/TweetDreams "TweetDreams"
[2]: http://dev.twitter.com "dev.twitter.com"
