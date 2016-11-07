from enum import Enum
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import re

from mojiutil import MojiUtil



class QuestionFormatMode(Enum):
    KeepNewLine = 0
    SmashNewLine = 1



class QuestionFrame(tk.LabelFrame):
    def __init__(self, master, **option):
        option.setdefault('text', '問題')
        super().__init__(master, **option)
        self.questionText = ScrolledText(self, height = 5)
        self.questionText.pack(side = tk.LEFT)
        formatButton = tk.Button(self, text = '整形')
        formatButton['command'] = self.formatQuestion
        formatButton.pack(side = tk.LEFT)
        self.formatMode = QuestionFormatMode.SmashNewLine


    @property
    def question(self):
        return self.questionText.get('1.0', tk.END).strip()


    @question.setter
    def question(self, question):
        self.questionText.delete('1.0', tk.END)
        self.questionText.insert(tk.END, question.strip())


    def formatQuestion(self):
        question = self.question
        # まず改行文字で分割
        questionList = question.split('\n')
        # 文中の空白類文字の削除
        questionList = [''.join(q.split()) for q in questionList]
        # 空要素の削除
        questionList = [q for q in questionList if q]
        # 連結
        if self.formatMode == QuestionFormatMode.SmashNewLine:
            question = ''.join(questionList)
        else:
            question = '\n'.join(questionList)
        # ,.?! の置き換え
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
        option.setdefault('text', '答え（改行区切り）')
        super().__init__(master, **option)
        self.answerText = ScrolledText(self, height = 5)
        self.answerText.pack()


    @property
    def answer(self):
        answerStr = self.answerText.get('1.0', tk.END).strip()
        answerList = answerStr.split('\n')
        return [ans.strip() for ans in answerList if ans.strip()]


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

