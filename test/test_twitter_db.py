#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from twitter_db import TwitterDb
import unittest


class TestTwitterDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dbpath = (os.path.dirname(os.path.abspath(__file__)) +
                       "/test.sqlite")
        if os.path.exists(cls._dbpath):
            os.remove(cls._dbpath)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls._dbpath):
            os.remove(cls._dbpath)

    def setUp(self):
        self._db = TwitterDb(self._dbpath)
        self._db.create_db()

    def tearDown(self):
        self._db.close()
        self._db = None
        os.remove(self._dbpath)

    def test_createdb(self):
        # createdb直後の状態をテストする
        self.assertTrue(os.path.exists(self._dbpath),
                        "Databaseファイルが存在しない")
        self.assertIsNone(self._db.GetCondition("test"),
                          "作成直後のDBのsearch_conditionにデータが存在する")

    def test_updateCondition(self):
        #search_conditionの更新を確認する
        self._db.SetCondition(None, "test", 0, 2, 3, 4)
        cond = self._db.GetCondition("test")
        self.assertEqual(cond['id'], 1)
        self.assertEqual(cond['term'], 'test')
        self.assertEqual(cond['found_since'], 0)
        self.assertEqual(cond['max_id'], 2)
        self.assertEqual(cond['min_id'], 3)
        self.assertEqual(cond['since_id'], 4)

        self._db.SetCondition(1, "test", 1, 3, 4, 5)
        cond = self._db.GetCondition("test")
        self.assertEqual(cond['id'], 1)
        self.assertEqual(cond['term'], 'test')
        self.assertEqual(cond['found_since'], 1)
        self.assertEqual(cond['max_id'], 3)
        self.assertEqual(cond['min_id'], 4)
        self.assertEqual(cond['since_id'], 5)

    def test_updateTweet(self):
        # Tweetの追加の確認
        self._db.AppendTweet(1, 1111, "TEST1", 2222, 3333)
        self._db.AppendTweet(1, 1112, "TEST2", 2223, 3334)
        self._db.AppendTweet(1, 1113, "TEST3", 2224, 3335)
        self._db.AppendTweet(1, 1114, "TEST4", 2225, 3336)

        self._db.AppendTweet(2, 9999, "TEST", 333, 777)
        # 同じツイートが違う検索条件でひっかかる
        self._db.AppendTweet(2, 1111, "TEST1", 2222, 3333)

        self._db.Commit()
        ret1 = self._db.GetTweets(1)
        ret2 = self._db.GetTweets(2)

        self.assertEqual(len(ret1), 4)
        self.assertEqual(len(ret2), 2)

if __name__ == '__main__':
    unittest.main()
