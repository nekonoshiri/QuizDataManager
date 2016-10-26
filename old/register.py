from abc import ABCMeta, abstractmethod
from enum import Enum

from dbmanip import QuestionDataDBManip
from interactive import ItraWithQD


class Register (metaclass = ABCMeta):
    def __init__ (self, genreId, subGenreId, examGenreId):
        self._genreId = genreId
        self._subGenreId = subGenreId
        self._examGenreId = examGenreId

    def __registerCommon (self, qdManip):
        (self._difficulty_min, self._difficulty_max) = ItraWithQD.inputDifficulty ()
        self._stable = ItraWithQD.inputStable ()
        (self._seriesId, self._seriesStr) = ItraWithQD (qdManip).inputSeries ()

    @abstractmethod
    def _registerPeculiar (self):
        pass

    @abstractmethod
    def _registerConfirm (self, qdManip):
        return True

    @abstractmethod
    def _registerDB(self, qdManip):
        pass

    def registerMain (self, qdManip):
        self._registerPeculiar ()
        self.__registerCommon (qdManip)
        if self._registerConfirm (qdManip):
            self._registerDB (qdManip)
            qdManip.save ()


class RegisterOX (Register):
    def _registerPeculiar (self):
        self._question = ItraWithQD.inputQuestion ()
        self._answer = ItraWithQD.inputBool ('クイズの答えを入力してね')
        self._comment = ItraWithQD.inputComment ()

    def _registerConfirm (self, qdManip):
        print ('以下のデータを登録するよ！')
        print ('ジャンル:', qdManip.getGenreNameById (self._genreId))
        print ('サブジャンル:', qdManip.getSubGenreNameById (self._subGenreId))
        print ('検定ジャンル:', qdManip.getExamGenreNameById (self._examGenreId))
        print ('形式: OX')
        print ('問題:', self._question)
        print ('答え:', 'まる' if self._answer else 'ばつ')
        print ('コメント:', self._comment)
        if self._difficulty_min == self._difficulty_max:
            print ('難易度:', self._difficulty_min)
        else:
            print ('難易度: %s 〜 %s' % (self._difficulty_min, self._difficulty_max))
        print ('安定性:', '安定' if self._stable else '不安定')
        print ('シリーズ:', qdManip.getSeriesNameById (self._seriesId))
        return ItraWithQD.inputBool ('登録する？')

    def _registerDB (self, qdManip):
        qdManip.registerOX (self._subGenreId, self._examGenreId,
            self._difficulty_min, self._difficulty_max,
            self._question, self._answer, self._comment,
            self._stable, self._seriesId)


class QuizType (Enum):
    OX = RegisterOX

