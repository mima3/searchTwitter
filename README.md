searchTwitter
==========
ツイッターを検索して、その結果をDBに保存するスクリプトです。

動作環境
------
Python2.7  
下記のライブラリをインストール済み  
・python_twitter  
・python-dateutil  

### インストールの例 ###
    easy_install python_twitter
    easy_install python-dateutil



使い方
------
1. 下記のURLにアクセスしてAPIキーを取得して、その値をtwitter.iniに記述します。  
https://apps.twitter.com/

twitter.ini.originalをtwitter.iniに変更してAPIを入力してください。


2. 記録用のDBを作成します。  

    python create_db.py test.sqlite


3. 検索を行い、その結果をDBに記録する

    python search_twitter.py test.sqlite "needtec" 0

第一引数：データベースへのパス  
第二引数：検索文字  
第三引数：since_id・・・このIDより大きいツイートを検索する  

現状のスクリプトではWindows(日本語)でしか動作しない。  
search_twitter.pyの35行目をコメントアウトすることでWindows以外でも動作する。

```
    # もし、UTF-8のターミナルなら以下の行はコメントアウトする
    term = unicode(term, 'cp932').encode('utf-8')
```


テーブルの説明
------
### search_conditions ###
検索条件を記録するテーブル

|列名|型|説明|
|---|---|---|
|id|INTEGER|一意のID|
|term|TEXT|検索に使用する文字|
|found_since|INTEGER|1の場合はsince_idまで検索済み|
|max_id|INTEGER|検索されたツイートIDの最大|
|min_id|INTEGER|検索されたツイートIDの最小|
|since_id|INTEGER|検索時に指定した開始ID。このID以降のものを検索する|

### tweets ###
ツイートを記録するテーブル

|列名|型|説明|
|---|---|---|
|id|INTEGER|一意のID|
|text|TEXT|ツイートの内容|
|user_id|INTEGER|ユーザーID|
|createdtime|INTEGER|ツイートしたタイムスタンプ|


### search_results ###
検索条件とツイートの関連付けテーブル

|列名|型|説明|
|---|---|---|
|id|INTEGER|一意のID|
|cond_id|INTEGER|search_conditionsのID|
|tweet_id|INTEGER|tweetsのID|

