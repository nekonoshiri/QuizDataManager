from enum import Enum
from sqlite3 import IntegrityError
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkcommon import EntryFrame
from tkhelper import ListboxIdd, ComboboxIdd
import validationException as ve



class RecordMode(Enum):
    Insert = 0
    Update = 1



class QuizDataManager(tk.Frame):
    # difficulty_min = 1
    # difficulty_max = 5


# Instance Variables
# __qdManip, __master, __stableVar, __searchWindow :: __init__
# __genreId, __subGenreId, __examGenreId, __seriesId,
# __difficulty_min, __difficulty_max :: __init__
# __recorderList :: __makeRecorderList
# __genreBox, __subGenreBox, __examGenreBox, __seriesBox
#     :: __createGenreSeriesFrame
# __mainNbook :: __createMainNotebook
# __pictureIdEF, __commentText :: __createSupplementalFrame
# __registerButton :: __createBottomButton


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
        return self.__stableVar.get()


    @stable.setter
    def stable(self, isStable):
        self.__stableVar.set(isStable)


    def __init__(self, master, qdManip):
        super().__init__(master)
        self.__qdManip = qdManip
        self.__master = master
        self.__genreId = None
        self.__subGenreId = None
        self.__examGenreId = None
        self.__seriesId = None
        self.__difficulty_min = 1
        self.__difficulty_max = 5
        self.__stableVar = tk.BooleanVar()
        self.stable = False
        self.__searchWindow = None
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
        self.__createMainNotebook()
        self.__createSupplementalFrame()
        self.__createBottomButton()


    def __createGenreSeriesFrame(self):
        def onGenreBoxSelect(evt):
            (self.__genreId, genreStr) = self.__genreBox.selectedIdd
            self.__subGenreBox.iddList = self.__qdManip.getSubGenreListOnGenre(
                self.__genreId)
            genreShowLabel['text'] = genreStr
            self.subGenreId = None

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
        genreFrame.pack(side = tk.LEFT)
        self.__genreBox = ListboxIdd(genreFrame)
        self.__genreBox.iddList = self.__qdManip.getGenreList()
        self.__genreBox.onSelect = onGenreBoxSelect
        self.__genreBox.pack()
        genreShowLabel = tk.Label(genreFrame, bg = 'LightPink')
        genreShowLabel.pack()

        subGenreFrame = tk.LabelFrame(outerFrame, text = 'サブジャンル')
        subGenreFrame.pack(side = tk.LEFT)
        self.__subGenreBox = ListboxIdd(subGenreFrame)
        self.__subGenreBox.onSelect = onSubGenreBoxSelect
        self.__subGenreBox.pack()
        subGenreShowLabel = tk.Label(subGenreFrame, bg = 'LightSkyBlue')
        subGenreShowLabel.pack()

        examGenreFrame = tk.LabelFrame(outerFrame, text = '検定ジャンル')
        examGenreFrame.pack(side = tk.LEFT)
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
        seriesFrame.pack(side = tk.LEFT)
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

        self.__pictureIdEF = EntryFrame(outerFrame, text = '画像ID')
        self.__pictureIdEF.pack()

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
            variable = self.__stableVar, value = True
        ).pack(side = tk.LEFT)
        tk.Radiobutton(
            stableFrame, text = '不安定',
            variable = self.__stableVar, value = False
        ).pack(side = tk.LEFT)

        outerFrame.pack()


    def __createBottomButton(self):
        bottomFrame = tk.Frame(self)
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
            self.__validationGenreIdAndSeriesId()
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


    def __validationGenreIdAndSeriesId(self):
        if self.genreId is None:
            raise ve.GenreNoneError
        if self.subGenreId is None:
            raise ve.SubGenreNoneError
        if self.examGenreId is None:
            raise ve.ExamGenreNoneError
        if self.seriesId is None:
            raise ve.SeriesIdNoneError


    def __cleanUpAll(self):
        self.pictureId = None
        self.comment = ''
        self.stable = False
        for recorder in self.__recorderList:
            recorder.cleanUp()



class SearchWindow(tk.Toplevel):
    def __init__(self, master, recorder):
        super().__init__(master)
        self.title('問題検索')
        self.__recorder = recorder
        self.__createMain()


    def __createMain(self):
        searchResult = self.__recorder.search()
        for (rowIx, rowItem) in enumerate(searchResult):
            for (columnIx, columnItem) in enumerate(rowItem):
                l = tk.Label(self, text = columnItem, relief = tk.RIDGE)
                l.grid(row = rowIx, column = columnIx,
                    sticky = tk.W + tk.E + tk.N + tk.S)
            if rowIx > 0:
                quizId = searchResult[rowIx][0]
                editButton = tk.Button(self, text = '編集',
                    command = self.__onEditButtonPush(quizId))
                editButton.grid(row = rowIx, column = columnIx + 1,
                    sticky = tk.W + tk.E + tk.N + tk.S)


    def __onEditButtonPush(self, quizId):
        def onEditButtonPush():
            if not messagebox.askokcancel('askokcancel',
                    'いま編集中のデータは破棄されるけどいい？'):
                return
            self.__recorder.edit(quizId)
            self.destroy()
        return onEditButtonPush
