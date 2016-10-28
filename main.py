from enum import Enum, IntEnum
from sqlite3 import IntegrityError
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import re

from tkhelper import ListboxIdd, ComboboxIdd
from dbmanip import QuestionDataDBManip
from mojiutil import MojiUtil
import validationException as ve


class QuizType(Enum):
    OX = '○×'
    Four = '四択'
    Assoc = '連想'
    Sort = '並べ替え'
    Panel = '文字パネル'
    Slot = 'スロット'
    Typing = 'タイピング'
    Cube = 'キューブ'
    Effect = 'エフェクト'
    Order = '順番当て'
    Connect = '線結び'
    Multi = '一問多答'
    Group = 'グループ分け'


class TypingType(IntEnum):
    Hiragana = 1
    Katakana = 2
    Eisuuji = 3


class QuestionFrame(tk.LabelFrame):
    def __init__(self, master, **option):
        super().__init__(master, **option)
        self['text'] = '問題'
        self.questionText = ScrolledText(self, height = 5)
        self.questionText.pack()
        formatButton = tk.Button(self, text = '整形')
        formatButton['command'] = self.formatQuestion
        formatButton.pack(anchor = tk.E)


    @property
    def question(self):
        return self.questionText.get('1.0', tk.END).strip()


    @question.setter
    def question(self, question):
        self.questionText.delete('1.0', tk.END)
        self.questionText.insert(tk.END, question.strip())


    def formatQuestion(self):
        question = self.question
        # 文中の空白類文字の削除
        question = ''.join(question.split())
        transdict = str.maketrans(',，.．!?', '、、。。！？')
        question = question.translate(transdict)
        # 数字１文字は全角，２文字以上は半角
        question = re.sub('\d',
            lambda obj: MojiUtil.toZenkaku(obj.group(0)), question
        )
        question = re.sub('\d\d+',
            lambda obj: MojiUtil.toHankaku(obj.group(0)), question
        )
        self.question = question


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


    def deleteEntryText(self):
        self.ety.delete(0, tk.END)


class Application(tk.Frame):
# Instance Variables
#
# _qdManip
# _master
#     self.changeWindowTitle(title)
#
# genreId :: None or int
# subGenreId :: None or int
# examGenreId :: None or int
# seriesId :: None or int
# assocTypeId :: int (default first index)
#
# mainNbook
#     self.getCurrentQuizType() :: QuizType
#
# questionFrameOX, Four, Sort, Panel, Slot, Typing, Cube, Effect, Order,
#              Connect, Multi, Group :: QuestionFrame
#
# answerOX
#     self.answerOX.get() :: bool (default True)
#
# answerEntryFour :: EntryFrame
# dummy1EntryFour, 2, 3, 4 :: EntryFrame
#
# question1EntryAssoc, 2, 3, 4 :: EntryFrame
# answerEntryAssoc :: EntryFrame
# dummy1EntryAssoc, 2, 3, 4 :: EntryFrame
#
# answerEntrySort :: EntryFrame
#
# answerFramePanel :: AnswerTextFrame
# panelEntryPanel :: EntryFrame
#
# answerEntrySlot :: EntryFrame
# dummy1EntrySlot, 2, 3 :: EntryFrame
#
# answerFrameTyping :: AnswerTextFrame
#
# answerEntryCube :: EntryFrame
#
# questionEntryEffect :: EntryFrame
# answerFrameEffect :: AnswerTextFrame
#
# commentText
# difficulty_min :: int (default 1)
# difficulty_max :: int (default 5)
#     satisfy (1 <= difficulty_min <= difficulty_max <= 5)
# stable: self.stable.get() :: bool (default True)


    def __init__(self, master, qdManip):
        super().__init__(master)
        self._qdManip = qdManip
        self._master = master
        self.changeWindowTitle('新規登録')
        self.pack()
        self.createWidgets()


    def changeWindowTitle(self, title):
        self._master.title(title)


    def createWidgets(self):
        self.createGenreSeriesFrame()
        self.createMainNotebook()
        self.createSupplementalFrame()
        self.createBottomButton()


    def createGenreSeriesFrame(self):
        def onGenreBoxSelect(evt):
            (self.genreId, genreStr) = genreBox.selectedIdd
            subGenreBox.iddList = self._qdManip.getSubGenreListOnGenre(self.genreId)
            genreShowLabel['text'] = genreStr
            subGenreShowLabel['text'] = ''
            self.subGenreId = None

        def onSubGenreBoxSelect(evt):
            (self.subGenreId, subGenreStr) = subGenreBox.selectedIdd
            subGenreShowLabel['text'] = subGenreStr

        def onExamGenreBoxSelect(evt):
            (self.examGenreId, examGenreStr) = examGenreBox.selectedIdd
            examGenreShowLabel['text'] = examGenreStr

        def onSeriesBoxSelect(evt):
            (self.seriesId, seriesStr) = seriesBox.selectedIdd
            seriesShowLabel['text'] = seriesStr

        self.genreId = None
        self.subGenreId = None
        self.examGenreId = None
        self.seriesId = None

        outerFrame = tk.Frame(self)

        genreFrame = tk.LabelFrame(outerFrame, text = 'ジャンル')
        genreFrame.pack(side = tk.LEFT)
        genreBox = ListboxIdd(genreFrame)
        genreBox.iddList = self._qdManip.getGenreList()
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
        examGenreBox.iddList = self._qdManip.getExamGenreList()
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
        seriesBox.iddList = self._qdManip.getSeriesList()
        seriesBox.onSelect = onSeriesBoxSelect
        seriesBox['yscrollcommand'] = seriesYScroll.set
        seriesYScroll['command'] = seriesBox.yview
        seriesBox.pack()
        seriesShowLabel = tk.Label(seriesFrame, bg = 'thistle')
        seriesShowLabel.pack()

        outerFrame.pack()


    def createMainNotebook(self):
        self.mainNbook = ttk.Notebook(self)
        for quizType in QuizType:
            self.mainNbook.add(self.selectFrameByQuizType(quizType),
                text = quizType.value)
        self.mainNbook.pack()


    def getCurrentQuizType(self):
        ix = self.mainNbook.index(self.mainNbook.select())
        return list(QuizType)[ix]


    def selectFrameByQuizType(self, quizType):
        return eval('self.frame%s()' % quizType.name)


    def frameOX(self):
        self.answerOX = tk.BooleanVar()
        self.answerOX.set(True)

        outerFrame = tk.Frame()

        self.questionFrameOX = QuestionFrame(outerFrame)
        self.questionFrameOX.pack()
        answerFrame = tk.LabelFrame(outerFrame, text = '答え')
        answerFrame.pack()
        tk.Radiobutton(answerFrame, text = '○', variable = self.answerOX,
            value = True).pack(side = tk.LEFT)
        tk.Radiobutton(answerFrame, text = '×', variable = self.answerOX,
            value = False).pack(side = tk.LEFT)

        return outerFrame


    def frameFour(self):
        outerFrame = tk.Frame()

        self.questionFrameFour = QuestionFrame(outerFrame)
        self.questionFrameFour.pack()

        self.answerEntryFour = EntryFrame(outerFrame, text = '答え')
        self.answerEntryFour.pack()
        self.dummy1EntryFour = EntryFrame(outerFrame, text = 'ダミー１')
        self.dummy1EntryFour.pack()
        self.dummy2EntryFour = EntryFrame(outerFrame, text = 'ダミー２')
        self.dummy2EntryFour.pack()
        self.dummy3EntryFour = EntryFrame(outerFrame, text = 'ダミー３')
        self.dummy3EntryFour.pack()

        return outerFrame


    def frameAssoc(self):
        def onAssocTypeBoxSelect(evt):
            (self.assocTypeId, assocTypeStr) = assocTypeBox.selectedIdd
            assocTypeLabel['text'] = assocTypeStr

        assocTypeList = self._qdManip.getAssocTypeList()

        outerFrame = tk.Frame()

        topFrame = tk.Frame(outerFrame)
        topFrame.pack()

        questionFrame = tk.Frame(topFrame)
        questionFrame.pack(side = tk.LEFT)
        self.question1EntryAssoc = EntryFrame(questionFrame, text = 'ヒント１')
        self.question1EntryAssoc.pack()
        self.question2EntryAssoc = EntryFrame(questionFrame, text = 'ヒント２')
        self.question2EntryAssoc.pack()
        self.question3EntryAssoc = EntryFrame(questionFrame, text = 'ヒント３')
        self.question3EntryAssoc.pack()
        self.question4EntryAssoc = EntryFrame(questionFrame, text = 'ヒント４')
        self.question4EntryAssoc.pack()

        paddingFrame = tk.Frame(topFrame, width = 50)
        paddingFrame.pack(side = tk.LEFT)

        answerFrame = tk.Frame(topFrame)
        answerFrame.pack(side = tk.LEFT)
        self.answerEntryAssoc = EntryFrame(answerFrame, text = '答え')
        self.answerEntryAssoc.pack()
        self.dummy1EntryAssoc = EntryFrame(answerFrame, text = 'ダミー１')
        self.dummy1EntryAssoc.pack()
        self.dummy2EntryAssoc = EntryFrame(answerFrame, text = 'ダミー２')
        self.dummy2EntryAssoc.pack()
        self.dummy3EntryAssoc = EntryFrame(answerFrame, text = 'ダミー３')
        self.dummy3EntryAssoc.pack()

        bottomFrame = tk.LabelFrame(outerFrame, text = '連想タイプ')
        bottomFrame.pack()
        assocTypeBox = ListboxIdd(bottomFrame, height = 4)
        assocTypeBox.iddList = assocTypeList
        assocTypeBox.onSelect = onAssocTypeBoxSelect
        assocTypeBox.pack()
        assocTypeLabel = tk.Label(bottomFrame, bg = 'LightPink')
        assocTypeLabel.pack()

        # initialize
        (self.assocTypeId, assocTypeLabel['text']) = assocTypeList[0]

        return outerFrame


    def frameSort(self):
        outerFrame = tk.Frame()

        self.questionFrameSort = QuestionFrame(outerFrame)
        self.questionFrameSort.pack()

        self.answerEntrySort = EntryFrame(outerFrame, text = '答え')
        self.answerEntrySort.pack()

        return outerFrame


    def framePanel(self):
        outerFrame = tk.Frame()

        self.questionFramePanel = QuestionFrame(outerFrame)
        self.questionFramePanel.pack()

        self.answerFramePanel = AnswerTextFrame(outerFrame)
        self.answerFramePanel.pack()

        self.panelEntryPanel = EntryFrame(outerFrame,
            text = 'パネル（8枚または10枚）')
        self.panelEntryPanel.pack()

        return outerFrame


    def frameSlot(self):
        outerFrame = tk.Frame()

        self.questionFrameSlot = QuestionFrame(outerFrame)
        self.questionFrameSlot.pack()

        self.answerEntrySlot = EntryFrame(outerFrame, text = '答え')
        self.answerEntrySlot.pack()

        self.dummy1EntrySlot = EntryFrame(outerFrame, text = 'ダミー１')
        self.dummy1EntrySlot.pack()

        self.dummy2EntrySlot = EntryFrame(outerFrame, text = 'ダミー２')
        self.dummy2EntrySlot.pack()

        self.dummy3EntrySlot = EntryFrame(outerFrame, text = 'ダミー３')
        self.dummy3EntrySlot.pack()

        return outerFrame


    def frameTyping(self):
        outerFrame = tk.Frame()

        self.questionFrameTyping = QuestionFrame(outerFrame)
        self.questionFrameTyping.pack()

        self.answerFrameTyping = AnswerTextFrame(outerFrame)
        self.answerFrameTyping.pack()
        return outerFrame


    def frameCube(self):
        outerFrame = tk.Frame()

        self.questionFrameCube = QuestionFrame(outerFrame)
        self.questionFrameCube.pack()

        self.answerEntryCube = EntryFrame(outerFrame, text = '答え')
        self.answerEntryCube.pack()
        return outerFrame


    def frameEffect(self):
        outerFrame = tk.Frame()

        self.questionFrameEffect = QuestionFrame(outerFrame)
        self.questionFrameEffect.pack()

        self.questionEntryEffect = EntryFrame(outerFrame,
            text = 'エフェクトをかける文字')
        self.questionEntryEffect.pack()

        self.answerFrameEffect = AnswerTextFrame(outerFrame)
        self.answerFrameEffect.pack()
        return outerFrame


    def frameOrder(self):
        outerFrame = tk.Frame()

        self.questionFrameOrder = QuestionFrame(outerFrame)
        self.questionFrameOrder.pack()
        return outerFrame


    def frameConnect(self):
        outerFrame = tk.Frame()

        self.questionFrameConnect = QuestionFrame(outerFrame)
        self.questionFrameConnect.pack()
        return outerFrame


    def frameMulti(self):
        outerFrame = tk.Frame()

        self.questionFrameMulti = QuestionFrame(outerFrame)
        self.questionFrameMulti.pack()
        return outerFrame


    def frameGroup(self):
        outerFrame = tk.Frame()

        self.questionFrameGroup = QuestionFrame(outerFrame)
        self.questionFrameGroup.pack()
        return outerFrame


    def createSupplementalFrame(self):
        def onDifficultyMinCBSelect(evt):
            self.difficulty_min = difficultyMinCB.selectedId
            difficultyMaxCB.iddList = [
                (ix, d) for (ix, d) in difficultyList if self.difficulty_min <= d
            ]

        def onDifficultyMaxCBSelect(evt):
            self.difficulty_max = difficultyMaxCB.selectedId
            difficultyMinCB.iddList = [
                (ix, d) for (ix, d) in difficultyList if d <= self.difficulty_max
            ]

        self.difficulty_min = 1
        self.difficulty_max = 5
        difficultyList = [(x, x) for x in range(1, 6)]

        outerFrame = tk.Frame(self)

        commentFrame = tk.LabelFrame(outerFrame, text = 'コメント')
        commentFrame.pack()
        self.commentText = ScrolledText(commentFrame, height = 3)
        self.commentText.pack()

        difficultyFrame = tk.LabelFrame(outerFrame, text = '難易度（最小／最大）')
        difficultyFrame.pack()
        difficultyMinCB = ComboboxIdd(difficultyFrame, state = 'readonly')
        difficultyMinCB.iddList = difficultyList
        difficultyMinCB.onSelect = onDifficultyMinCBSelect
        difficultyMinCB.set(self.difficulty_min)
        difficultyMinCB.pack(side = tk.LEFT)
        difficultyMaxCB = ComboboxIdd(difficultyFrame, state = 'readonly')
        difficultyMaxCB.iddList = difficultyList
        difficultyMaxCB.onSelect = onDifficultyMaxCBSelect
        difficultyMaxCB.set(self.difficulty_max)
        difficultyMaxCB.pack(side = tk.LEFT)

        stableFrame = tk.LabelFrame(outerFrame, text = '安定性')
        stableFrame.pack()
        self.stable = tk.BooleanVar()
        self.stable.set(True)
        tk.Radiobutton(stableFrame, text = '安定', variable = self.stable,
            value = True).pack(side = tk.LEFT)
        tk.Radiobutton(stableFrame, text = '不安定', variable = self.stable,
            value = False).pack(side = tk.LEFT)

        outerFrame.pack()


    def createBottomButton(self):
        bottomFrame = tk.Frame(self)
        registerButton = tk.Button(bottomFrame, text = '登録')
        registerButton['command'] = self.registerMain
        registerButton.pack(side = tk.LEFT)
        bottomFrame.pack(anchor = tk.E)


    def getQuestion(self):
        quizType = self.getCurrentQuizType()
        if quizType == QuizType.Assoc:
            question = (
                self.question1EntryAssoc.getEntryText(),
                self.question2EntryAssoc.getEntryText(),
                self.question3EntryAssoc.getEntryText(),
                self.question4EntryAssoc.getEntryText(),
            )
            for q in question:
                if not q: raise ve.QuestionBlankError
        else:
            questionFrame = eval('self.questionFrame%s' % quizType.name)
            question = questionFrame.question
            if not question:
                raise ve.QuestionBlankError
        return question


    def getTypingTypeAndAnswer(self):
        def getTypingType(answer):
            if MojiUtil.isHiragana(answer):
                return TypingType.Hiragana
            elif MojiUtil.isZenkakuKatakana(answer):
                return TypingType.Katakana
            elif answer.encode('utf-8').isalnum():
                return TypingType.Eisuuji
            else:
                raise ve.TypingTypeInconsistError

        quizType = self.getCurrentQuizType()
        if quizType == QuizType.Typing:
            rowAnswerList = self.answerFrameTyping.answer
        elif quizType == QuizType.Cube:
            rowAnswerList = [self.answerEntryCube.getEntryText()]
        elif quizType == QuizType.Effect:
            rowAnswerList = self.answerFrameEffect.answer
        else:
            return

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


    def validationCommon(self):
        if self.genreId is None:
            raise ve.GenreNoneError
        if self.subGenreId is None:
            raise ve.SubGenreNoneError
        if self.examGenreId is None:
            raise ve.ExamGenreNoneError
        if self.seriesId is None:
            raise ve.SeriesIdNoneError


    def registerMain(self):
        quizType = self.getCurrentQuizType()
        register = eval('self.register%s' % quizType.name)
        try:
            self.validationCommon()
            comment = self.commentText.get('1.0', tk.END).strip()
            stable = self.stable.get()
            register(comment, stable)
            self._qdManip.save()
            messagebox.showinfo('登録完了', '登録したよ！')
            self.deleteEachTextEntry()
        except ve.ValidationError as verr:
            messagebox.showwarning('登録失敗', verr.message)
        except IntegrityError:
            messagebox.showwarning('登録失敗',
                '既に同じクイズが登録されているよ！')


    def registerOX(self, comment, stable):
        question = self.getQuestion()
        answer = self.answerOX.get()
        self._qdManip.registerOX(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, answer,
            comment, stable, self.seriesId)


    def registerFour(self, comment, stable):
        question = self.getQuestion()
        answer = self.answerEntryFour.getEntryText()
        dummy1 = self.dummy1EntryFour.getEntryText()
        dummy2 = self.dummy2EntryFour.getEntryText()
        dummy3 = self.dummy3EntryFour.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError
        self._qdManip.registerFour(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, answer,
            dummy1, dummy2, dummy3, comment, stable, self.seriesId)


    def registerAssoc(self, comment, stable):
        (question1, question2, question3, question4) = self.getQuestion()
        answer = self.answerEntryAssoc.getEntryText()
        dummy1 = self.dummy1EntryAssoc.getEntryText()
        dummy2 = self.dummy2EntryAssoc.getEntryText()
        dummy3 = self.dummy3EntryAssoc.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError
        self._qdManip.registerAssoc(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max,
            question1, question2, question3, question4, answer,
            dummy1, dummy2, dummy3, self.assocTypeId,
            comment, stable, self.seriesId)


    def registerSort(self, comment, stable):
        question = self.getQuestion()
        answer = self.answerEntrySort.getEntryText()
        if not answer:
            raise ve.AnswerBlankError
        self._qdManip.registerSort(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, answer,
            comment, stable, self.seriesId)


    def registerPanel(self, comment, stable):
        question = self.getQuestion()

        answerList = self.answerFramePanel.answer
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

        panel = self.panelEntryPanel.getEntryText()
        if not len(panel) in (8, 10):
            raise ve.PanelLengthError

        for answer in answerList:
            for c in answer:
                if not c in panel:
                    raise ve.PanelNoAnswerError

        answerStr = '\n'.join(answerList)

        self._qdManip.registerPanel(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, answerStr, panel,
            comment, stable, self.seriesId)


    def registerSlot(self, comment, stable):
        question = self.getQuestion()
        answer = self.answerEntrySlot.getEntryText()
        dummy1 = self.dummy1EntrySlot.getEntryText()
        dummy2 = self.dummy2EntrySlot.getEntryText()
        dummy3 = self.dummy3EntrySlot.getEntryText()
        for s in (answer, dummy1, dummy2, dummy3):
            if not s: raise ve.AnswerBlankError
        if not (len(answer) == len(dummy1) == len(dummy2) == len(dummy3)):
            raise ve.SlotStrLenError
        self._qdManip.registerSlot(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, answer,
            dummy1, dummy2, dummy3, comment, stable, self.seriesId)


    def registerTyping(self, comment, stable):
        question = self.getQuestion()
        (typingtype, answer) = self.getTypingTypeAndAnswer()
        self._qdManip.registerTyping(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, typingtype,
            answer, comment, stable, self.seriesId)


    def registerCube(self, comment, stable):
        question = self.getQuestion()
        (typingtype, answer) = self.getTypingTypeAndAnswer()
        self._qdManip.registerCube(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, typingtype,
            answer, comment, stable, self.seriesId)


    def registerEffect(self, comment, stable):
        question = self.getQuestion()
        questionEffect = self.questionEntryEffect.getEntryText()
        if not questionEffect:
            raise ve.AnswerBlankError
        (typingtype, answer) = self.getTypingTypeAndAnswer()
        self._qdManip.registerEffect(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, questionEffect,
            typingtype, answer, comment, stable, self.seriesId)


    def deleteQuestion(self):
        for quizType in QuizType:
            if quizType == QuizType.Assoc:
                self.question1EntryAssoc.deleteEntryText()
                self.question2EntryAssoc.deleteEntryText()
                self.question3EntryAssoc.deleteEntryText()
                self.question4EntryAssoc.deleteEntryText()
            else:
                questionFrame = eval('self.questionFrame%s' % quizType.name)
                questionFrame.question = ''


    def deleteComment(self):
        self.commentText.delete('1.0', tk.END)


    def deleteEachTextEntry(self):
        self.deleteQuestion()
        self.deleteComment()
        self.answerEntryFour.deleteEntryText()
        self.dummy1EntryFour.deleteEntryText()
        self.dummy2EntryFour.deleteEntryText()
        self.dummy3EntryFour.deleteEntryText()
        self.answerEntryAssoc.deleteEntryText()
        self.dummy1EntryAssoc.deleteEntryText()
        self.dummy2EntryAssoc.deleteEntryText()
        self.dummy3EntryAssoc.deleteEntryText()
        self.answerEntrySort.deleteEntryText()
        self.answerFramePanel.answer = ''
        self.panelEntryPanel.deleteEntryText()
        self.answerEntrySlot.deleteEntryText()
        self.dummy1EntrySlot.deleteEntryText()
        self.dummy2EntrySlot.deleteEntryText()
        self.dummy3EntrySlot.deleteEntryText()
        self.answerFrameTyping.answer = ''
        self.answerEntryCube.deleteEntryText()
        self.questionEntryEffect.deleteEntryText()
        self.answerFrameEffect.answer = ''



if __name__ == '__main__':
    qdManip = QuestionDataDBManip('question_data.sqlite3')
    root = tk.Tk()
    app = Application(root, qdManip)
    app.mainloop()
    qdManip.close()
