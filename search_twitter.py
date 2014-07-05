#!/usr/bin/python
# -*- coding: utf-8 -*-
from twitter_ctrl import TweeterSearcher
from twitter_db import TwitterDb
import sys
import time
import dateutil.parser
import datetime
import calendar
import ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')
from collections import defaultdict


def main(argvs, argc):
    if argc != 4:
        print "Usage: python search_to_db.py dbpath term since_id"
        return -1

    dbpath = argvs[1]
    term = argvs[2]
    since_id = int(argvs[3])

    conf = ConfigParser.SafeConfigParser()
    conf.read("twitter.ini")

    print "==================================="
    print "DB path:", dbpath
    print "term :", term
    print "since_id :", since_id
    print "==================================="
    # もし、UTF-8のターミナルなら以下の行はコメントアウトする
    term = unicode(term, 'cp932').encode('utf-8')
    tw = TweeterSearcher(consumer_key=conf.get('Twitter',
                                               'consumer_key'),
                         consumer_secret=conf.get('Twitter',
                                                  'consumer_secret'),
                         access_token_key=conf.get('Twitter',
                                                   'access_token_key'),
                         access_token_secret=conf.get('Twitter',
                                                      'access_token_secret'))
    db = TwitterDb(dbpath)
    cond = db.GetCondition(term)
    tw_max_id = None
    tw_since_id = None
    cond_id = None
    if cond is None:
        tw_since_id = since_id
        db.SetCondition(None, term, 0, 0, 0, since_id)
        cond = db.GetCondition(term)
        cond_id = cond['id']
    else:
        cond_id = cond['id']
        if cond['found_since']:
            tw_since_id = cond['max_id'] + 1
        else:
            tw_since_id = since_id
            if cond['min_id'] > 0:
                tw_max_id = cond['min_id']-1
    print "tw_since_id :", tw_since_id
    print "tw_max_id :", tw_max_id

    ret = tw.StartSearch(term, tw_since_id, tw_max_id)
    found = 0
    for t in tw.GetTweets():
        print t['text']
        utc = dateutil.parser.parse(t['createdtime']).utctimetuple()
        tmstamp = time.mktime(utc)
        db.AppendTweet(cond_id, t['id'], t['text'], t['user_id'], tmstamp)
    if ret:
        # 全レコードを読み込んだ
        print "All tweets is imported."
        found = 1

    if len(tw.GetTweets()) > 0:
        db.SetCondition(cond_id, term, found, tw.max_id, tw.min_id, since_id)
        print "Import %d" % (len(tw.GetTweets()))

    db.Commit()

    tm = tw.GetSearchReset()
    print "REMAING:%d RESET-TIME: %d:%d" % (tw.GetSearchRemaining(),
                                            tm.tm_hour,
                                            tm.tm_min)

    return 0

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
