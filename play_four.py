import random
import tkinter as tk
from tkinter import messagebox

from dbmanip import QuestionDataDBManip
from util import findIndex



class QuizQuestionFrame(tk.Frame):
    @property
    def position(self):
        return self._position


    @position.setter
    def position(self, position):
        self._position = position
        self._textVar.set(self._text[:position])


    @property
    def text(self):
        return self._text


    @text.setter
    def text(self, text):
        self._text = text


    def __init__(self, master, **option):
        self._text = option.pop('text', '')
        self.interval = option.pop('interval', 30)
        self._position = 0
        self._textVar = tk.StringVar()
        super().__init__(master, **option)
        tk.Label(self, width = 24, height = 10,
            anchor = tk.NW, justify = tk.LEFT, bg = 'pale green',
            textvariable = self._textVar, font = ('Meiryo', 20),
            wraplength = '11c').pack()


    def posInc(self):
        self.position = self.position + 1


    def posReset(self):
        self.position = 0


    def posEnd(self):
        self.position = len(self.text)


    def startQuestion(self):
        def posIncLoop():
            self.posInc()
            if self.position > len(self.text):
                return
            self.after(self.interval, posIncLoop)

        self.posReset()
        posIncLoop()



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



class QuizButtonRectFourFrame(tk.Frame):
    def __init__(self, master, **option):
        paddingHeight = option.pop('padH', 30)
        super().__init__(master, **option)
        self._answerButton1 = QuizButtonRect(self, tag = 1)
        self._answerButton1.pack()
        tk.Frame(self, height = paddingHeight).pack()
        self._answerButton2 = QuizButtonRect(self, tag = 2)
        self._answerButton2.pack()
        tk.Frame(self, height = paddingHeight).pack()
        self._answerButton3 = QuizButtonRect(self, tag = 3)
        self._answerButton3.pack()
        tk.Frame(self, height = paddingHeight).pack()
        self._answerButton4 = QuizButtonRect(self, tag = 4)
        self._answerButton4.pack()
        self._answerButtons = (self._answerButton1, self._answerButton2,
            self._answerButton3, self._answerButton4)


    def setButtonsText(self, textB1, textB2, textB3, textB4):
        self._answerButton1.text = textB1
        self._answerButton2.text = textB2
        self._answerButton3.text = textB3
        self._answerButton4.text = textB4


    def setAnswerButton(self, answerButtonNumber):
        if answerButtonNumber < 1 or answerButtonNumber > 4:
            return
        for answerButton in self._answerButtons:
            answerButton.value = False
        self._answerButtons[answerButtonNumber - 1].value = True


    def setOptionRandomly(self, answer, dummy1, dummy2, dummy3):
        optionList = [(answer, True),(dummy1, False),
            (dummy2, False), (dummy3, False)]
        random.shuffle(optionList)
        answerButtonNumber = findIndex(lambda x: x[1], optionList) + 1
        options = [x[0] for x in optionList]
        self.setAnswerButton(answerButtonNumber)
        self.setButtonsText(options[0], options[1], options[2], options[3])


    def setButtonCommand(self, command):
        self._answerButton1.setButtonCommand(command)
        self._answerButton2.setButtonCommand(command)
        self._answerButton3.setButtonCommand(command)
        self._answerButton4.setButtonCommand(command)



class PlayMain(tk.Frame):
    def _member(self, master, qdManip):
        self._master = master
        self._qdManip = qdManip
        self._questionCount = 0
        self._correctCount = 0
        self._comment = ''
        self._quizList = self._qdManip.select(
            ['question', 'answer', 'dummy1', 'dummy2', 'dummy3', 'comment'],
            'quiz_four'
        )
        random.shuffle(self._quizList)


    def __init__(self, master, qdManip):
        super().__init__(master)
        self._member(master, qdManip)
        self._createQuestionFrame()
        self._createButtonFrame()
        self.pack()
        self._setNextQuestion()


    def _createQuestionFrame(self):
        self.questionFrame = QuizQuestionFrame(self)
        self.questionFrame.pack()


    def _createButtonFrame(self):
        def buttonCommand(ansB):
            self._questionCount += 1
            self._answerShowMsgBox(ansB.value)

            self._setNextQuestion()

        self.buttonFrame =  QuizButtonRectFourFrame(self)
        self.buttonFrame.setButtonCommand(buttonCommand)
        self.buttonFrame.pack()


    def _answerShowMsgBox(self, value):
        if value:
            self._correctCount += 1
            messagebox.showinfo('正解！',
                '正解だよ！\n\n{}'.format(self._comment))
        else:
            messagebox.showerror('はずれ！',
                '間違いだよ！\n\n{}'.format(self._comment))



    def _setNextQuestion(self):
        if not self._quizList:
            self._finish()
            return
        (question, answer,
            dummy1, dummy2, dummy3, comment) = self._quizList.pop()
        self.questionFrame.text = question
        self._comment = comment
        self.buttonFrame.setOptionRandomly(answer, dummy1, dummy2, dummy3)
        self.questionFrame.startQuestion()


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
