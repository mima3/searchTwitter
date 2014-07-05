#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import twitter
from twitter import Api

reload(sys)
sys.setdefaultencoding('utf-8')


class TweeterSearcher:
    """
    ツイッターの情報を管理するデーターベース
    """
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token_key,
                 access_token_secret):
        self._api = Api(base_url="https://api.twitter.com/1.1",
                        consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token_key=access_token_key,
                        access_token_secret=access_token_secret)
        self.UpdateRateLimitStatus()
        self._tweets = []
        self._users = {}

    def UpdateRateLimitStatus(self):
        self._rate_limit = self._api.GetRateLimitStatus()

    def GetSearchRemaining(self):
        """
        GetSearchの残り実行可能回数を取得
        """
        search = self._rate_limit['resources']['search']
        return search['/search/tweets']['remaining']

    def GetSearchReset(self):
        search = self._rate_limit['resources']['search']
        return time.localtime(search['/search/tweets']['reset'])

    def StartSearch(self, term, since_id=None, max_id=None):
        self._tweets = []
        self._users = {}
        self.max_id = 0
        self.min_id = 0

        ret = self._GetSearch(term, since_id, max_id)
        while True:
            if ret == -1:
                return False
            if ret == 0:
                return True
            ret = self._GetSearch(term, since_id, self.min_id - 1)

    def GetTweets(self):
        return self._tweets

    def _GetSearch(self, term, since_id, max_id):
        """
        Twitterの検索を行う
        @param term 検索文字
        @param since_id 検索開始ID　このID以上のIDが検索される
        @param max_id 検索最大ID　このID以下のIDのみ検索される
        @return 検索した最低ID　-1の場合はAPIの上限　０はすべて検索できた
        """
        if self.GetSearchRemaining() == 0:
            return -1
        search = self._rate_limit['resources']['search']
        --search['/search/tweets']['remaining']

        try:
            found = self._api.GetSearch(term=term,
                                        count=100,
                                        result_type='recent',
                                        lang='ja',
                                        max_id=max_id,
                                        since_id=since_id)
        except twitter.TwitterError, ex:
            print ex
            return -1

        for f in found:
            if self.min_id > f.id or self.min_id == 0:
                self.min_id = f.id
            if self.max_id < f.id or self.max_id == 0:
                self.max_id = f.id
            rec = {'id': f.id,
                   'text': f.text,
                   'user_id': f.user.id,
                   'createdtime': f.created_at}
            self._tweets.append(rec)
        return len(found)
