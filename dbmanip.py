from copy import deepcopy
from functools import reduce
import sqlite3

from util import find


class DBManip(object):
    def __init__(self, filePath):
        self.__filePath = filePath
        self.__conn = sqlite3.connect(self.__filePath)
        self.__crs = self.__conn.cursor()


    def close(self):
        self.__conn.close()


    def save(self):
        self.__conn.commit()


    def execute(self, sql, params = []):
        self.__crs.execute(sql, params)
        return self.__crs.fetchall()


    # ex) db.select(['id', 'name'], 'mytable')
    def select(self, columns, table, cond = '', params = []):
        columnstr = self.__reduceItr(columns)
        return self.execute( 'select %s from %s ' % (columnstr, table) + cond, params)


    # ex) db.insert('mytable', ['id', 'name'], [1, 'mimi'])
    def insert(self, table, columns, values):
        columnstr = self.__reduceItr(columns)
        valuestrQ = (', ?' * len (values))[1:]
        return self.execute(
            'insert into %s (%s) values (%s)' % (table, columnstr, valuestrQ),
            values
        )


    # ['a', 'b', 'c'] -> "a, b, c"
    @staticmethod
    def __reduceItr(itr):
        return reduce(lambda x, y: "%s, %s" % (x, y), itr)


class QuestionDataDBManip(DBManip):
    def __init__(self, filePath):
        super().__init__(filePath)
        self.__genreList = self.select(['id', 'genre'], 'genre')
        self.__subGenreList = self.select(['id', 'subgenre', 'genre'], 'subgenre')
        self.__examGenreList = self.select(['id', 'examgenre'], 'examgenre')
        self.__seriesList = self.select(['id', 'series'], 'series')
        self.__assocTypeList = self.select(['id', 'assoctype'], 'assoctype')


    # [(id, genre)]
    def getGenreList(self):
        return deepcopy(self.__genreList)


    # [(id, subgenre)]
    def getSubGenreList(self):
        return [(i, sg) for (i, sg, g) in self.__subGenreList]


    # [(id, subgenre, genre)]
    def getSubGenreListWithGenre(self):
        return deepcopy(self.__subGenreList)


    # [(id, subgenre)] only for the genre
    def getSubGenreListOnGenre(self, genreId):
        return [(i, sg) for (i, sg, g) in self.__subGenreList if g == genreId]


    def getExamGenreList(self):
        return deepcopy(self.__examGenreList)


    def getSeriesList(self):
        return deepcopy(self.__seriesList)


    def getAssocTypeList(self):
        return deepcopy(self.__assocTypeList)


    def getGenreIdBySubGenreId(self, subGenreId, throw = False):
        return find(lambda x: x[1] == subGenreId, self.__subGenreList, throw)


    def getGenreNameById(self, genreId):
        return [g for (i, g) in self.__genreList if i == genreId][0]


    def getGenreNameBySubGenreId(self, subGenreId):
        try:
            genreId = getGenreIdBySubGenreId(subGenreId, throw = True)
            return getGenreNameById(genreId)
        except ValueError:
            return ''


    def getSubGenreNameById(self, subGenreId):
        return [sg for (i, sg, g) in self.__subGenreList if i == subGenreId][0]


    def getExamGenreNameById(self, examGenreId):
        return [eg for (i, eg) in self.__examGenreList if i == examGenreId][0]


    def getSeriesNameById(self, seriesId):
        return [s for (i, s) in self.__seriesList if i == seriesId][0]


    def registerOX(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            answer: bool, comment: str, stable: bool, seriesId: int,
            pictureId: int):
        self.insert(
            'quiz_ox',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, comment, stable, seriesId, pictureId]
        )


    def registerFour(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str, answer: str,
            dummy1: str, dummy2: str, dummy3: str,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_four',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'dummy1', 'dummy2', 'dummy3',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, dummy1, dummy2, dummy3,
             comment, stable, seriesId, pictureId]
        )


    def registerAssoc(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int,
            question1: str, question2: str, question3: str, question4:str,
            answer: str, dummy1: str, dummy2: str, dummy3: str, assoctype: int,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_assoc',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question1', 'question2', 'question3', 'question4',
             'answer', 'dummy1', 'dummy2', 'dummy3', 'assoctype',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question1, question2, question3, question4,
             answer, dummy1, dummy2, dummy3, assoctype,
             comment, stable, seriesId, pictureId]
        )


    def registerSort(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            answer: str, comment: str, stable: bool, seriesId: int,
            pictureId: int):
        self.insert(
            'quiz_sort',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, comment, stable, seriesId, pictureId]
        )


    def registerPanel(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            answer: str, panel: str, comment: str, stable: bool, seriesId: int,
            pictureId: int):
        self.insert(
            'quiz_panel',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'panel', 'comment', 'stable', 'series',
             'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, panel, comment, stable, seriesId, pictureId]
        )


    def registerSlot(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            answer: str, dummy1: str, dummy2: str, dummy3: str,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_slot',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'dummy1', 'dummy2', 'dummy3',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, dummy1, dummy2, dummy3,
             comment, stable, seriesId, pictureId]
        )


    def registerTyping(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            typingtype: int, answer: str, comment: str, stable: bool,
            seriesId: int, pictureId: int):
        self.insert(
            'quiz_typing',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'typingtype', 'answer', 'comment', 'stable', 'series',
             'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, typingtype, answer, comment, stable, seriesId, pictureId]
        )


    def registerCube(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            typingtype: int, answer: str, comment: str, stable: bool,
            seriesId: int, pictureId: int):
        self.insert(
            'quiz_cube',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'typingtype', 'answer', 'comment', 'stable', 'series',
             'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, typingtype, answer, comment, stable, seriesId, pictureId]
        )


    def registerEffect(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int,
            question: str, questionEffect: str, typingtype: int, answer: str,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_effect',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'questionEffect', 'typingtype',
             'answer', 'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, questionEffect, typingtype,
             answer, comment, stable, seriesId, pictureId]
        )


    def registerOrder(self):
        pass


    def registerConnect(self):
        pass


    def registerMulti(self):
        pass


    def registerGroup(self):
        pass

