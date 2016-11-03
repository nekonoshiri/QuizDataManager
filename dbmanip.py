from copy import deepcopy
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
        columnstr = ','.join(columns)
        return self.execute(
            'select {} from {} {}'.format(columnstr, table, cond),
            params
        )


    # ex) db.insert('mytable', ['id', 'name'], [1, 'mimi'])
    def insert(self, table, columns, values):
        columnstr = ','.join(columns)
        valuestrQ = (', ?' * len (values))[1:]
        return self.execute(
            'insert into {} ({}) values ({})'.format(table, columnstr, valuestrQ),
            values
        )


    # ex) db.update('mytable', ['id', 'name'], [1, 'mimi'])
    def update(self, table, columns, values, cond, params = []):
        setStr = ','.join(
            ['{} = ?'.format(col) for col in columns]
        )
        return self.execute(
            'update {} set {} {}'.format(table, setStr, cond),
            values + params
        )



class QuestionDataDBManip(DBManip):
    def __init__(self, filePath):
        super().__init__(filePath)
        self.__genreList = self.select(['id', 'genre'], 'genre')
        self.__subGenreList = self.select(['id', 'subgenre', 'genre'], 'subgenre')
        self.__examGenreList = self.select(['id', 'examgenre'], 'examgenre')
        self.__seriesList = self.select(['id', 'series'], 'series')
        self.__assocTypeList = self.select(['id', 'assoctype'], 'assoctype')
        self.__multiTypeList = self.select(['id', 'multitype'], 'multitype')


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


    def getMultiTypeList(self):
        return deepcopy(self.__multiTypeList)


    def getGenreIdBySubGenreId(self, subGenreId, throw = False):
        return find(lambda x: x[0] == subGenreId, self.__subGenreList, throw)[2]


    def getGenreNameById(self, genreId):
        return [g for (i, g) in self.__genreList if i == genreId][0]


    def getGenreNameBySubGenreId(self, subGenreId):
        try:
            genreId = self.getGenreIdBySubGenreId(subGenreId, throw = True)
            return self.getGenreNameById(genreId)
        except ValueError:
            return ''


    def getSubGenreNameById(self, subGenreId):
        return [sg for (i, sg, g) in self.__subGenreList if i == subGenreId][0]


    def getExamGenreNameById(self, examGenreId):
        return [eg for (i, eg) in self.__examGenreList if i == examGenreId][0]


    def getSeriesNameById(self, seriesId):
        return [s for (i, s) in self.__seriesList if i == seriesId][0]


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


    def registerOrder(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int,
            question: str, answer: str, multitypeId: int,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_order',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'multitype',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, multitypeId,
             comment, stable, seriesId, pictureId]
        )


    def registerConnect(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            option_left: str, option_right: str, multitypeId: int,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_connect',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'option_left', 'option_right', 'multitype',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, option_left, option_right, multitypeId,
             comment, stable, seriesId, pictureId]
        )


    def registerMulti(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int,
            question: str, answer: str, dummy: str, multitypeId: int,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_multi',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'dummy', 'multitype',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, dummy, multitypeId,
             comment, stable, seriesId, pictureId]
        )


    def registerGroup(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            group1: str, group2: str, group3: str, multitypeId: int,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_group',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'group1', 'group2', 'group3', 'multitype',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, group1, group2, group3, multitypeId,
             comment, stable, seriesId, pictureId]
        )


    def registerFirstcome(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            answer: str, dummy: str, multitypeId: int,
            comment: str, stable: bool, seriesId: int, pictureId: int):
        self.insert(
            'quiz_firstcome',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'answer', 'dummy', 'multitype',
             'comment', 'stable', 'series', 'picture_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, answer, dummy, multitypeId,
             comment, stable, seriesId, pictureId]
        )


    def registerImagetouch(self, subGenreId: int, examGenreId: int,
            difficulty_min: int, difficulty_max: int, question: str,
            comment: str, stable: bool, seriesId: int,
            pictureId: int, picture_answer_id: int):
        self.insert(
            'quiz_imagetouch',
            ['subgenre', 'examgenre', 'difficulty_min', 'difficulty_max',
             'question', 'comment', 'stable', 'series',
             'picture_id', 'picture_answer_id'],
            [subGenreId, examGenreId, difficulty_min, difficulty_max,
             question, comment, stable, seriesId,
             pictureId, picture_answer_id]
        )

