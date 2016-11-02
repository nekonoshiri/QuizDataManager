# QuizDataManager

Quiz data manager with python

# 必要なもの

- python3 と 標準ライブラリ
- sqlite3


# 最初になにをする

1. sqlite3 データベースを作る

main.py と同じ場所に question_data.sqlite3 を作る

```
$ sqlite3 question_data.sqlite3
```

1. データベースの初期化

initializedatabase.py の initializeDatabase() を実行

```py
$ python3
>>> import initializedatabase
>>> initializedatabase.initializeDatabase()
done initialize
```

# 使い方

```
$ python3 main.py
```
