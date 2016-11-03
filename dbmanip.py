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
            'insert into {} ({}) values ({})'.format(table,
                columnstr, valuestrQ),
            values
        )


    # ex) db.update('mytable', ['name'], ['tama'], 'where id = 1')
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
        self.__subGenreList = self.select(['id', 'subgenre', 'genre'],
            'subgenre')
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

