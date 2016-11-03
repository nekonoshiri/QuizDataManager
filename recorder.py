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


    @abstractmethod
    def recordationFrame(self): pass


    @abstractmethod
    def record(self): pass


    # @abstractmethod
    def edit(self, quizId): pass


    @abstractmethod
    def search(self): pass


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
    def __init__(self, qdManip, qdManager):
        super().__init__(qdManip, qdManager)
        self._answerVar = tk.BooleanVar()
        self._answer = True


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


    def record(self, quizId = None):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        table = 'quiz_ox'
        columns = [
            'subgenre', 'examgenre',
            'difficulty_min', 'difficulty_max', 'question', 'answer',
            'comment', 'stable', 'series', 'picture_id'
        ]
        values = [
            qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, self._answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId
        ]

        if qdm.recordMode == RecordMode.Insert:
            self._qdManip.insert(table, columns, values)
        else:
            self._qdManip.update(table, columns, values,
                'where id = {}'.format(quizId)
            )
            qdm.setRecordMode(RecordMode.Insert)


    def edit(self, quizId):
        qdm = self._qdManager
        qdm.setRecordMode(RecordMode.Update, quizId)
        quizData = self._qdManip.select(['*'], 'quiz_ox',
            'where id = ?', [quizId])[0]
        (_, subGenreId, examGenreId, difficulty_min, difficulty_max,
            question, answer, comment,
            stable, _, _, _, seriesId, pictureId) = quizData
        genreId = self._qdManip.getGenreIdBySubGenreId(subGenreId)
        qdm.genreId = genreId
        qdm.subGenreId = subGenreId
        qdm.examGenreId = examGenreId
        qdm.difficulty_min = difficulty_min
        qdm.difficulty_max = difficulty_max
        self._questionFrame.question = question
        self._answer = answer
        qdm.comment = comment
        qdm.stable = stable
        qdm.seriesId = seriesId
        qdm.pictureId = pictureId


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限',
            '問題', '答え', 'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            'quiz_ox',
            [
                'quiz_ox.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
                'difficulty_min', 'difficulty_max', 'question',
                "replace(replace(answer, 1, 'True'), 0, 'False')",
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            "where question like '{}%'".format(questionHead)
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''
        self._answer = True



@recorder
class RecorderFour(Recorder):
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


    def record(self, qdm):
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
        self._qdManip.registerFour(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answer,
            dummy1, dummy2, dummy3,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_four',
            [
                'quiz_four.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def recordationFrame(self):
        def onAssocTypeBoxSelect(evt):
            (self._assocTypeId, assocTypeStr) = self._assocTypeBox.selectedIdd
            assocTypeLabel['text'] = assocTypeStr

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
        self._assocTypeBox.iddList = self._qdManip.getAssocTypeList()
        self._assocTypeBox.onSelect = onAssocTypeBoxSelect
        self._assocTypeBox.pack()
        assocTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        assocTypeLabel.pack()

        # initialize
        self._assocTypeBox.select(AssocType.OrderUnknown)

        return outerFrame


    def record(self, qdm):
        qdm = self._qdManager
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
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question1 = self._question1EF.getEntryText()
        question2 = self._question2EF.getEntryText()
        question3 = self._question3EF.getEntryText()
        question4 = self._question4EF.getEntryText()
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()
        if any((question1, question2, question3, question4,
                answer, dummy1, dummy2, dummy3)):
            cond = """where
            question1 = '{0}' or question1 = '{1}'
            or question1 = '{2}' or question1 = '{3}'
            or question2 = '{0}' or question2 = '{1}'
            or question2 = '{2}' or question2 = '{3}'
            or question3 = '{0}' or question3 = '{1}'
            or question3 = '{2}' or question3 = '{3}'
            or question4 = '{0}' or question4 = '{1}'
            or question4 = '{2}' or question4 = '{3}'
            or answer = '{4}' or answer = '{5}'
            or answer = '{6}' or answer = '{7}'
            or dummy1 = '{4}' or dummy1 = '{5}'
            or dummy1 = '{6}' or dummy1 = '{7}'
            or dummy2 = '{4}' or dummy2 = '{5}'
            or dummy2 = '{6}' or dummy2 = '{7}'
            or dummy3 = '{4}' or dummy3 = '{5}'
            or dummy3 = '{6}' or dummy3 = '{7}'
            """.format(question1, question2, question3, question4,
                answer, dummy1, dummy2, dummy3)
        else:
            cond = ''
        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限',
            '問題１', '問題２', '問題３', '問題４',
            '答え', 'ダミー１', 'ダミー２', 'ダミー３', '連想タイプ',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            'quiz_assoc',
            [
                'quiz_assoc.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question1', 'question2', 'question3', 'question4',
                'answer', 'dummy1', 'dummy2', 'dummy3','assoctype.assoctype',
                'comment', 'stable.stable', 'series.series', 'picture_id'
            ],
            cond,
            assocType = True
        )
        return header + result


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



@recorder
class RecorderSort(Recorder):
    @property
    def quizName(self):
        return '並替'


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()

        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()

        return outerFrame


    def record(self, qdm):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answer = self._answerEF.getEntryText()
        if not answer:
            raise ve.AnswerBlankError
        self._qdManip.registerSort(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        answer = self._answerEF.getEntryText()

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
        if answer:
            condList.append("answer = '{}'".format(answer))
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            'quiz_sort',
            [
                'quiz_sort.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
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

        self._qdManip.registerPanel(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max,
            question, answerStr, panel,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        answerList = self._answerFrame.answer

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_panel',
            [
                'quiz_panel.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
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
        self._qdManip.registerSlot(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answer,
            dummy1, dummy2, dummy3,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        answer = self._answerEF.getEntryText()
        dummy1 = self._dummy1EF.getEntryText()
        dummy2 = self._dummy2EF.getEntryText()
        dummy3 = self._dummy3EF.getEntryText()

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_slot',
            [
                'quiz_slot.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        return outerFrame


    def record(self, qdm):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        rowAnswerList = self._answerFrame.answer
        (typingtype, answer) = self.getTypingTypeAndAnswer(rowAnswerList)
        self._qdManip.registerTyping(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, typingtype,
            answer, qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        rowAnswerList = self._answerFrame.answer
        answerList = [str.upper(MojiUtil.toHankaku(ans)) for ans in rowAnswerList]

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_typing',
            [
                'quiz_typing.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._answerEF = EntryFrame(outerFrame, text = '答え')
        self._answerEF.pack()

        return outerFrame


    def record(self, qdm):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        rowAnswerList = [self._answerEF.getEntryText()]
        (typingtype, answer) = self.getTypingTypeAndAnswer(rowAnswerList)
        self._qdManip.registerCube(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, typingtype,
            answer, qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        rowAnswer = self._answerEF.getEntryText()
        answer = str.upper(MojiUtil.toHankaku(rowAnswer))

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
        if answer:
            condList.append("answer = '{}'".format(answer))
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題', '答え',
            'コメント', '安定性', 'シリーズ', '画像ID'
        )]
        result = self.selectFromJoinedTable(
            'quiz_cube',
            [
                'quiz_cube.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def recordationFrame(self):
        outerFrame = tk.Frame()

        self._questionFrame = QuestionFrame(outerFrame)
        self._questionFrame.pack()
        self._questionEF = EntryFrame(outerFrame, text = 'エフェクトをかける文字')
        self._questionEF.pack()
        self._answerFrame = AnswerTextFrame(outerFrame)
        self._answerFrame.pack()

        return outerFrame


    def record(self, qdm):
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
        self._qdManip.registerEffect(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, questionEffect,
            typingtype, answer,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        questionEffect = self._questionEF.getEntryText()
        rowAnswerList = self._answerFrame.answer
        answerList = [str.upper(MojiUtil.toHankaku(ans)) for ans in rowAnswerList]

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_effect',
            [
                'quiz_effect.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        answerList = self._answerFrame.answer
        if not answerList:
            raise ve.AnswerBlankError
        answerStr = '\n'.join(answerList)
        self._qdManip.registerOrder(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question, answerStr,
            self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        answerList = self._answerFrame.answer
        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_order',
            [
                'quiz_order.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
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
        self._qdManip.registerConnect(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question,
            optionLeftStr, optionRightStr,
            self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        optionLeftList = self._optionLeftFrame.answer
        optionRightList = self._optionRightFrame.answer
        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_connect',
            [
                'quiz_connect.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
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
        self._qdManip.registerMulti(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question,
            answerStr, dummyStr,
            self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        answerList = self._answerFrame.answer
        dummyList = self._dummyFrame.answer
        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_multi',
            [
                'quiz_multi.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        group1List = self._group1Frame.answer
        group2List = self._group2Frame.answer
        group3List = self._group3Frame.answer
        if (not group1List) or (not group2List) or (not group3List):
            raise ve.AnswerBlankError
        group1Str = '\n'.join(group1List)
        group2Str = '\n'.join(group2List)
        group3Str = '\n'.join(group3List)
        self._qdManip.registerGroup(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question,
            group1Str, group2Str, group3Str,
            self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        group1List = self._group1Frame.answer
        group2List = self._group2Frame.answer
        group3List = self._group3Frame.answer
        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_group',
            [
                'quiz_group.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
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
        self._qdManip.registerFirstcome(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question,
            answerStr, dummyStr,
            self._multiTypeId,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]
        answerList = self._answerFrame.answer
        dummyList = self._dummyFrame.answer
        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
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
            'quiz_firstcome',
            [
                'quiz_firstcome.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
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


    def record(self, qdm):
        qdm = self._qdManager
        question = self._questionFrame.question
        if not question:
            raise ve.QuestionBlankError
        pictureAnswerId = self._pictureAnswerId
        self._qdManip.registerImagetouch(qdm.subGenreId, qdm.examGenreId,
            qdm.difficulty_min, qdm.difficulty_max, question,
            qdm.comment, qdm.stable, qdm.seriesId, qdm.pictureId,
            pictureAnswerId)


    def search(self):
        question = self._questionFrame.question
        questionHead = question[:4]

        condList = []
        if question:
            condList.append("question like '{}%'".format(questionHead))
        cond = 'where ' + ' or '.join(condList) if condList else ''

        header = [(
            'ID', 'ジャンル', 'サブジャンル', '検定ジャンル',
            '☆下限', '☆上限', '問題',
            'コメント', '安定性', 'シリーズ', '画像ID', '答え画像ID'
        )]
        result = self.selectFromJoinedTable(
            'quiz_imagetouch',
            [
                'quiz_imagetouch.id', 'genre.genre', 'subgenre.subgenre',
                'examgenre.examgenre',
                'difficulty_min', 'difficulty_max',
                'question', 'comment', 'stable.stable', 'series.series',
                'picture_id', 'picture_answer_id'
            ],
            cond
        )
        return header + result


    def cleanUp(self):
        self._questionFrame.question = ''



