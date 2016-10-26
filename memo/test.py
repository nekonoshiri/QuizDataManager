import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk ()


noteBook = ttk.Notebook ()

button1 = tk.Button ()
button1['text'] = 'Button1'

button2 = tk.Button ()
button2['text'] = 'Button2'

noteBook.add (button1, text = 'tab1')
noteBook.add (button2, text = 'tab2')

noteBook.pack ()

root.mainloop ()
