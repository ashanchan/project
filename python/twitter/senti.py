#!/usr/bin/python3
import pkgImporter
import tweepy
from textblob import TextBlob
import util.log as LOGGER
import util.system as SYSTEM
# ===================================================
lineBreak = SYSTEM.repeat2Length('=', 130)
consumer_key = 'D98F3LC8PbnARAIvQf4j89mb1'
consumer_secret = 'tfOFJHBcwl9vws9qdQCIuCsEYqIKKAUmehZdjtaeCMFTOrQAC5'
access_token = '893115233962733568-FpXzBDZid5aPORuYYU6NM3jtmcAKHzV'
access_token_secret = 'o6gu3PSVtjsS6mJsxJlETUWWjinIEDrt7kjedocRmfXxo'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
# ===================================================


def init():
    readParam()
    
# ===================================================


def readParam():
    SYSTEM.clear()
    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tStarting Twitter Sentiment Analysis Process'))
    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', (''))
    topic = input('Enter twitter tags for analytis : ')
    LOGGER.show('info', (''))
    LOGGER.show('info', (lineBreak))
    findSentiment(topic)

# ===================================================

def findSentiment(topic):
    public_tweets = api.search(topic)
    ctr = 0
    polarity = 0
    subjectivity = 0
    for tweet in public_tweets:
        analysis = TextBlob(tweet.text)
        LOGGER.show('info', ('%d \t%s\n \t%s \t %s' % (ctr,  tweet.text, analysis.sentiment.polarity, analysis.sentiment.subjectivity)))
        polarity += analysis.sentiment.polarity
        subjectivity += analysis.sentiment.subjectivity
        print ('\n')
        ctr += 1

    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tFinal Analysis of topic %s against %d opinion \t Polarity [%f] \t  subjectivity [%f]' %(topic, ctr, polarity, subjectivity)))
    LOGGER.show('info', (lineBreak))
    print('\n')
    needed = SYSTEM.acceptValidInput('Continue More Analysis : [Y/N] : ', ['Y', 'y', 'N', 'n'])

    if needed.upper() == 'Y' :
        readParam()


# ===================================================
init()
