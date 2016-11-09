import random
import tkinter as tk
from tkinter import messagebox

from dbmanip import QuestionDataDBManip



class QuizQuestionFrame(tk.Frame):
    @property
    def text(self):
        return self._text.get()


    @text.setter
    def text(self, text):
        self._text.set(text)


    def __init__(self, master, **option):
        self._text = tk.StringVar(value = option.pop('text', ''))
        super().__init__(master, **option)
        font = ('Meiryo', 20)
        self.label = tk.Label(self, width = 24, height = 10,
            anchor = tk.NW, justify = tk.LEFT, bg = 'pale green',
            textvariable = self._text, font = font, wraplength = '11c')
        self.label.pack()



class QuizButtonRect(tk.Frame):
    @property
    def text(self):
        return self._text.get()


    @text.setter
    def text(self, text):
        self._text.set(text)


    @property
    def tag(self):
        return self._tag.get()


    @tag.setter
    def tag(self, tag):
        self._tag.set(tag)


    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, value):
        self._value = value


    def setButtonCommand(self, command):
        self.button.config(command = lambda: command(self))


    def __init__(self, master, **option):
        self._tag = tk.StringVar(value = option.pop('tag', ''))
        self._text = tk.StringVar(value = option.pop('text', ''))
        self._value = option.pop('value', None)
        super().__init__(master, **option)
        font = ('Meiryo', 15)
        height = 1
        width = (3, 28)
        self.label = tk.Label(self, width = width[0], height = height,
            textvariable = self._tag, font = font,
            bg = 'violetRed1')
        self.label.pack(side = tk.LEFT)
        self.button = tk.Button(self, width = width[1], height = height,
            textvariable = self._text, font = font,
            bg = 'LightGoldenrod1', activebackground = 'khaki3')
        self.button.pack(side = tk.LEFT)



class PlayMain(tk.Frame):
    def _member(self, master, qdManip):
        self._master = master
        self._qdManip = qdManip
        self._questionCount = 0
        self._correctCount = 0


    def __init__(self, master, qdManip):
        super().__init__(master)
        self._member(master, qdManip)
        self._createQuestionFrame()
        self._createButtonRect()
        self.pack()
        self._main()


    def _createQuestionFrame(self):
        self.questionF = QuizQuestionFrame(self)
        self.questionF.pack()


    def _createButtonRect(self):
        paddingHeight = 30
        self.ansB1 = QuizButtonRect(self, tag = 1)
        self.ansB1.pack()
        tk.Frame(self, height = paddingHeight).pack()
        self.ansB2 = QuizButtonRect(self, tag = 2)
        self.ansB2.pack()
        tk.Frame(self, height = paddingHeight).pack()
        self.ansB3 = QuizButtonRect(self, tag = 3)
        self.ansB3.pack()
        tk.Frame(self, height = paddingHeight).pack()
        self.ansB4 = QuizButtonRect(self, tag = 4)
        self.ansB4.pack()


    def _main(self):
        quizList = self._qdManip.select(
            ['question', 'answer', 'dummy1', 'dummy2', 'dummy3', 'comment'],
            'quiz_assoc'
        )
        random.shuffle(quizList)
        self._mainloop(quizList)


    def _mainloop(self, quizList):
        def ansBCommand(ansB):
            self._questionCount += 1
            if ansB.value:
                self._correctCount += 1
                messagebox.showinfo('正解！',
                    '正解だよ！\n\n{}'.format(comment))
            else:
                messagebox.showerror('はずれ！',
                    '間違いだよ！\n\n{}'.format(comment))
            self._mainloop(quizList)

        if not quizList:
            self._finish()
            return
        quiz = quizList.pop()
        (question, answer, dummy1, dummy2, dummy3, comment) = quiz
        self.questionF.text = question
        optionList = [(answer, True),(dummy1, False),
            (dummy2, False), (dummy3, False)]
        random.shuffle(optionList)
        ansBList = [self.ansB1, self.ansB2, self.ansB3, self.ansB4]
        for (ansB, option) in zip(ansBList, optionList):
            (ansB.text, ansB.value) = option
            ansB.setButtonCommand(ansBCommand)


    def _finish(self):
        messagebox.showinfo('終了！',
            '今回の成績は {} 問 / {} 問だよ！'.format(self._correctCount,
                self._questionCount))
        self._master.destroy()


if __name__ == '__main__':
    qdManip = QuestionDataDBManip('question_data.sqlite3')
    root = tk.Tk()
    app = PlayMain(root, qdManip)
    app.mainloop()
    qdManip.close()
