from abc import ABCMeta, abstractmethod, abstractproperty
from enum import IntEnum
import tkinter as tk

from tkcommon import QuestionFrame, AnswerTextFrame, EntryFrame
from tkhelper import ListboxIdd
from mojiutil import MojiUtil
from quizdatamanager import QuizDataManager
import validationException as ve



class TypingType(IntEnum):
    Hiragana = 1
    Katakana = 2
    Eisuuji = 3



class AssocType(IntEnum):
    OrderUnknown = 0
    OrderFixed = 1
    Random3 = 2
    Random4 = 3



class Recorder(object, metaclass = ABCMeta):
    def __init__(self, qdManip):
        self._qdManip = qdManip


    @property
    @abstractmethod
    def tabOrder(self): pass


    @property
    @abstractmethod
    def quizName(self): pass


    @abstractmethod
    def recordationFrame(self): pass


    @abstractmethod
    def record(self, comment, stable, pictureId): pass


    @abstractmethod
    def cleanUp(self): pass


    # for Typing, Cube, Effect
    def getTypingTypeAndAnswer(self, rowAnswerList):
        def getTypingType(answer):
            if MojiUtil.isHiragana(answer):
                return TypingType.Hiragana
            elif MojiUtil.isZenkakuKatakana(answer):
                return TypingType.Katakana
            elif answer.encode('utf-8').isalnum():
                return TypingType.Eisuuji
            else:
                raise ve.TypingTypeInconsistError

        answerList = [str.upper(MojiUtil.toHankaku(ans)) for ans in rowAnswerList]
        typingType = None
        for answer in answerList:
            if not answer:
                raise ve.AnswerBlankError
            if len(answer) > 8:
                raise ve.AnswerLengthOverError
            if typingType is None:
                typingType = getTypingType(answer)
                continue
            newTypingType = getTypingType(answer)
            if typingType != newTypingType:
                raise ve.TypingTypeInconsistError
            typingType = newTypingType

        answerStr = '\n'.join(answerList)
        return (typingType, answerStr)



class RecorderOX(Recorder):
    def __init__(self, qdManip):
        super().__init__(qdManip)
        self._answerVar = tk.BooleanVar()
        self._answer = True


    @property
    def tabOrder(self):
        return 1


    @property
    def quizName(self):
        return 'OX'


    @property
    def _answer(self):
        return self._answerVar.get()


    @_answer.setter
    def _answer(self, answer: bool):
        self._answerVar.set(answer)


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        answerFrame = tk.LabelFrame(outerFrame, text = '答え')
        answerFrame.pack()
        trueRb = tk.Radiobutton(answerFrame, text = '○',
            variable = self._answerVar, value = True)
        trueRb.pack(side = tk.LEFT)
        falseRb = tk.Radiobutton(answerFrame, text = '×',
            variable = self._answerVar, value = False)
        falseRb.pack(side = tk.LEFT)

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        self._qdManip.registerOX(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, self._answer,
            comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answer = True



class RecorderFour(Recorder):
    @property
    def tabOrder(self):
        return 2


    @property
    def quizName(self):
        return '四択'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()
        self._dummy1EF = EntryFrame(outerFrame, text = 'ダミー１')
        self._dummy1EF.pack()
        self._dummy2EF = EntryFrame(outerFrame, text = 'ダミー２')
        self._dummy2EF.pack()
        self._dummy3EF = EntryFrame(outerFrame, text = 'ダミー３')
        self._dummy3EF.pack()

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError
        self._qdManip.registerFour(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answer,
            dummy1, dummy2, dummy3, comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()
        self._dummy1EF.deleteEntryText()
        self._dummy2EF.deleteEntryText()
        self._dummy3EF.deleteEntryText()



class RecorderAssoc(Recorder):
    @property
    def tabOrder(self):
        return 3


    @property
    def quizName(self):
        return '連想'


    def recordationFrame(self):
        def onAssocTypeBoxSelect(evt):
            (self._assocTypeId, assocTypeStr) = self._assocTypeBox.selectedIdd
            assocTypeLabel['text'] = assocTypeStr

        assocTypeList = self._qdManip.getAssocTypeList()

        outerFrame = tk.Frame()

        topFrame = tk.Frame(outerFrame)
        topFrame.pack()

        questionFrame = tk.Frame(topFrame)
        questionFrame.pack(side = tk.LEFT)
        self._question1EF = EntryFrame(questionFrame, text = 'ヒント１')
        self._question1EF.pack()
        self._question2EF = EntryFrame(questionFrame, text = 'ヒント２')
        self._question2EF.pack()
        self._question3EF = EntryFrame(questionFrame, text = 'ヒント３')
        self._question3EF.pack()
        self._question4EF = EntryFrame(questionFrame, text = 'ヒント４')
        self._question4EF.pack()

        paddingFrame = tk.Frame(topFrame, width = 50)
        paddingFrame.pack(side = tk.LEFT)

        answerFrame = tk.Frame(topFrame)
        answerFrame.pack(side = tk.LEFT)
        self._answerEF = EntryFrame(answerFrame, text = '答え')
        self._answerEF.pack()
        self._dummy1EF = EntryFrame(answerFrame, text = 'ダミー１')
        self._dummy1EF.pack()
        self._dummy2EF = EntryFrame(answerFrame, text = 'ダミー２')
        self._dummy2EF.pack()
        self._dummy3EF = EntryFrame(answerFrame, text = 'ダミー３')
        self._dummy3EF.pack()

        bottomFrame = tk.LabelFrame(outerFrame, text = '連想タイプ')
        bottomFrame.pack()
        self._assocTypeBox = ListboxIdd(bottomFrame, height = 4)
        self._assocTypeBox.iddList = assocTypeList
        self._assocTypeBox.onSelect = onAssocTypeBoxSelect
        self._assocTypeBox.pack()
        assocTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        assocTypeLabel.pack()

        # initialize
        self._assocTypeBox.select(AssocType.OrderUnknown)

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question1 = self._question1EF.getEntryText()
        question2 = self._question2EF.getEntryText()
        question3 = self._question3EF.getEntryText()
        question4 = self._question4EF.getEntryText()
        for s in (question1, question2, question3, question4):
            if not s: raise ve.QuestionBlankError
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError

        self._qdManip.registerAssoc(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question1, question2, question3, question4,
            answer, dummy1, dummy2, dummy3, self._assocTypeId,
            comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._question1EF.deleteEntryText()
        self._question2EF.deleteEntryText()
        self._question3EF.deleteEntryText()
        self._question4EF.deleteEntryText()
        self._answerEF.deleteEntryText()
        self._dummy1EF.deleteEntryText()
        self._dummy2EF.deleteEntryText()
        self._dummy3EF.deleteEntryText()
        self._assocTypeBox.select(AssocType.OrderUnknown)



class RecorderSort(Recorder):
    @property
    def tabOrder(self):
        return 4


    @property
    def quizName(self):
        return '並べ替え'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answer = self._answerEF.getEntryText()
        if not answer:
            raise ve.AnswerBlankError
        self._qdManip.registerSort(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answer,
            comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()



class RecorderPanel(Recorder):
    @property
    def tabOrder(self):
        return 5


    @property
    def quizName(self):
        return '文字パネル'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        self._panelEF = EntryFrame(outerFrame,
            text = 'パネル（8枚または10枚）')
        self._panelEF.pack()

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError

        answerList = self._answerFrame.answer
        answerLen = None
        for answer in answerList:
            if not answer:
                raise ve.AnswerBlankError
            if answerLen is None:
                answerLen = len(answer)
                continue
            newAnswerLen = len(answer)
            if answerLen != newAnswerLen:
                raise ve.PanelLengthInconsistError
            answerLen = newAnswerLen

        panel = self._panelEF.getEntryText()
        if not len(panel) in (8, 10):
            raise ve.PanelLengthError

        for answer in answerList:
            for c in answer:
                if not c in panel:
                    raise ve.PanelNoAnswerError

        answerStr = '\n'.join(answerList)

        self._qdManip.registerPanel(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answerStr, panel,
            comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerFrame.answer = ''
        self._panelEF.deleteEntryText()



class RecorderSlot(Recorder):
    @property
    def tabOrder(self):
        return 6


    @property
    def quizName(self):
        return 'スロット'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()
        self._dummy1EF = EntryFrame(outerFrame, text = 'ダミー１')
        self._dummy1EF.pack()
        self._dummy2EF = EntryFrame(outerFrame, text = 'ダミー２')
        self._dummy2EF.pack()
        self._dummy3EF = EntryFrame(outerFrame, text = 'ダミー３')
        self._dummy3EF.pack()

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError
        if not (len(answer) == len(dummy1) == len(dummy2) == len(dummy3)):
            raise ve.SlotStrLenError
        self._qdManip.registerSlot(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answer,
            dummy1, dummy2, dummy3, comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()
        self._dummy1EF.deleteEntryText()
        self._dummy2EF.deleteEntryText()
        self._dummy3EF.deleteEntryText()



class RecorderTyping(Recorder):
    @property
    def tabOrder(self):
        return 7


    @property
    def quizName(self):
        return 'タイピング'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        rowAnswerList = self._answerFrame.answer
        (typingtype, answer) = self.getTypingTypeAndAnswer(rowAnswerList)
        self._qdManip.registerTyping(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, typingtype,
            answer, comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerFrame.answer = ''



class RecorderCube(Recorder):
    @property
    def tabOrder(self):
        return 8


    @property
    def quizName(self):
        return 'キューブ'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        rowAnswerList = [self._answerEF.getEntryText()]
        (typingtype, answer) = self.getTypingTypeAndAnswer(rowAnswerList)
        self._qdManip.registerCube(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, typingtype,
            answer, comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()



class RecorderEffect(Recorder):
    @property
    def tabOrder(self):
        return 9


    @property
    def quizName(self):
        return 'エフェクト'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._questionEF = EntryFrame(outerFrame, text = 'エフェクトをかける文字')
        self._questionEF.pack()
        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        return outerFrame


    def record(self, comment, stable, pictureId):
        qdm = QuizDataManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        questionEffect = self._questionEF.getEntryText()
        if not questionEffect:
            raise ve.QuestionBlankError
        if not questionEffect:
            raise ve.AnswerBlankError
        rowAnswerList = self._answerFrame.answer
        (typingtype, answer) = self.getTypingTypeAndAnswer(rowAnswerList)
        self._qdManip.registerEffect(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, questionEffect,
            typingtype, answer, comment, stable, qdm.seriesId, pictureId)


    def cleanUp(self):
        self._questionFrame.question = ''
        self._questionEF.deleteEntryText()
        self._answerFrame.answer = ''

