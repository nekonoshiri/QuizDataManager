from enum import IntEnum

from inputAux import InputLoop

class Interactive:
    class __MyInputLoop (InputLoop):
        _defaultPrompt = '> '
        def _defaultShaping (self,ipt):
            return ipt.strip ()

    def __init__ (self):
        pass

    # list index function (interactive)
    @classmethod
    def index (cls, lst, showFunc = lambda x: x, startIx = 1):
        (minIx, maxIx) = (startIx, startIx + len (lst) - 1)
        i = startIx
        for cont in lst:
            print ("%s: %s" % (i, showFunc (cont)))
            i += 1
        inputLoop = cls.__MyInputLoop ()
        inputLoop.shaping = lambda ipt: int (ipt.strip())
        inputLoop.validation = lambda x: minIx <= x <= maxIx
        inputLoop.interval = lambda x: print (
            '%s .. %s の数字を入力してね！' % (minIx, maxIx))
        return lst[inputLoop.inputLoop () - minIx]

    # for input String
    @classmethod
    def inputString (cls, printStr):
        print (printStr)
        return cls.__MyInputLoop ().input ()

    # for input Bool
    @classmethod
    def inputBool (cls, printStr):
        print (printStr)
        print ('t: True')
        print ('f: False')
        inputLoop = cls.__MyInputLoop ()
        inputLoop.validation = lambda x: x in ('t', 'f')
        inputLoop.interval = lambda x: print ('t か f を入力して！')
        return True if inputLoop.inputLoop () == 't' else False


class ItraWithQD (Interactive):
    # table 'genre'
    class GenreConst (IntEnum):
        GENRE_UNKNOWN = 0
        NONGENRE      = 1
        EXAM          = 9

    # table 'subgenre'
    class SubGenreConst (IntEnum):
        SUBGENRE_UNKNOWN = 0
        NONGENRE         = 1

    # table 'examgenre'
    class ExamGenreConst (IntEnum):
        NOEXAM = 1

    def __init__ (self, qdManip):
        self.__qdManip = qdManip

    # return genreId
    def inputGenre (self):
        print ('どのジャンルの問題を登録するの？')
        genreList = self.__qdManip.getGenreList ()
        (genreId, _) = self.index (genreList, lambda x: x[1])
        return genreId

    # return subGenreId
    def inputSubGenre (self, genreId):
        if genreId == self.GenreConst.GENRE_UNKNOWN:
            return self.SubGenreConst.SUBGENRE_UNKNOWN
        elif genreId == self.GenreConst.NONGENRE:
            return self.SubGenreConst.NONGENRE
        elif genreId == self.GenreConst.EXAM:
            return self.SubGenreConst.SUBGENRE_UNKNOWN
        else:
            print ('どのサブジャンルの問題を登録するの？')
            subGenreList = self.__qdManip.getSubGenreListOnGenre (genreId)
            (subGenreId, _) = self.index (subGenreList, lambda x: x[1])
            return subGenreId

    # return examGenreId
    def inputExamGenre (self, genreId):
        if genreId == self.GenreConst.EXAM:
            print ('どの検定の問題を登録するの？')
            examGenreList = self.__qdManip.getExamGenreList ()
            (examGenreId, _) = self.index (examGenreList, lambda x: x[1])
            return examGenreId
        else:
            return self.ExamGenreConst.NOEXAM

    # return the sub class of Register
    @classmethod
    def inputQuizType (cls, quizTypeList):
        print ('どの形式の問題を登録するの？')
        quizType = cls.index (quizTypeList, lambda x: x.name)
        return quizType.value

    #return question
    @classmethod
    def inputQuestion (cls):
        return cls.inputString ('問題を入力してね')

    # return comment
    @classmethod
    def inputComment (cls):
        return cls.inputString ('コメントを入力してね')

    # return (difficulty_min, difficulty_max)
    @classmethod
    def inputDifficulty (cls):
        difficulty = [1, 2, 3, 4, 5]
        print ('難易度の最小値を入力してね')
        difficulty_min = cls.index (difficulty)
        print ('難易度の最大値を入力してね')
        difficulty2 = [i for i in difficulty if difficulty_min <= i]
        difficulty_max = cls.index (difficulty2, startIx = difficulty_min)
        return (difficulty_min, difficulty_max)

    # return (seriesId, seriesStr)
    def inputSeries (self):
        print ('問題を回収したシリーズを入力してね（複数ある場合は最新のもの）')
        seriesList = self.__qdManip.getSeriesList ()
        return self.index (seriesList, lambda x: x[1], 0)

    # return stable
    @classmethod
    def inputStable (cls):
        return cls.inputBool (
            '安定性を入力してね（将来変更されることが無さそうであれば t）'
        )

    @classmethod
    def inputForContinue (cls, continueList):
        return cls.index (continueList, lambda x: x.value, 0)
