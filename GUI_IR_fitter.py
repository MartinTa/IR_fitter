#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import IR_fitter
import os

class Application():
    def __init__(self,parent):
        self.parent = parent
        self.note = ttk.Notebook(self.parent,width=500,height=300)
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
        ## tab1
        self.tab1.rowconfigure(0, weight=1)
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.columnconfigure(1, weight=1)
        self.tab1.columnconfigure(2, weight=1)
        self.tab1.columnconfigure(3, weight=1)
        self.listbox = tk.Listbox(self.tab1,selectmode=tk.EXTENDED)
        self.listbox.grid(row=0,columnspan=4,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.browseButton = tk.Button(self.tab1, text='browse/add',command=self.BrowseClick)
        self.browseButton.grid(row=1, column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.removeButton = tk.Button(self.tab1, text='remove',command=self.RemoveClick)
        self.removeButton.grid(row=1, column=1,sticky=tk.N+tk.S+tk.E+tk.W)
        self.plotButton = tk.Button(self.tab1, text='plot',command=self.PlotClick,background="green")
        self.plotButton.grid(row=1, column=2,sticky=tk.N+tk.S+tk.E+tk.W)
        self.quantifyButton = tk.Button(self.tab1, text='quantify',command=self.Quantify,background="green")
        self.quantifyButton.grid(row=1, column=3,sticky=tk.N+tk.S+tk.E+tk.W)
        self.statusline = tk.Label(self.tab1)
        self.statusline.grid(row=2,column=0,columnspan=4,sticky=tk.N+tk.S+tk.E+tk.W)
    def BrowseClick(self):
        filepaths = filedialog.askopenfilenames()
        for filepath in filepaths:
            self.listbox.insert(tk.END,filepath)
    def RemoveClick(self):
        indices = self.listbox.curselection()
        for index in reversed(indices):
            self.listbox.delete(index)
    def PlotClick(self):
        indices = self.listbox.curselection()
        for index in indices:
            filepath = str(self.listbox.get(index))
            name = os.path.split(filepath)[1]
            spectrum = self.GetSpectrumWithCurrentSettings(name,filepath)
            IR_fitter.PlotAbsorbances(spectrum)
    def Quantify(self):
        index = self.listbox.curselection()
        if len(index) != 1:
            self.statusline["text"] = "Error, choose exactly one composite sample to quantify!"
        else:
            self.statusline["text"] = ""
            k_min = 1000#float(eval(app.getEntry(k_min_name_quantification)))
            k_max = 2000#float(eval(app.getEntry(k_max_name_quantification)))
            component_spectra = []
            filepaths = list(self.listbox.get(0,tk.END))
            composition_filepath = filepaths.pop(index[0])
            for filepath in filepaths:
                name = os.path.splitext(os.path.split(filepath)[1])[0]
                chunks = name.split('_')
                if len(chunks) < 2 or chunks[-1] != "nm":
                    self.statusline["text"] = "Error: name of component has to have _thickness_nm.DX at the end, where thickness is a number"
                    return 1
                thickness = float(chunks[-2])
                spectrum = self.GetSpectrumWithCurrentSettings(name,filepath,thickness=thickness,normalize_by_thickness=True)
                component_spectra.append(spectrum)
            composition_name = os.path.split(composition_filepath)[1]
            composite_spectrum = self.GetSpectrumWithCurrentSettings(composition_name,composition_filepath)
            results = IR_fitter.CalculateSuperposition(composite_spectrum, component_spectra,k_min=k_min, k_max=k_max)
            d_vec,d_error_vec,F_vec,F_error_vec = results["d_vec"],results["d_error_vec"],results["F_vec"],results["F_error_vec"]
            txt_list = ['Superposition of sample {} calculated:'.format(composite_spectrum.name)]
            for k,s in enumerate(component_spectra):
                txt_list.append('d_{} = {}'.format(s.name,IR_fitter.GetErrorString(d_vec[k],d_error_vec[k])))
                txt_list.append('F_{} = {}'.format(s.name,IR_fitter.GetErrorString(F_vec[k],F_error_vec[k])))
            txt_list.append('d = {}'.format(IR_fitter.GetErrorString(np.sum(d_vec),np.sum(d_error_vec)))) 
            #app.setMessage("mess",os.linesep.join(txt_list))
            IR_fitter.PlotSuperposition(results,composite_spectrum, component_spectra,
                              k_min=k_min,
                              k_max=k_max,
                              interactive_plot=True)
    def GetSpectrumWithCurrentSettings(self,name,filepath,thickness=None,normalize_by_thickness=False):
        spectrum = IR_fitter.absorbance_spectrum(name=name,
                   datafile_path=filepath,
                   thickness=thickness,
                   normalize_by_thickness=normalize_by_thickness,
                   k_min = 800,#float(eval(app.getEntry(k_min_name_baseline))),
                   k_max = np.inf,#float(eval(app.getEntry(k_max_name_baseline))),
                   r = 1E8,#float(eval(app.getEntry(r_name))),
                   p = 0.005)#float(eval(app.getEntry(p_name))))
        return spectrum
        
root = tk.Tk()
app = Application(root)
root.mainloop()
#app.master.title('Sample application')
#app.mainloop()
