from abc import ABCMeta, abstractmethod, abstractproperty
from enum import IntEnum
import tkinter as tk

from tkcommon import QuestionFrame, AnswerTextFrame, EntryFrame
from tkhelper import ListboxIdd
from mojiutil import MojiUtil
from quizdatamanager import RecordMode
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



class MultiType(IntEnum):
    Unknown = 0
    Fixed = 1
    Unfixed = 2



def recorder(cls):
    '''decorator: register RecorderXXXX to Recorder.RecorderList'''
    Recorder.RecorderList.append(cls)
    return cls



class Recorder(object, metaclass = ABCMeta):
    RecorderList = []


    def __init__(self, qdManip, qdManager):
        self._qdManip = qdManip
        self._qdManager = qdManager
        self._recordMode = RecordMode.Insert


    @property
    @abstractmethod
    def quizName(self): pass


    @property
    @abstractmethod
    def tableName(self): pass


    @abstractmethod
    def recordationFrame(self): pass


    @abstractmethod
    def record(self): pass


    @abstractmethod
    def edit(self, quizId): pass


    @abstractmethod
    def search(self): pass


    @abstractmethod
    def cleanUp(self): pass


    def getQuizData(self, quizId):
        return self._qdManip.select(['*'], self.tableName,
            'where id = ?', [quizId])[0]


    def editCommon(self, quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId):
        qdm = self._qdManager
        genreId = self._qdManip.getGenreIdBySubGenreId(subGenreId)
        qdm.genreId = genreId
        qdm.subGenreId = subGenreId
        qdm.examGenreId = examGenreId
        qdm.difficulty_min = difficulty_min
        qdm.difficulty_max = difficulty_max
        qdm.comment = comment
        qdm.stable = stable
        qdm.seriesId = seriesId
        qdm.pictureId = pictureId
        qdm.setRecordMode(RecordMode.Update, quizId)


    # for Typing, Cube, Effect
    def getTypingTypeAndAnswer(self, rowAnswerList):
        def getTypingType(answer):
            if MojiUtil.isHiragana(answer, onbiki = True):
                return TypingType.Hiragana
            elif MojiUtil.isZenkakuKatakana(answer, onbiki = True):
                return TypingType.Katakana
            elif answer.encode('utf-8').isalnum():
                return TypingType.Eisuuji
            else:
                raise ve.TypingTypeInconsistError

        answerList = [str.upper(MojiUtil.toHankaku(ans)) for ans in rowAnswerList]
        if not answerList:
            raise ve.AnswerBlankError
        typingType = getTypingType(answerList[0])
        for answer in answerList:
            if len(answer) > 8:
                raise ve.AnswerLengthOverError
            newTypingType = getTypingType(answer)
            if typingType != newTypingType:
                raise ve.TypingTypeInconsistError
            typingType = newTypingType

        answerStr = '\n'.join(answerList)
        return (typingType, answerStr)


    #for search
    def selectFromJoinedTable(self, table, columns, cond = '', params = [],
            assocType = False, multiType = False):
        joinedTable = '''(((({0}
        inner join subgenre on {0}.subgenre = subgenre.id)
        inner join genre on subgenre.genre = genre.id)
        inner join examgenre on {0}.examgenre = examgenre.id)
        inner join stable on {0}.stable = stable.id)
        inner join series on {0}.series = series.id
        '''.format(table)
        if assocType:
            joinedTable = '''
            ({0}) inner join assoctype on {1}.assoctype = assoctype.id
            '''.format(joinedTable, table)
        if multiType:
            joinedTable = '''
            ({0}) inner join multitype on {1}.multitype = multitype.id
            '''.format(joinedTable, table)
        return self._qdManip.select(columns, joinedTable, cond, params)


@recorder
class RecorderOX(Recorder):
    class Answer(IntEnum):
        Undefined = -1
        AnswerFalse = 0
        AnswerTrue = 1


    def __init__(self, qdManip, qdManager):
        super().__init__(qdManip, qdManager)
        self._answerVar = tk.IntVar()
        self._answer = self.Answer.Undefined


    @property
    def quizName(self):
        return 'OX'


    @property
    def tableName(self):
        return 'quiz_ox'


    @property
    def _answer(self):
        return int(self._answerVar.get())


    @_answer.setter
    def _answer(self, answer):
        self._answerVar.set(int(answer))


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        answerFrame = tk.LabelFrame(outerFrame, text = '答え')
        answerFrame.pack()
        trueRb = tk.Radiobutton(answerFrame, text = '○',
            variable = self._answerVar,
            value = int(self.Answer.AnswerTrue))
        trueRb.pack(side = tk.LEFT)
        falseRb = tk.Radiobutton(answerFrame, text = '×',
            variable = self._answerVar,
            value = int(self.Answer.AnswerFalse))
        falseRb.pack(side = tk.LEFT)

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answer = self._answer
        if answer == self.Answer.Undefined:
            raise ve.AnswerBlankError
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answer = answer
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限',
            '問題', '答え', 'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                "replace(replace(answer, 1, '○'), 0, '×')",
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            "where question like '%{}%'".format(questionHead)
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answer = self.Answer.Undefined



@recorder
class RecorderFour(Recorder):
    @property
    def quizName(self):
        return '四択'


    @property
    def tableName(self):
        return 'quiz_four'


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


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer', 'dummy1', 'dummy2', 'dummy3',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answer, dummy1, dummy2, dummy3,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, dummy1, dummy2, dummy3, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerEF.setEntryText(answer)
        self._dummy1EF.setEntryText(dummy1)
        self._dummy1EF.setEntryText(dummy2)
        self._dummy1EF.setEntryText(dummy3)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if any((answer, dummy1, dummy2, dummy3)):
            l = [
                "answer = '{}'", "dummy1 = '{}'",
                "dummy2 = '{}'", "dummy3 = '{}'"
            ]
            for s in l:
                condList.extend([
                    s.format(answer), s.format(dummy1),
                    s.format(dummy2), s.format(dummy3)
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題',
            '答え', 'ダミー１', 'ダミー２', 'ダミー３',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                'answer', 'dummy1', 'dummy2', 'dummy3',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()
        self._dummy1EF.deleteEntryText()
        self._dummy2EF.deleteEntryText()
        self._dummy3EF.deleteEntryText()



@recorder
class RecorderAssoc(Recorder):
    @property
    def quizName(self):
        return '連想'


    @property
    def tableName(self):
        return 'quiz_assoc'


    def recordationFrame(self):
        def onAssocTypeBoxSelect(evt):
            (self._assocTypeId, assocTypeStr) = self._assocTypeBox.selectedIdd
            assocTypeLabel['text'] = assocTypeStr

        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        answerFrame = tk.Frame(outerFrame)
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
        bottomFrame.pack(side = tk.LEFT)
        self._assocTypeBox = ListboxIdd(bottomFrame, height = 4)
        self._assocTypeBox.iddList = self._qdManip.getAssocTypeList()
        self._assocTypeBox.onSelect = onAssocTypeBoxSelect
        self._assocTypeBox.pack()
        assocTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        assocTypeLabel.pack()

        # initialize
        self._assocTypeBox.select(AssocType.OrderUnknown)

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        if question.count('\n') > 3:
            raise ve.AssocLengthError
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer', 'dummy1', 'dummy2', 'dummy3', 'assoctype',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answer, dummy1, dummy2, dummy3, self._assocTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, dummy1, dummy2, dummy3, assoctype,
            comment, stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerEF.setEntryText(answer)
        self._dummy1EF.setEntryText(dummy1)
        self._dummy2EF.setEntryText(dummy2)
        self._dummy3EF.setEntryText(dummy3)
        self._assocTypeBox.select(assoctype)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()

        condList = []
        if question:
            for q in question.split('\n'):
                condList.append("question like '%{}%'".format(q))

        if any((answer, dummy1, dummy2, dummy3)):
            l = [
                "answer = '{}'", "dummy1 = '{}'",
                "dummy2 = '{}'", "dummy3 = '{}'"
            ]
            for s in l:
                condList.extend([
                    s.format(answer), s.format(dummy1),
                    s.format(dummy2), s.format(dummy3)
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限',
            '問題', '答え', 'ダミー１', 'ダミー２', 'ダミー３',
            '連想タイプ',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'answer', 'dummy1', 'dummy2', 'dummy3',
                'assoctype.assoctype',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond,
            assocType = True
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()
        self._dummy1EF.deleteEntryText()
        self._dummy2EF.deleteEntryText()
        self._dummy3EF.deleteEntryText()
        self._assocTypeBox.select(AssocType.OrderUnknown)



@recorder
class RecorderSort(Recorder):
    @property
    def quizName(self):
        return '並替'


    @property
    def tableName(self):
        return 'quiz_sort'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answer = self._answerEF.getEntryText()
        if not answer:
            raise ve.AnswerBlankError
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerEF.setEntryText(answer)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        answer = self._answerEF.getEntryText()

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if answer:
            condList.append("answer = '{}'".format(answer))
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'answer',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()



@recorder
class RecorderPanel(Recorder):
    @property
    def quizName(self):
        return '文字パネ'


    @property
    def tableName(self):
        return 'quiz_panel'


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


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError

        answerList = self._answerFrame.answer
        if not answerList:
            raise ve.AnswerBlankError
        answerLen = len(answerList[0])
        for answer in answerList:
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

        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer', 'panel',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answerStr, panel,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, panel, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerFrame.answer = answer
        self._panelEF.setEntryText(panel)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        answerList = self._answerFrame.answer

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if answerList:
            for answer in answerList:
                condList.extend([
                    s.format(answer) for s in
                    [
                        "answer like '%\n{0}\n%'", "answer like '{0}\n%'",
                        "answer like '%\n{0}'", "answer like '{0}'"
                    ]
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え', 'パネル',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'answer', 'panel',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerFrame.answer = ''
        self._panelEF.deleteEntryText()



@recorder
class RecorderSlot(Recorder):
    @property
    def quizName(self):
        return 'スロット'


    @property
    def tableName(self):
        return 'quiz_slot'


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


    def record(self, quizId = None):
        qdm = self._qdManager
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
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer', 'dummy1', 'dummy2', 'dummy3',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answer, dummy1, dummy2, dummy3,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, dummy1, dummy2, dummy3,
            comment, stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerEF.setEntryText(answer)
        self._dummy1EF.setEntryText(dummy1)
        self._dummy2EF.setEntryText(dummy2)
        self._dummy3EF.setEntryText(dummy3)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if any((answer, dummy1, dummy2, dummy3)):
            l = [
                "answer = '{}'", "dummy1 = '{}'",
                "dummy2 = '{}'", "dummy3 = '{}'"
            ]
            for s in l:
                condList.extend([
                    s.format(answer), s.format(dummy1),
                    s.format(dummy2), s.format(dummy3)
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題',
            '答え', 'ダミー１', 'ダミー２', 'ダミー３',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                'answer', 'dummy1', 'dummy2', 'dummy3',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()
        self._dummy1EF.deleteEntryText()
        self._dummy2EF.deleteEntryText()
        self._dummy3EF.deleteEntryText()



@recorder
class RecorderTyping(Recorder):
    @property
    def quizName(self):
        return 'タイピ'


    @property
    def tableName(self):
        return 'quiz_typing'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        rowAnswerList = self._answerFrame.answer
        (typingtype, answer) = self.getTypingTypeAndAnswer(rowAnswerList)
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'typingtype', 'answer',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, typingtype, answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, _, answer, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerFrame.answer = answer
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        rowAnswerList = self._answerFrame.answer
        answerList = [str.upper(MojiUtil.toHankaku(ans)) for ans in rowAnswerList]

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if answerList:
            for answer in answerList:
                condList.extend([
                    s.format(answer) for s in
                    [
                        "answer like '%\n{0}\n%'", "answer like '{0}\n%'",
                        "answer like '%\n{0}'", "answer like '{0}'"
                    ]
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'answer',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerFrame.answer = ''



@recorder
class RecorderCube(Recorder):
    @property
    def quizName(self):
        return 'キューブ'


    @property
    def tableName(self):
        return 'quiz_cube'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        rowAnswerList = [self._answerEF.getEntryText()]
        (typingtype, answer) = self.getTypingTypeAndAnswer(rowAnswerList)
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'typingtype', 'answer',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, typingtype, answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, _, answer, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerEF.setEntryText(answer)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        rowAnswer = self._answerEF.getEntryText()
        answer = str.upper(MojiUtil.toHankaku(rowAnswer))

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if answer:
            condList.append("answer = '{}'".format(answer))
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'answer',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerEF.deleteEntryText()



@recorder
class RecorderEffect(Recorder):
    @property
    def quizName(self):
        return 'エフェ'


    @property
    def tableName(self):
        return 'quiz_effect'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._questionEF = EntryFrame(outerFrame, text = 'エフェクトをかける文字')
        self._questionEF.pack()
        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
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
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'questionEffect', 'typingtype', 'answer',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, questionEffect, typingtype, answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, questionEffect, _, answer, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._questionEF.setEntryText(questionEffect)
        self._answerFrame.answer = answer
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        questionEffect = self._questionEF.getEntryText()
        rowAnswerList = self._answerFrame.answer
        answerList = [str.upper(MojiUtil.toHankaku(ans)) for ans in rowAnswerList]

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if questionEffect:
            condList.append("questionEffect = '{}'".format(questionEffect))
        if answerList:
            for answer in answerList:
                condList.extend([
                    s.format(answer) for s in
                    [
                        "answer like '%\n{0}\n%'", "answer like '{0}\n%'",
                        "answer like '%\n{0}'", "answer like '{0}'"
                    ]
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '文字', '答え',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'questionEffect', 'answer',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._questionEF.deleteEntryText()
        self._answerFrame.answer = ''



@recorder
class RecorderOrder(Recorder):
    @property
    def quizName(self):
        return '順当'


    @property
    def tableName(self):
        return 'quiz_order'


    def recordationFrame(self):
        def onMultiTypeBoxSelect(evt):
            (self._multiTypeId, multiTypeStr) = self._multiTypeBox.selectedIdd
            multiTypeLabel['text'] = multiTypeStr

        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        bottomFrame = tk.LabelFrame(outerFrame, text = '問題タイプ')
        bottomFrame.pack()
        self._multiTypeBox = ListboxIdd(bottomFrame, height = 3)
        self._multiTypeBox.iddList = self._qdManip.getMultiTypeList()
        self._multiTypeBox.onSelect = onMultiTypeBoxSelect
        self._multiTypeBox.pack()
        multiTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        multiTypeLabel.pack()

        # initialize
        self._multiTypeBox.select(MultiType.Unknown)

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answerList = self._answerFrame.answer
        if not answerList:
            raise ve.AnswerBlankError
        answerStr = '\n'.join(answerList)
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer', 'multitype',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answerStr, self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, multitype, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerFrame.answer = answer
        self._multiTypeBox.select(multitype)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        answerList = self._answerFrame.answer
        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if answerList:
            for answer in answerList:
                condList.extend([
                    s.format(answer) for s in
                    [
                        "answer like '%\n{0}\n%'", "answer like '{0}\n%'",
                        "answer like '%\n{0}'", "answer like '{0}'"
                    ]
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え', '問題タイプ',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'answer', 'multitype.multitype',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond,
            multiType = True
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerFrame.answer = ''
        self._multiTypeBox.select(MultiType.Unknown)



@recorder
class RecorderConnect(Recorder):
    @property
    def quizName(self):
        return '線結'


    @property
    def tableName(self):
        return 'quiz_connect'


    def recordationFrame(self):
        def onMultiTypeBoxSelect(evt):
            (self._multiTypeId, multiTypeStr) = self._multiTypeBox.selectedIdd
            multiTypeLabel['text'] = multiTypeStr

        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        topFrame = tk.Frame(outerFrame)
        topFrame.pack()
        self._optionLeftFrame = AnswerTextFrame(topFrame)
        self._optionLeftFrame['text'] = '左選択肢'
        self._optionLeftFrame.answerText['width'] = 40
        self._optionLeftFrame.pack(side = tk.LEFT)
        self._optionRightFrame = AnswerTextFrame(topFrame)
        self._optionRightFrame['text'] = '右選択肢'
        self._optionRightFrame.answerText['width'] = 40
        self._optionRightFrame.pack(side = tk.LEFT)

        bottomFrame = tk.LabelFrame(outerFrame, text = '問題タイプ')
        bottomFrame.pack()
        self._multiTypeBox = ListboxIdd(bottomFrame, height = 3)
        self._multiTypeBox.iddList = self._qdManip.getMultiTypeList()
        self._multiTypeBox.onSelect = onMultiTypeBoxSelect
        self._multiTypeBox.pack()
        multiTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        multiTypeLabel.pack()

        # initialize
        self._multiTypeBox.select(MultiType.Unknown)

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        optionLeft = self._optionLeftFrame.answer
        optionRight = self._optionRightFrame.answer
        if (not optionLeft) or (not optionRight):
            raise ve.AnswerBlankError
        optionLeftStr = '\n'.join(optionLeft)
        optionRightStr = '\n'.join(optionRight)
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'option_left', 'option_right', 'multitype',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, optionLeftStr, optionRightStr, self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, option_left, option_right, multitype, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._optionLeftFrame.answer = option_left
        self._optionRightFrame.answer = option_right
        self._multiTypeBox.select(multitype)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        optionLeftList = self._optionLeftFrame.answer
        optionRightList = self._optionRightFrame.answer
        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if optionLeftList:
            for optL in optionLeftList:
                condList.extend([
                    s.format(optL) for s in
                    [
                        "option_left like '%\n{0}\n%'",
                        "option_left like '{0}\n%'",
                        "option_left like '%\n{0}'",
                        "option_left like '{0}'"
                    ]
                ])
        if optionRightList:
            for optR in optionRightList:
                condList.extend([
                    s.format(optR) for s in
                    [
                        "option_right like '%\n{0}\n%'",
                        "option_right like '{0}\n%'",
                        "option_right like '%\n{0}'",
                        "option_right like '{0}'"
                    ]
                ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '左選択肢', '右選択肢', '問題タイプ',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                'option_left', 'option_right', 'multitype.multitype',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond,
            multiType = True
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._optionLeftFrame.answer = ''
        self._optionRightFrame.answer = ''
        self._multiTypeBox.select(MultiType.Unknown)



@recorder
class RecorderMulti(Recorder):
    @property
    def quizName(self):
        return '多答'


    @property
    def tableName(self):
        return 'quiz_multi'


    def recordationFrame(self):
        def onMultiTypeBoxSelect(evt):
            (self._multiTypeId, multiTypeStr) = self._multiTypeBox.selectedIdd
            multiTypeLabel['text'] = multiTypeStr

        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        topFrame = tk.Frame(outerFrame)
        topFrame.pack()
        self._answerFrame = AnswerTextFrame(topFrame)
        self._answerFrame['text'] = '答え'
        self._answerFrame.answerText['width'] = 40
        self._answerFrame.pack(side = tk.LEFT)
        self._dummyFrame = AnswerTextFrame(topFrame)
        self._dummyFrame['text'] = 'ダミー'
        self._dummyFrame.answerText['width'] = 40
        self._dummyFrame.pack(side = tk.LEFT)

        bottomFrame = tk.LabelFrame(outerFrame, text = '問題タイプ')
        bottomFrame.pack()
        self._multiTypeBox = ListboxIdd(bottomFrame, height = 3)
        self._multiTypeBox.iddList = self._qdManip.getMultiTypeList()
        self._multiTypeBox.onSelect = onMultiTypeBoxSelect
        self._multiTypeBox.pack()
        multiTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        multiTypeLabel.pack()

        # initialize
        self._multiTypeBox.select(MultiType.Unknown)

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answerList = self._answerFrame.answer
        dummyList = self._dummyFrame.answer
        if (not answerList) and (not dummyList):
            raise ve.AnswerBlankError
        answerStr = '\n'.join(answerList)
        dummyStr = '\n'.join(dummyList)
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer', 'dummy', 'multitype',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answerStr, dummyStr, self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, dummy, multitype, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerFrame.answer = answer
        self._dummyFrame.answer = dummy
        self._multiTypeBox.select(multitype)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        answerList = self._answerFrame.answer
        dummyList = self._dummyFrame.answer
        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if answerList:
            for answer in answerList:
                for column in ('answer', 'dummy'):
                    condList.extend([
                        s.format(column, answer) for s in
                        [
                            "{0} like '%\n{1}\n%'", "{0} like '{1}\n%'",
                            "{0} like '%\n{1}'", "{0} like '{1}'"
                        ]
                    ])
        if dummyList:
            for dummy in dummyList:
                for column in ('answer', 'dummy'):
                    condList.extend([
                        s.format(column, dummy) for s in
                        [
                            "{0} like '%\n{1}\n%'", "{0} like '{1}\n%'",
                            "{0} like '%\n{1}'", "{0} like '{1}'"
                        ]
                    ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え', 'ダミー', '問題タイプ',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                'answer', 'dummy', 'multitype.multitype',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond,
            multiType = True
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerFrame.answer = ''
        self._dummyFrame.answer = ''
        self._multiTypeBox.select(MultiType.Unknown)



@recorder
class RecorderGroup(Recorder):
    @property
    def quizName(self):
        return 'グル分け'


    @property
    def tableName(self):
        return 'quiz_group'


    def recordationFrame(self):
        def onMultiTypeBoxSelect(evt):
            (self._multiTypeId, multiTypeStr) = self._multiTypeBox.selectedIdd
            multiTypeLabel['text'] = multiTypeStr

        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        topFrame = tk.LabelFrame(outerFrame,
            text = '各グループの一行目はグループ名（ヘッダ）')
        topFrame.pack()
        self._group1Frame = AnswerTextFrame(topFrame)
        self._group1Frame['text'] = 'グループ１'
        self._group1Frame.answerText['width'] = 30
        self._group1Frame.pack(side = tk.LEFT)
        self._group2Frame = AnswerTextFrame(topFrame)
        self._group2Frame['text'] = 'グループ２'
        self._group2Frame.answerText['width'] = 30
        self._group2Frame.pack(side = tk.LEFT)
        self._group3Frame = AnswerTextFrame(topFrame)
        self._group3Frame['text'] = 'グループ３'
        self._group3Frame.answerText['width'] = 30
        self._group3Frame.pack(side = tk.LEFT)

        bottomFrame = tk.LabelFrame(outerFrame, text = '問題タイプ')
        bottomFrame.pack()
        self._multiTypeBox = ListboxIdd(bottomFrame, height = 3)
        self._multiTypeBox.iddList = self._qdManip.getMultiTypeList()
        self._multiTypeBox.onSelect = onMultiTypeBoxSelect
        self._multiTypeBox.pack()
        multiTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        multiTypeLabel.pack()

        # initialize
        self._multiTypeBox.select(MultiType.Unknown)

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        group1List = self._group1Frame.answer
        group2List = self._group2Frame.answer
        group3List = self._group3Frame.answer
        if (group1List, group2List, group3List).count([]) >= 2:
            raise ve.AnswerBlankError
        group1Str = '\n'.join(group1List)
        group2Str = '\n'.join(group2List)
        group3Str = '\n'.join(group3List)
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'group1', 'group2', 'group3', 'multitype',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, group1Str, group2Str, group3Str, self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, group1, group2, group3, multitype, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._group1Frame.answer = group1
        self._group2Frame.answer = group2
        self._group3Frame.answer = group3
        self._multiTypeBox.select(multitype)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        group1List = self._group1Frame.answer
        group2List = self._group2Frame.answer
        group3List = self._group3Frame.answer
        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        for groupList in (group1List, group2List, group3List):
            if not groupList:
                continue
            for groupItem in groupList:
                for column in ('group1', 'group2', 'group3'):
                    condList.extend([
                        s.format(column, groupItem) for s in
                        [
                            "{0} like '%\n{1}\n%'", "{0} like '{1}\n%'",
                            "{0} like '%\n{1}'", "{0} like '{1}'"
                        ]
                    ])

        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題',
            'グループ１', 'グループ２', 'グループ３', '問題タイプ',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                'group1', 'group2', 'group3', 'multitype.multitype',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond,
            multiType = True
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._group1Frame.answer = ''
        self._group2Frame.answer = ''
        self._group3Frame.answer = ''
        self._multiTypeBox.select(MultiType.Unknown)



@recorder
class RecorderFirstcome(Recorder):
    @property
    def quizName(self):
        return '早勝ち'


    @property
    def tableName(self):
        return 'quiz_firstcome'


    def recordationFrame(self):
        def onMultiTypeBoxSelect(evt):
            (self._multiTypeId, multiTypeStr) = self._multiTypeBox.selectedIdd
            multiTypeLabel['text'] = multiTypeStr

        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        topFrame = tk.Frame(outerFrame)
        topFrame.pack()
        self._answerFrame = AnswerTextFrame(topFrame)
        self._answerFrame['text'] = '答え'
        self._answerFrame.answerText['width'] = 40
        self._answerFrame.pack(side = tk.LEFT)
        self._dummyFrame = AnswerTextFrame(topFrame)
        self._dummyFrame['text'] = 'ダミー'
        self._dummyFrame.answerText['width'] = 40
        self._dummyFrame.pack(side = tk.LEFT)

        bottomFrame = tk.LabelFrame(outerFrame, text = '問題タイプ')
        bottomFrame.pack()
        self._multiTypeBox = ListboxIdd(bottomFrame, height = 3)
        self._multiTypeBox.iddList = self._qdManip.getMultiTypeList()
        self._multiTypeBox.onSelect = onMultiTypeBoxSelect
        self._multiTypeBox.pack()
        multiTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        multiTypeLabel.pack()

        # initialize
        self._multiTypeBox.select(MultiType.Unknown)

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answerList = self._answerFrame.answer
        dummyList = self._dummyFrame.answer
        if (not answerList) or (not dummyList):
            raise ve.AnswerBlankError
        answerStr = '\n'.join(answerList)
        dummyStr = '\n'.join(dummyList)
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'answer', 'dummy', 'multitype',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answerStr, dummyStr, self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, dummy, multitype, comment,
            stable, _, _, _, seriesId, pictureId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._answerFrame.answer = answer
        self._dummyFrame.answer = dummy
        self._multiTypeBox.select(multitype)
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]
        answerList = self._answerFrame.answer
        dummyList = self._dummyFrame.answer
        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        if answerList:
            for answer in answerList:
                for column in ('answer', 'dummy'):
                    condList.extend([
                        s.format(column, answer) for s in
                        [
                            "{0} like '%\n{1}\n%'", "{0} like '{1}\n%'",
                            "{0} like '%\n{1}'", "{0} like '{1}'"
                        ]
                    ])
        if dummyList:
            for dummy in dummyList:
                for column in ('answer', 'dummy'):
                    condList.extend([
                        s.format(column, dummy) for s in
                        [
                            "{0} like '%\n{1}\n%'", "{0} like '{1}\n%'",
                            "{0} like '%\n{1}'", "{0} like '{1}'"
                        ]
                    ])
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え', 'ダミー', '問題タイプ',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                'answer', 'dummy', 'multitype.multitype',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond,
            multiType = True
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answerFrame.answer = ''
        self._dummyFrame.answer = ''
        self._multiTypeBox.select(MultiType.Unknown)



@recorder
class RecorderImagetouch(Recorder):
    @property
    def quizName(self):
        return '画タッチ'


    @property
    def tableName(self):
        return 'quiz_imagetouch'


    @property
    def _pictureAnswerId(self):
        pictureAnswerIdStr = self._pictureAnswerIdEF.getEntryText()
        if not pictureAnswerIdStr:
            raise ve.AnswerBlankError
        try:
            return int(pictureAnswerIdStr)
        except ValueError:
            raise ve.InvalidPictureIdError


    @_pictureAnswerId.setter
    def _pictureAnswerId(self, pictureAnswerId):
        if pictureAnswerId is None:
            self._pictureAnswerIdEF.deleteEntryText()
        else:
            self._pictureAnswerIdEF.setEntryText(str(pictureAnswerId))


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        self._pictureAnswerIdEF = EntryFrame(outerFrame, text = '答え画像ID')
        self._pictureAnswerIdEF.pack()

        return outerFrame


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        pictureAnswerId = self._pictureAnswerId
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max',
            'question', 'comment', 'stable',
            'series', 'picture_id', 'picture_answer_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, qdm.comment, qdm.stable,
            qdm.seriesId, qdm.pictureId, pictureAnswerId
        ]
        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(self.tableName, columns, values)
        else:
            self._qdManip.update(self.tableName, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, comment,
            stable, _, _, _, seriesId, pictureId, pictureAnswerId
        ) = self.getQuizData(quizId)
        self._questionFrame.question = question
        self._pictureAnswerId = pictureAnswerId
        self.editCommon(quizId, subGenreId, examGenreId,
            difficulty_min, difficulty_max,
            comment, stable, seriesId, pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:6]

        condList = []
        if question:
            condList.append("question like '%{}%'".format(questionHead))
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題',
            'コメント', '安定性', 'シリーズ', '画像ID', '答え画像ID'
        )]
        result = self.selectFromJoinedTable(
            self.tableName,
            [
                '{}.id'.format(self.tableName),
                'genre.genre', 'subgenre.subgenre', 'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'comment', 'stable.stable', 'series.series',
                'picture_id', 'picture_answer_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''



