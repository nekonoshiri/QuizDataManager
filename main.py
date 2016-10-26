from enum import Enum
from sqlite3 import IntegrityError
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import re

from tkhelper import ListboxIdd, ComboboxIdd
from dbmanip import QuestionDataDBManip
from mojiutil import MojiUtil


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


class QuestionFrame(tk.LabelFrame):
    def __init__(self, master, **option):
        super().__init__(master, **option)
        self['text'] = '問題'
        self.questionText = QuestionText(self, height = 5)
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


class QuestionText(ScrolledText):
    def __init__(self, master, **option):
        super().__init__(master, **option)
        self['height'] = 5


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
#
# mainNbook
#     self.getCurrentQuizType() :: QuizType
#
# questionFrameOX
#     self.getQuestion() :: str
# answerOX
#     self.answerOX.get() :: bool (default True)
#
# commentText
#     self.getComment() :: str
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
        return outerFrame


    def frameAssoc(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameSort(self):
        outerFrame = tk.Frame()
        return outerFrame


    def framePanel(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameSlot(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameTyping(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameCube(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameEffect(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameOrder(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameConnect(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameMulti(self):
        outerFrame = tk.Frame()
        return outerFrame


    def frameGroup(self):
        outerFrame = tk.Frame()
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
        questionFrame = eval('self.questionFrame%s' % quizType.name)
        return questionFrame.question


    def getComment(self):
        return self.commentText.get('1.0', tk.END).strip()


    def registerFailMsgBox(self, text):
        messagebox.showwarning('登録失敗', text)


    def validationCommon(self):
        if self.genreId is None:
            self.registerFailMsgBox('ジャンルを入力してね！')
            return False
        if self.subGenreId is None:
            self.registerFailMsgBox('サブジャンルを入力してね！')
            return False
        if self.examGenreId is None:
            self.registerFailMsgBox('検定ジャンルを入力してね！')
            return False
        if self.seriesId is None:
            self.registerFailMsgBox('回収シリーズを入力してね！')
            return False
        quizType = self.getCurrentQuizType()
        question = self.getQuestion()
        if not question:
            self.registerFailMsgBox('問題を入力してね！')
            return False
        return question


    def registerMain(self):
        quizType = self.getCurrentQuizType()
        register = eval('self.register%s' % quizType.name)
        try:
            if register():
                self._qdManip.save()
                messagebox.showinfo('登録完了', '登録したよ！')
        except IntegrityError:
            self.registerFailMsgBox('既に同じクイズが登録されているよ！')
            return


    def registerOX(self):
        question = self.validationCommon()
        if not question:
            return False
        answer = self.answerOX.get()
        comment = self.getComment()
        stable = self.stable.get()
        self._qdManip.registerOX(self.subGenreId, self.examGenreId,
            self.difficulty_min, self.difficulty_max, question, answer,
            comment, stable, self.seriesId)
        return True



if __name__ == '__main__':
    qdManip = QuestionDataDBManip('question_data.sqlite3')
    root = tk.Tk()
    app = Application(root, qdManip)
    app.mainloop()
    qdManip.close()
