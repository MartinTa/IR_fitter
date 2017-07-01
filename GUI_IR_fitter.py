#!/usr/bin/env python
#import tkinter as tk
#from tkinter import ttk
#from tkinter import filedialog
#
#root = tk.Tk()
#note = ttk.Notebook(root)
#tab1 = tk.Frame(note)
#tab2 = tk.Frame(note)
#tab3 = tk.Frame(note)
#tk.Listbox(tab1).pack(padx=0,pady=0,expand=tk.YES, fill=tk.BOTH)
#tk.Button(tab1, text='browse', command=lambda: filedialog.askopenfilenames()).pack(padx=20, pady=20)
#
#
#note.add(tab1, text = "Tab One")
#note.add(tab2, text = "Settings")
#note.add(tab3, text = "Tab Three")
#note.pack()
#root.mainloop()


#!/usr/bin/env python
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
class Application():
    def __init__(self,parent):
        self.parent = parent
        self.note = ttk.Notebook(self.parent)
        self.tab1 = tk.Frame(self.note,background="red")
        self.tab2 = tk.Frame(self.note)
        self.tab3 = tk.Frame(self.note)
        self.createWidgets()
    def createWidgets(self):
        self.parent.title("GUI_IR_fitter")
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.note.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.note.add(self.tab1, text = "Tab One")
        self.note.add(self.tab2, text = "Settings")
        self.note.add(self.tab3, text = "Tab Three")
        self.note.grid()
        self.tab1.rowconfigure(0, weight=1)
        self.tab1.columnconfigure(0, weight=1)
        
        self.browseButton = tk.Button(self.tab1, text='browse',command=lambda: filedialog.askopenfilenames(),background="green")
        self.browseButton.grid(row=0, column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        
        
root = tk.Tk()
app = Application(root)
root.mainloop()
#app.master.title('Sample application')
#app.mainloop()
