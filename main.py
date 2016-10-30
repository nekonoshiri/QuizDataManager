import tkinter as tk

from dbmanip import QuestionDataDBManip
from quizdatamanager import QuizDataManager



if __name__ == '__main__':
    qdManip = QuestionDataDBManip('question_data.sqlite3')
    root = tk.Tk()
    app = QuizDataManager(root, qdManip)
    app.mainloop()
    qdManip.close()

