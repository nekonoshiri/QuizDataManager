from enum import Enum, IntEnum
import platform
from sqlite3 import IntegrityError
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from tkcommon import QuestionFrame, EntryFrame
from tkhelper import ListboxIdd, ComboboxIdd
import validationException as ve



class RecordMode(Enum):
    Insert = 0
    Update = 1



class StableType(IntEnum):
    Undefined = -1
    Unstable = 0
    Stable = 1



class QuizDataManager(tk.Frame):
    @property
    def recordMode(self):
        return self.__recordMode


    def setRecordMode(self, recordMode, quizId = None):
        if recordMode == RecordMode.Insert:
            quizId = None
        self.recordMode = (recordMode, quizId)


    @recordMode.setter
    def recordMode(self, arg):
        (recordMode, quizId) = arg
        self.__recordMode = recordMode
        if recordMode == RecordMode.Insert:
            self.__master.title('新規登録')
            self.__registerButton['text'] = '登録'
            self.__quizId = None
        else:
            self.__master.title('編集')
            self.__registerButton['text'] = '上書き編集'
            self.__quizId = quizId


    @property
    def genreId(self):
        return self.__genreId


    @genreId.setter
    def genreId(self, genreId):
        self.__genreId = genreId
        self.__genreBox.select(genreId)


    @property
    def subGenreId(self):
        return self.__subGenreId


    @subGenreId.setter
    def subGenreId(self, subGenreId):
        self.__subGenreId = subGenreId
        self.__subGenreBox.select(subGenreId)


    @property
    def examGenreId(self):
        return self.__examGenreId


    @examGenreId.setter
    def examGenreId(self, examGenreId):
        self.__examGenreId = examGenreId
        self.__examGenreBox.select(examGenreId)


    @property
    def seriesId(self):
        return self.__seriesId


    @seriesId.setter
    def seriesId(self, seriesId):
        self.__seriesId = seriesId
        self.__seriesBox.select(seriesId)


    @property
    def question(self):
        return self.__questionFrame.question


    @question.setter
    def question(self, question):
        self.__questionFrame.question = question


    @property
    def difficulty_min(self):
        return self.__difficulty_min


    @difficulty_min.setter
    def difficulty_min(self, difficulty_min):
        self.__difficulty_min = difficulty_min
        self.__difficultyMinCB.select(difficulty_min)


    @property
    def difficulty_max(self):
        return self.__difficulty_max


    @difficulty_max.setter
    def difficulty_max(self, difficulty_max):
        self.__difficulty_max = difficulty_max
        self.__difficultyMaxCB.select(difficulty_max)


    @property
    def pictureId(self):
        pictureIdStr = self.__pictureIdEF.getEntryText()
        if not pictureIdStr:
            return None
        try:
            return int(pictureIdStr)
        except ValueError:
            raise ve.InvalidPictureIdError


    @pictureId.setter
    def pictureId(self, pictureId):
        if pictureId is None:
            self.__pictureIdEF.deleteEntryText()
        else:
            self.__pictureIdEF.setEntryText(str(pictureId))


    @property
    def comment(self):
        return self.__commentText.get('1.0', tk.END).strip()


    @comment.setter
    def comment(self, comment):
        self.__commentText.delete('1.0', tk.END)
        self.__commentText.insert(tk.END, comment.strip())


    @property
    def stable(self):
        return int(self.__stableVar.get())


    @stable.setter
    def stable(self, stableType):
        self.__stableVar.set(int(stableType))


    def _member(self, master, qdManip):
        self.__qdManip = qdManip
        self.__master = master
        self.__genreId = None
        self.__subGenreId = None
        self.__examGenreId = None
        self.__seriesId = None
        self.__difficulty_min = 1
        self.__difficulty_max = 5
        self.__stableVar = tk.IntVar()
        self.__subGenreFixVar = tk.BooleanVar(value = False)
        self.stable = StableType.Undefined
        self.__searchWindow = None

# other members
# __recorderList :: __makeRecorderList
# __genreBox, __subGenreBox, __examGenreBox, __seriesBox
#     :: __createGenreSeriesFrame
# __questionFrame, __pictureIdEF :: __createQuestionFrame
# __mainNbook :: __createMainNotebook
# __commentText :: __createSupplementalFrame
# __registerButton :: __createBottomButton

    def __init__(self, master, qdManip):
        super().__init__(master)
        self._member(master, qdManip)
        self.__makeRecorderList()
        self.__createWidgets()
        self.setRecordMode(RecordMode.Insert)
        self.pack()


    def __makeRecorderList(self):
        from recorder import Recorder
        self.__recorderList = [
            R(self.__qdManip, self) for R in Recorder.RecorderList
        ]


    def __createWidgets(self):
        self.__createGenreSeriesFrame()
        self.__createQuestionFrame()
        self.__createMainNotebook()
        self.__createSupplementalFrame()
        self.__createBottomButton()


    def __createGenreSeriesFrame(self):
        def onGenreBoxSelect(evt):
            (self.__genreId, genreStr) = self.__genreBox.selectedIdd
            self.__subGenreBox.iddList = self.__qdManip.getSubGenreListOnGenre(
                self.__genreId)
            genreShowLabel['text'] = genreStr
            self.__subGenreId = None
            subGenreShowLabel['text'] = ''

        def onSubGenreBoxSelect(evt):
            (self.__subGenreId, subGenreStr) = self.__subGenreBox.selectedIdd
            subGenreShowLabel['text'] = subGenreStr

        def onExamGenreBoxSelect(evt):
            (self.__examGenreId, examGenreStr) = self.__examGenreBox.selectedIdd
            examGenreShowLabel['text'] = examGenreStr

        def onSeriesBoxSelect(evt):
            (self.__seriesId, seriesStr) = self.__seriesBox.selectedIdd
            seriesShowLabel['text'] = seriesStr

        outerFrame = tk.Frame(self)

        genreFrame = tk.LabelFrame(outerFrame, text = 'ジャンル')
        genreFrame.pack(side = tk.LEFT, anchor = tk.N)
        self.__genreBox = ListboxIdd(genreFrame)
        self.__genreBox.iddList = self.__qdManip.getGenreList()
        self.__genreBox.onSelect = onGenreBoxSelect
        self.__genreBox.pack()
        genreShowLabel = tk.Label(genreFrame, bg = 'LightPink')
        genreShowLabel.pack()

        subGenreFrame = tk.LabelFrame(outerFrame, text = 'サブジャンル')
        subGenreFrame.pack(side = tk.LEFT, anchor = tk.N)
        self.__subGenreBox = ListboxIdd(subGenreFrame)
        self.__subGenreBox.onSelect = onSubGenreBoxSelect
        self.__subGenreBox.pack()
        subGenreShowLabel = tk.Label(subGenreFrame, bg = 'LightSkyBlue')
        subGenreShowLabel.pack()
        subGenreFixCB = tk.Checkbutton(subGenreFrame, text = '固定',
            variable = self.__subGenreFixVar)
        subGenreFixCB.pack()

        examGenreFrame = tk.LabelFrame(outerFrame, text = '検定ジャンル')
        examGenreFrame.pack(side = tk.LEFT, anchor = tk.N)
        examYScroll = tk.Scrollbar(examGenreFrame, orient = tk.VERTICAL)
        examYScroll.pack(side = tk.RIGHT, fill = tk.Y)
        self.__examGenreBox = ListboxIdd(examGenreFrame)
        self.__examGenreBox.iddList = self.__qdManip.getExamGenreList()
        self.__examGenreBox.onSelect = onExamGenreBoxSelect
        self.__examGenreBox['yscrollcommand'] = examYScroll.set
        examYScroll['command'] = self.__examGenreBox.yview
        self.__examGenreBox.pack()
        examGenreShowLabel = tk.Label(examGenreFrame, bg = 'gold')
        examGenreShowLabel.pack()

        seriesFrame = tk.LabelFrame(outerFrame, text = '回収シリーズ')
        seriesFrame.pack(side = tk.LEFT, anchor = tk.N)
        seriesYScroll = tk.Scrollbar(seriesFrame, orient = tk.VERTICAL)
        seriesYScroll.pack(side = tk.RIGHT, fill = tk.Y)
        self.__seriesBox = ListboxIdd(seriesFrame)
        self.__seriesBox.iddList = self.__qdManip.getSeriesList()
        self.__seriesBox.onSelect = onSeriesBoxSelect
        self.__seriesBox['yscrollcommand'] = seriesYScroll.set
        seriesYScroll['command'] = self.__seriesBox.yview
        self.__seriesBox.pack()
        seriesShowLabel = tk.Label(seriesFrame, bg = 'thistle')
        seriesShowLabel.pack()

        outerFrame.pack()


    def __createQuestionFrame(self):
        self.__questionFrame = QuestionFrame(self)
        self.__questionFrame.pack()
        self.__pictureIdEF = EntryFrame(self, text = '画像ID')
        self.__pictureIdEF.pack()


    def __createMainNotebook(self):
        self.__mainNbook = ttk.Notebook(self)
        for recorder in self.__recorderList:
            self.__mainNbook.add(recorder.recordationFrame(),
                text = recorder.quizName)
        self.__mainNbook.pack()


    def __createSupplementalFrame(self):
        def onDifficultyMinCBSelect(evt):
            self.__difficulty_min = self.__difficultyMinCB.selectedId
            self.__difficultyMaxCB.iddList = [
                (ix, d) for (ix, d) in difficultyList
                if self.difficulty_min <= d
            ]

        def onDifficultyMaxCBSelect(evt):
            self.__difficulty_max = self.__difficultyMaxCB.selectedId
            self.__difficultyMinCB.iddList = [
                (ix, d) for (ix, d) in difficultyList
                if d <= self.difficulty_max
            ]

        difficultyList = [(x, x) for x in range(1, 6)]

        outerFrame = tk.Frame(self)

        commentFrame = tk.LabelFrame(outerFrame, text = 'コメント')
        commentFrame.pack()
        self.__commentText = ScrolledText(commentFrame, height = 5)
        self.__commentText.pack()

        difficultyFrame = tk.LabelFrame(outerFrame,
            text = '難易度（最小／最大）')
        difficultyFrame.pack()
        self.__difficultyMinCB = ComboboxIdd(difficultyFrame, state = 'readonly')
        self.__difficultyMinCB.iddList = difficultyList
        self.__difficultyMinCB.onSelect = onDifficultyMinCBSelect
        self.__difficultyMinCB.set(self.difficulty_min)
        self.__difficultyMinCB.pack(side = tk.LEFT)
        self.__difficultyMaxCB = ComboboxIdd(difficultyFrame, state = 'readonly')
        self.__difficultyMaxCB.iddList = difficultyList
        self.__difficultyMaxCB.onSelect = onDifficultyMaxCBSelect
        self.__difficultyMaxCB.set(self.difficulty_max)
        self.__difficultyMaxCB.pack(side = tk.LEFT)

        stableFrame = tk.LabelFrame(outerFrame, text = '安定性')
        stableFrame.pack()
        tk.Radiobutton(
            stableFrame, text = '安定',
            variable = self.__stableVar, value = int(StableType.Stable)
        ).pack(side = tk.LEFT)
        tk.Radiobutton(
            stableFrame, text = '不安定',
            variable = self.__stableVar, value = int(StableType.Unstable)
        ).pack(side = tk.LEFT)

        outerFrame.pack()


    def __createBottomButton(self):
        def clear():
            if self.recordMode == RecordMode.Insert:
                if not messagebox.askokcancel('askokcancel',
                        '入力をクリアする？'):
                    return
            else:
                if not messagebox.askokcancel('askokcancel',
                        '編集をキャンセルする？'):
                    return
            self.__cleanUpAll()
            self.setRecordMode(RecordMode.Insert)

        bottomFrame = tk.Frame(self)
        clearButton = tk.Button(bottomFrame, text = 'クリア')
        clearButton['command'] = clear
        clearButton.pack(side = tk.LEFT)
        paddingFrame = tk.Frame(bottomFrame, width = 10)
        paddingFrame.pack(side = tk.LEFT)
        searchButton = tk.Button(bottomFrame, text = '問題検索')
        searchButton['command'] = self.__createSearchWindow
        searchButton.pack(side = tk.LEFT)
        paddingFrame = tk.Frame(bottomFrame, width = 10)
        paddingFrame.pack(side = tk.LEFT)
        self.__registerButton = tk.Button(bottomFrame, fg = 'red')
        self.__registerButton['command'] = self.__record
        self.__registerButton.pack(side = tk.LEFT)
        bottomFrame.pack(anchor = tk.E)


    def __getCurrentRecorder(self):
        ix = self.__mainNbook.index(self.__mainNbook.select())
        return self.__recorderList[ix]


    def __createSearchWindow(self):
        def onDestroy(evt):
            self.__searchWindow = None
        if self.__searchWindow:
            self.__searchWindow.destroy()
        recorder = self.__getCurrentRecorder()
        self.__searchWindow = SearchWindow(self, recorder)
        self.__searchWindow.bind('<Destroy>', onDestroy)


    def __record(self):
        recorder = self.__getCurrentRecorder()
        try:
            self.__validationCommon()
            recorder.record(self.__quizId)
            self.__qdManip.save()
            if self.recordMode == RecordMode.Insert:
                messagebox.showinfo('登録完了', '登録したよ！')
            else:
                messagebox.showinfo('編集完了', '編集したよ！')
            self.__cleanUpAll()
        except ve.ValidationError as verr:
            messagebox.showwarning('登録失敗', verr.message)
        except IntegrityError:
            messagebox.showwarning('登録失敗',
                '既に同じクイズが登録されているよ！')


    def __validationCommon(self):
        if self.genreId is None:
            raise ve.GenreNoneError
        if self.subGenreId is None:
            raise ve.SubGenreNoneError
        if self.examGenreId is None:
            raise ve.ExamGenreNoneError
        if self.seriesId is None:
            raise ve.SeriesIdNoneError
        if not self.question:
            raise ve.QuestionBlankError
        if self.stable == StableType.Undefined:
            raise ve.StableTypeUndefinedError


    def __cleanUpAll(self):
        self.__questionFrame.question = ''
        self.pictureId = None
        self.comment = ''
        self.stable = StableType.Undefined
        if not self.__subGenreFixVar.get():
            self.__genreBox.select(self.genreId)
        for recorder in self.__recorderList:
            recorder.cleanUp()



class SearchWindow(tk.Toplevel):
    def __init__(self, master, recorder):
        super().__init__(master)
        self.title('問題検索')
        self.__recorder = recorder
        self.__createMain()


    def __createMain(self):
        yscroll = tk.Scrollbar(self)
        yscroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)
        xscroll = tk.Scrollbar(self, orient = tk.HORIZONTAL)
        xscroll.grid(row = 1, column = 0, sticky = tk.E + tk.W)
        canvas = tk.Canvas(self,
            yscrollcommand = yscroll.set,
            xscrollcommand = xscroll.set)
        canvas.grid(row = 0, column = 0,
            sticky = tk.N + tk.S + tk.E + tk.W)
        yscroll.config(command = canvas.yview)
        xscroll.config(command = canvas.xview)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        innerFrame = tk.Frame(canvas)
        innerFrame.rowconfigure(1, weight = 1)
        innerFrame.columnconfigure(1, weight = 1)

        searchResult = self.__recorder.search()
        for (rowIx, rowItem) in enumerate(searchResult):
            for (columnIx, columnItem) in enumerate(rowItem):
                l = tk.Label(innerFrame, text = columnItem, relief = tk.RIDGE,
                    justify = tk.LEFT, wraplength = 150)
                l.grid(row = rowIx, column = columnIx + 1,
                    sticky = tk.W + tk.E + tk.N + tk.S)
            if rowIx > 0:
                quizId = searchResult[rowIx][0]
                editButton = tk.Button(innerFrame, text = '編集',
                    command = self.__onEditButtonPush(quizId))
                editButton.grid(row = rowIx, column = 0,
                    sticky = tk.W + tk.E + tk.N + tk.S)

        canvas.create_window(0, 0, anchor = tk.NW, window = innerFrame)
        innerFrame.update_idletasks()
        canvas.config(scrollregion = canvas.bbox("all"))
        self.__bindMouseWheel(canvas)
        canvas.config(width = innerFrame.winfo_width())


    def __bindMouseWheel(self, canvas):
        def onMouseWheel(evt):
            factor = 1
            if OS == 'Linux':
                if evt.num == 4:
                    canvas.yview_scroll(-1 * factor, tk.UNITS)
                elif evt.num == 5:
                    canvas.yview_scroll(factor, tk.UNITS)
            elif OS == 'Windows':
                canvas.yview_scroll(-1 * int((evt.delta / 120) * factor),
                    tk.UNITS)
            elif OS == 'Darwin':
                canvas.yview_scroll(evt.delta, tk.UNITS)


        OS = platform.system()
        if OS == 'Linux':
            canvas.bind_all('<Button-4>', onMouseWheel)
            canvas.bind_all('<Button-5>', onMouseWheel)
        else:
            canvas.bind_all('<MouseWheel>', onMouseWheel)



    def __onEditButtonPush(self, quizId):
        def onEditButtonPush():
            if not messagebox.askokcancel('askokcancel',
                    'いま編集中のデータは破棄されるけどいい？'):
                return
            self.__recorder.edit(quizId)
            self.destroy()
        return onEditButtonPush
