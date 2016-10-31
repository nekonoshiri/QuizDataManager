from sqlite3 import IntegrityError
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from tkcommon import EntryFrame
from tkhelper import ListboxIdd, ComboboxIdd
import validationException as ve



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
        from recorder import Recorder
        self.__recorderList = []
        for recorder in Recorder.RecorderList:
            self.__recorderList.append(recorder(self.__qdManip))


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

