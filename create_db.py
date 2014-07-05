#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from twitter_db import TwitterDb


def main(argvs, argc):
    """
    このスクリプトでツイッターの情報を記録するデータベースを作成します
    """
    if(argc != 2):
        print "Usage #python %s dbname" % argvs[0]
        return -1

    dbname = argvs[1]
    if os.path.exists(dbname):
        print dbname, " already exists."
        return -1

    db = TwitterDb(dbname)
    db.create_db()
    print db.dbpath, " is created."

    return 0

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
