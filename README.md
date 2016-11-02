# QuizDataManager

Quiz data manager with python

# これはなに

クイズのゲームのデータを集めるのにつかえる

# 必要なもの

- python3 と 標準ライブラリ
- (sqlite3)


# 最初になにをする

1. データベースの初期化

initializedatabase.py の initializeDatabase() を実行

すると question_data.sqlite3 というデータベースが作られる

```py
$ python3
>>> import initializedatabase
>>> initializedatabase.initializeDatabase()
done initialize
>>> quit()
```

# 使い方

```
$ python3 main.py
```
