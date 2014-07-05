#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3
import sys
import os


class TwitterDb:
    """
    ツイッターの情報を管理するデーターベース
    """
    def __init__(self, dbpath):
        self._dbpath = dbpath
        self._conn = sqlite3.connect(dbpath)
        self._conn.text_factory = str

    def __del__(self):
        if self._conn:
            self.close()

    def close(self):
        self._conn.close()
        self._conn = None

    @property
    def dbpath(self):
        return self._dbpath

    def create_db(self):
        """
        テーブルを作成する
        """
        sql = '''CREATE TABLE tweets(
                                 id INTEGER PRIMARY KEY,
                                 text TEXT,
                                 user_id INTEGER,
                                 createdtime INTEGER);'''
        self._conn.execute(sql)

        sql = '''CREATE TABLE users(
                                 id INTEGER PRIMARY KEY,
                                 name TEXT,
                                 screen_name TEXT,
                                 description TEXT);'''
        self._conn.execute(sql)

        sql = '''CREATE TABLE search_conditions(
                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 term TEXT,
                                 found_since INTEGER,
                                 max_id INTEGER,
                                 min_id INTEGER,
                                 since_id INTEGER);'''
        self._conn.execute(sql)

        sql = '''CREATE TABLE search_results(
                                 cond_id INTEGER,
                                 tweet_id INTEGER,
                                 PRIMARY KEY(cond_id,tweet_id));'''
        self._conn.execute(sql)

    def GetCondition(self, term):
        """
        検索条件を取得する
        @param term 条件文
        @return search_conditionsテーブルの内容を取得する
        """
        sql = '''SELECT
                   id,term,found_since,max_id, min_id, since_id
                 FROM search_conditions
                 WHERE term = ?;'''
        rows = self._conn.execute(sql, [term, ])
        for r in rows:
            ret = {'id': r[0],
                   'term': r[1],
                   'found_since': r[2],
                   'max_id': r[3],
                   'min_id': r[4],
                   'since_id': r[5]}
            return ret
        return None

    def SetCondition(self, id, term, found_since, max_id, min_id, since_id):
        """
        検索条件を設定する
        @param id     設定対象のID NoneのときはInsertになる
        @param term 条件文
        @param found_since 1ならば、since_idは検索済みである
        @param since_id Twitterの検索に使用するsince_id
        @return search_conditionsテーブルの内容を取得する
        """
        if id:
            sql = '''UPDATE search_conditions
                     SET
                       found_since = ? ,
                       max_id = ?,
                       min_id = ?,
                       since_id = ?
                     WHERE id = ?'''
            self._conn.execute(sql,
                               [found_since, max_id, min_id, since_id, id, ])
        else:
            sql = '''INSERT INTO search_conditions
                     (id, term, found_since, max_id, min_id, since_id )
                     VALUES(?, ?, ?, ?, ?, ?);'''
            self._conn.execute(sql,
                               [id,
                                term,
                                found_since,
                                max_id,
                                min_id,
                                since_id, ])

    def AppendTweet(self, cond_id, id, text, user_id, createdtime):
        try:
            sql = '''INSERT INTO tweets
                     (id, text, user_id, createdtime)
                     VALUES( ?, ?, ?, ?) ;'''
            self._conn.execute(sql, [id, text, user_id, createdtime, ])
        except sqlite3.IntegrityError:
            print "%d is already inserted." % (id)

        sql = '''INSERT INTO search_results
                 (cond_id, tweet_id)
                 VALUES( ?, ?);'''
        self._conn.execute(sql, [cond_id, id, ])

    def GetTweets(self, cond_id):
        sql = '''SELECT id,text, user_id, createdtime FROM tweets
                     INNER JOIN search_results ON id=tweet_id
                 WHERE cond_id=?;'''
        rows = self._conn.execute(sql, [cond_id, ])
        ret = []
        for r in rows:
            ret.append({'id': r[0],
                        'text': r[1],
                        'user_id': r[2],
                        'createdtime': r[3]})
        return ret

    def Commit(self):
        self._conn.commit()

    def Rollback(self):
        self._conn.rollback()
