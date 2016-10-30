from abc import ABCMeta, abstractmethod, abstractproperty
from enum import IntEnum
from sqlite3 import IntegrityError
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from tkcommon import QuestionFrame, AnswerTextFrame, EntryFrame, QuestionFrame
from tkhelper import ListboxIdd, ComboboxIdd
from dbmanip import QuestionDataDBManip
from mojiutil import MojiUtil
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



class AnswerTextFrame(tk.LabelFrame):
    def __init__(self, master, **option):
        super().__init__(master, **option)
        self['text'] = '答え（改行区切り）'
        self.answerText = ScrolledText(self, height = 5)
        self.answerText.pack()


    @property
    def answer(self):
        answerStr = self.answerText.get('1.0', tk.END).strip()
        answerList = answerStr.split('\n')
        return [ans.strip() for ans in answerList]


    @answer.setter
    def answer(self, answerStr):
        self.answerText.delete('1.0', tk.END)
        self.answerText.insert(tk.END, answerStr.strip())



class EntryFrame(tk.LabelFrame):
    def __init__(self, master, **option):
        super().__init__(master, **option)
        self.ety = tk.Entry(self, width = 30)
        self.ety.pack()


    def getEntryText(self):
        return self.ety.get().strip()


    def setEntryText(self, text):
        self.deleteEntryText()
        self.ety.insert(0, text.strip())


    def deleteEntryText(self):
        self.ety.delete(0, tk.END)



class QuizDataManager(tk.Frame):
    genreId = None
    subGenreId = None
    examGenreId = None
    seriesId = None
    difficulty_min = 1
    difficulty_max = 5


# Instance Variables
# __qdManip, __master, __stableVar, __recorderList :: __init__
# __mainNbook :: __createMainNotebook
# __pictureIdEF, __commentText :: __createSupplementalFrame


    @property
    def __pictureId(self):
        pictureIdStr = self.__pictureIdEF.getEntryText()
        if not pictureIdStr:
            return None
        try:
            return int(pictureIdStr)
        except ValueError:
            raise ve.InvalidPictureIdError


    @__pictureId.setter
    def __pictureId(self, pictureId):
        if pictureId is None:
            self.__pictureIdEF.deleteEntryText()
        else:
            self.__pictureIdEF.setEntryText(str(pictureId))


    @property
    def __comment(self):
        return self.__commentText.get('1.0', tk.END).strip()


    @__comment.setter
    def __comment(self, comment):
        self.__commentText.delete('1.0', tk.END)
        self.__commentText.insert(tk.END, comment.strip())


    @property
    def __stable(self):
        return self.__stableVar.get()


    @__stable.setter
    def __stable(self, isStable):
        self.__stableVar.set(isStable)


    @property
    def __windowTitle(self):
        return self.__master.title()


    @__windowTitle.setter
    def __windowTitle(self, title):
        self.__master.title(title)


    def __init__(self, master, qdManip):
        super().__init__(master)
        self.__qdManip = qdManip
        self.__master = master
        self.__windowTitle = '新規登録'
        self.__stableVar = tk.BooleanVar()
        self.__stable = False
        self.__makeRecorderList()
        self.__createWidgets()
        self.pack()


    def __makeRecorderList(self):
        self.__recorderList = []
        for recorder in Recorder.__subclasses__():
            self.__recorderList.append(recorder(self.__qdManip))
        self.__recorderList.sort(key = lambda r: r.tabOrder)


    def __createWidgets(self):
        self.__createGenreSeriesFrame()
        self.__createMainNotebook()
        self.__createSupplementalFrame()
        self.__createBottomButton()


    def __createGenreSeriesFrame(self):
        def onGenreBoxSelect(evt):
            (self.__class__.genreId, genreStr) = genreBox.selectedIdd
            subGenreBox.iddList = self.__qdManip.getSubGenreListOnGenre(
                self.__class__.genreId)
            genreShowLabel['text'] = genreStr
            subGenreShowLabel['text'] = ''
            self.__class__.subGenreId = None

        def onSubGenreBoxSelect(evt):
            (self.__class__.subGenreId, subGenreStr) = subGenreBox.selectedIdd
            subGenreShowLabel['text'] = subGenreStr

        def onExamGenreBoxSelect(evt):
            (self.__class__.examGenreId, examGenreStr) = examGenreBox.selectedIdd
            examGenreShowLabel['text'] = examGenreStr

        def onSeriesBoxSelect(evt):
            (self.__class__.seriesId, seriesStr) = seriesBox.selectedIdd
            seriesShowLabel['text'] = seriesStr

        outerFrame = tk.Frame(self)

        genreFrame = tk.LabelFrame(outerFrame, text = 'ジャンル')
        genreFrame.pack(side = tk.LEFT)
        genreBox = ListboxIdd(genreFrame)
        genreBox.iddList = self.__qdManip.getGenreList()
        genreBox.onSelect = onGenreBoxSelect
        genreBox.pack()
        genreShowLabel = tk.Label(genreFrame, bg = 'LightPink')
        genreShowLabel.pack()

        subGenreFrame = tk.LabelFrame(outerFrame, text = 'サブジャンル')
        subGenreFrame.pack(side = tk.LEFT)
        subGenreBox = ListboxIdd(subGenreFrame)
        subGenreBox.onSelect = onSubGenreBoxSelect
        subGenreBox.pack()
        subGenreShowLabel = tk.Label(subGenreFrame, bg = 'LightSkyBlue')
        subGenreShowLabel.pack()

        examGenreFrame = tk.LabelFrame(outerFrame, text = '検定ジャンル')
        examGenreFrame.pack(side = tk.LEFT)
        examYScroll = tk.Scrollbar(examGenreFrame, orient = tk.VERTICAL)
        examYScroll.pack(side = tk.RIGHT, fill = tk.Y)
        examGenreBox = ListboxIdd(examGenreFrame)
        examGenreBox.iddList = self.__qdManip.getExamGenreList()
        examGenreBox.onSelect = onExamGenreBoxSelect
        examGenreBox['yscrollcommand'] = examYScroll.set
        examYScroll['command'] = examGenreBox.yview
        examGenreBox.pack()
        examGenreShowLabel = tk.Label(examGenreFrame, bg = 'gold')
        examGenreShowLabel.pack()

        seriesFrame = tk.LabelFrame(outerFrame, text = '回収シリーズ')
        seriesFrame.pack(side = tk.LEFT)
        seriesYScroll = tk.Scrollbar(seriesFrame, orient = tk.VERTICAL)
        seriesYScroll.pack(side = tk.RIGHT, fill = tk.Y)
        seriesBox = ListboxIdd(seriesFrame)
        seriesBox.iddList = self.__qdManip.getSeriesList()
        seriesBox.onSelect = onSeriesBoxSelect
        seriesBox['yscrollcommand'] = seriesYScroll.set
        seriesYScroll['command'] = seriesBox.yview
        seriesBox.pack()
        seriesShowLabel = tk.Label(seriesFrame, bg = 'thistle')
        seriesShowLabel.pack()

        outerFrame.pack()


    def __createMainNotebook(self):
        self.__mainNbook = ttk.Notebook(self)
        for recorder in self.__recorderList:
            self.__mainNbook.add(recorder.recordationFrame(),
                text = recorder.quizName)
        self.__mainNbook.pack()


    def __createSupplementalFrame(self):
        def onDifficultyMinCBSelect(evt):
            self.__class__.difficulty_min = difficultyMinCB.selectedId
            difficultyMaxCB.iddList = [
                (ix, d) for (ix, d) in difficultyList
                if self.__class__.difficulty_min <= d
            ]

        def onDifficultyMaxCBSelect(evt):
            self.__class__.difficulty_max = difficultyMaxCB.selectedId
            difficultyMinCB.iddList = [
                (ix, d) for (ix, d) in difficultyList
                if d <= self.__class__.difficulty_max
            ]

        difficultyList = [(x, x) for x in range(1, 6)]

        outerFrame = tk.Frame(self)

        self.__pictureIdEF = EntryFrame(outerFrame, text = '画像ID')
        self.__pictureIdEF.pack()

        commentFrame = tk.LabelFrame(outerFrame, text = 'コメント')
        commentFrame.pack()
        self.__commentText = ScrolledText(commentFrame, height = 3)
        self.__commentText.pack()

        difficultyFrame = tk.LabelFrame(outerFrame,
            text = '難易度（最小／最大）')
        difficultyFrame.pack()
        difficultyMinCB = ComboboxIdd(difficultyFrame, state = 'readonly')
        difficultyMinCB.iddList = difficultyList
        difficultyMinCB.onSelect = onDifficultyMinCBSelect
        difficultyMinCB.set(self.__class__.difficulty_min)
        difficultyMinCB.pack(side = tk.LEFT)
        difficultyMaxCB = ComboboxIdd(difficultyFrame, state = 'readonly')
        difficultyMaxCB.iddList = difficultyList
        difficultyMaxCB.onSelect = onDifficultyMaxCBSelect
        difficultyMaxCB.set(self.__class__.difficulty_max)
        difficultyMaxCB.pack(side = tk.LEFT)

        stableFrame = tk.LabelFrame(outerFrame, text = '安定性')
        stableFrame.pack()
        tk.Radiobutton(
            stableFrame, text = '安定',
            variable = self.__stableVar, value = True
        ).pack(side = tk.LEFT)
        tk.Radiobutton(
            stableFrame, text = '不安定',
            variable = self.__stableVar, value = False
        ).pack(side = tk.LEFT)

        outerFrame.pack()


    def __createBottomButton(self):
        bottomFrame = tk.Frame(self)
        registerButton = tk.Button(bottomFrame, text = '登録')
        registerButton['command'] = self.__record
        registerButton.pack(side = tk.LEFT)
        bottomFrame.pack(anchor = tk.E)


    def __record(self):
        ix = self.__mainNbook.index(self.__mainNbook.select())
        recorder = self.__recorderList[ix]
        try:
            self.__validationGenreIdAndSeriesId()
            pictureId = self.__pictureId
            recorder.record(self.__comment, self.__stable, self.__pictureId)
            self.__qdManip.save()
            messagebox.showinfo('登録完了', '登録したよ！')
            self.__cleanUpAll()
        except ve.ValidationError as verr:
            messagebox.showwarning('登録失敗', verr.message)
        except IntegrityError:
            messagebox.showwarning('登録失敗',
                '既に同じクイズが登録されているよ！')


    def __validationGenreIdAndSeriesId(self):
        if self.__class__.genreId is None:
            raise ve.GenreNoneError
        if self.__class__.subGenreId is None:
            raise ve.SubGenreNoneError
        if self.__class__.examGenreId is None:
            raise ve.ExamGenreNoneError
        if self.__class__.seriesId is None:
            raise ve.SeriesIdNoneError


    def __cleanUpAll(self):
        self.__pictureId = None
        self.__comment = ''
        self.__stable = False
        for recorder in self.__recorderList:
            recorder.cleanUp()



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



if __name__ == '__main__':
    qdManip = QuestionDataDBManip('question_data.sqlite3')
    root = tk.Tk()
    app = QuizDataManager(root, qdManip)
    app.mainloop()
    qdManip.close()
