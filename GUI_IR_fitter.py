#!/usr/bin/env python

import matplotlib
matplotlib.use('TkAgg') # use this tk compatible matplotlib backend for IR_fitter
from matplotlib import pyplot as plt
plt.ion()
import IR_fitter
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import os

class Application():
    def __init__(self,parent):
        self.parent = parent
        self.note = ttk.Notebook(self.parent,width=650,height=300)
        self.tab1 = tk.Frame(self.note)
        self.tab2 = tk.Frame(self.note)
        self.tab3 = tk.Frame(self.note)
        self.createWidgets()
    def createWidgets(self):
        self.parent.title("GUI_IR_fitter")
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.note.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.note.add(self.tab1, text = "Main")
        self.note.add(self.tab2, text = "Settings")
        self.note.add(self.tab3, text = "Quantification Results")
        self.note.grid()
        ## tab1
        self.tab1.rowconfigure(0, weight=1)
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.columnconfigure(1, weight=1)
        self.tab1.columnconfigure(2, weight=1)
        self.tab1.columnconfigure(3, weight=1)
        self.tab1.columnconfigure(4, weight=1)
        self.tab1.columnconfigure(5, weight=1)
        self.listbox = tk.Listbox(self.tab1,selectmode=tk.EXTENDED)
        self.listbox.grid(row=0,columnspan=6,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.status = tk.StringVar()
        self.statusline = tk.Label(self.tab1,textvariable=self.status,height=2,wraplength=650)
        self.statusline.grid(row=2,column=0,columnspan=6,sticky=tk.N+tk.S+tk.E+tk.W)
        self.browseButton = tk.Button(self.tab1, text='browse/add',command=self.BrowseClick)
        self.browseButton.grid(row=1, column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.browseButton.bind("<Enter>",lambda event: self.status.set("browse for spectrum files (.DX or .DPT) and add them to list"))
        self.browseButton.bind("<Leave>",lambda event: self.status.set(""))
        self.removeButton = tk.Button(self.tab1, text='remove',command=self.RemoveClick)
        self.removeButton.grid(row=1, column=1,sticky=tk.N+tk.S+tk.E+tk.W)
        self.removeButton.bind("<Enter>",lambda event: self.status.set("remove selected files"))
        self.removeButton.bind("<Leave>",lambda event: self.status.set(""))
        self.plotButton = tk.Button(self.tab1, text='plot',command=self.PlotClick)
        self.plotButton.grid(row=1, column=2,sticky=tk.N+tk.S+tk.E+tk.W)
        self.plotButton.bind("<Enter>",lambda event: self.status.set("plot spectrum and baseline of selected files"))
        self.plotButton.bind("<Leave>",lambda event: self.status.set(""))
        self.exportCsvButton = tk.Button(self.tab1, text='export csv',command=self.ExportCsvClick)
        self.exportCsvButton.grid(row=1, column=3,sticky=tk.N+tk.S+tk.E+tk.W)
        self.exportCsvButton.bind("<Enter>",lambda event: self.status.set("export spectrum and baseline of each selected file as csv (only within baseline wavenumbers)"))
        self.exportCsvButton.bind("<Leave>",lambda event: self.status.set(""))
        self.quantify_plot_button = tk.Button(self.tab1, text='quantify/plot',command=self.QuantifyPlotClick)
        self.quantify_plot_button.grid(row=1, column=4,sticky=tk.N+tk.S+tk.E+tk.W)
        self.quantify_plot_button.bind("<Enter>",lambda event: self.status.set("quantify and plot selected composit spectrum"))
        self.quantify_plot_button.bind("<Leave>",lambda event: self.status.set(""))
        self.quantify_export_button = tk.Button(self.tab1, text='quantify/plot/export',command=self.QuantifyExportClick)
        self.quantify_export_button.grid(row=1, column=5,sticky=tk.N+tk.S+tk.E+tk.W)
        self.quantify_export_button.bind("<Enter>",lambda event: self.status.set("quantify, plot and export selected composit spectrum, its baseline and baseline corrected standard spectra scaled by their fitting coefficient, only within quantification wavenumbers"))
        self.quantify_export_button.bind("<Leave>",lambda event: self.status.set(""))
        ## tab2
        self.tab2.columnconfigure(0, weight=1)
        self.labelframe_baseline=tk.LabelFrame(self.tab2,text="Baseline Settings",background='white')
        self.labelframe_baseline.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.labelframe_baseline.rowconfigure(0,weight=1)
        self.labelframe_baseline.rowconfigure(1,weight=1)
        self.labelframe_baseline.columnconfigure(0,weight=1)
        self.labelframe_baseline.columnconfigure(1,weight=1)
        self.labelframe_baseline.columnconfigure(2,weight=1)
        self.labelframe_baseline.columnconfigure(3,weight=1)
        self.labelframe_baseline.columnconfigure(4,weight=1)
        self.labelframe_baseline.columnconfigure(5,weight=1)
        tk.Label(self.labelframe_baseline,text="k_min = ").grid(row=0,column=0,sticky=tk.N+tk.S+tk.E)
        self.baseline_kmin = tk.Entry(self.labelframe_baseline)
        self.baseline_kmin.insert(0,"800")
        self.baseline_kmin.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W)
        tk.Label(self.labelframe_baseline,text="1/cm").grid(row=0,column=2,sticky=tk.N+tk.S+tk.W)
        tk.Label(self.labelframe_baseline,text="k_max = ").grid(row=0,column=3,sticky=tk.N+tk.S+tk.E)
        self.baseline_kmax = tk.Entry(self.labelframe_baseline)
        self.baseline_kmax.insert(0,"np.inf")
        self.baseline_kmax.grid(row=0,column=4,sticky=tk.N+tk.S+tk.E+tk.W)
        tk.Label(self.labelframe_baseline,text="1/cm").grid(row=0,column=5,sticky=tk.N+tk.S+tk.W)

        tk.Label(self.labelframe_baseline,text="r = ").grid(row=1,column=0,sticky=tk.N+tk.S+tk.E)
        self.r = tk.Entry(self.labelframe_baseline)
        self.r.insert(0,"1E8")
        self.r.grid(row=1,column=1,sticky=tk.N+tk.S+tk.E+tk.W)
        tk.Label(self.labelframe_baseline,text="p = ").grid(row=1,column=3,sticky=tk.N+tk.S+tk.E)
        self.p = tk.Entry(self.labelframe_baseline)
        self.p.insert(0,"0.005")
        self.p.grid(row=1,column=4,sticky=tk.N+tk.S+tk.E+tk.W)        
        
        self.labelframe_quantification=tk.LabelFrame(self.tab2,text="Quantification Settings",background='white')
        self.labelframe_quantification.grid(row=1,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.labelframe_quantification.rowconfigure(0,weight=1)
        self.labelframe_quantification.columnconfigure(0,weight=1)
        self.labelframe_quantification.columnconfigure(1,weight=1)
        self.labelframe_quantification.columnconfigure(2,weight=1)
        self.labelframe_quantification.columnconfigure(3,weight=1)
        self.labelframe_quantification.columnconfigure(4,weight=1)
        self.labelframe_quantification.columnconfigure(5,weight=1)        
        
        tk.Label(self.labelframe_quantification,text="k_min = ").grid(row=0,column=0,sticky=tk.N+tk.S+tk.E)
        self.quantification_kmin = tk.Entry(self.labelframe_quantification)
        self.quantification_kmin.insert(0,"1000")
        self.quantification_kmin.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W)
        tk.Label(self.labelframe_quantification,text="1/cm").grid(row=0,column=2,sticky=tk.N+tk.S+tk.W)
        tk.Label(self.labelframe_quantification,text="k_max = ").grid(row=0,column=3,sticky=tk.N+tk.S+tk.E)
        self.quantification_kmax = tk.Entry(self.labelframe_quantification)
        self.quantification_kmax.insert(0,"2000")
        self.quantification_kmax.grid(row=0,column=4,sticky=tk.N+tk.S+tk.E+tk.W)
        tk.Label(self.labelframe_quantification,text="1/cm").grid(row=0,column=5,sticky=tk.N+tk.S+tk.W)
        #tab3
        self.tab3.rowconfigure(0, weight=1)
        self.tab3.columnconfigure(0, weight=1)
        self.quantification_text = tk.Text(self.tab3)
        self.quantification_text.grid(row=0,column=0,sticky=tk.N+tk.S+tk.W+tk.E)
    def BrowseClick(self):
        filepaths = filedialog.askopenfilenames()
        for filepath in filepaths:
            self.listbox.insert(tk.END,filepath)
    def RemoveClick(self):
        indices = self.listbox.curselection()
        if len(indices) == 0:
            self.status.set("Select at least one spectrum to remove!")
        else:
            self.status.set("")            
        for index in reversed(indices):
            self.listbox.delete(index)
    def PlotClick(self):
        spectra = self.GetSelectedSpectra()
        if len(spectra) > 0:
            IR_fitter.PlotAbsorbances(spectra)
            self.status.set("Plotted {} spectra".format(len(spectra)))
    def ExportCsvClick(self):
        spectra = self.GetSelectedSpectra()
        if len(spectra) > 0:
            directory = filedialog.askdirectory(title="Select folder to which files get exported")
            for spectrum in spectra:
                with open(os.path.join(directory,spectrum.name+".csv"),'w') as f:
                    f.write("wavenumber / cm^-1 , absorbance" + os.linesep)
                    for k,A in zip(spectrum.wavenumber_cut,spectrum.absorbance_cut):
                        f.write("{:e},{:e}{}".format(k,A,os.linesep))
            self.status.set("Exported {} spectra as .csv".format(len(spectra)))
    def QuantifyPlotClick(self):
        results, composite_spectrum, standard_spectra,k_min,k_max = self.GetQuantification()
        if results == None:
            return
        self.note.select(2)
        IR_fitter.PlotSuperposition(results,composite_spectrum, standard_spectra,
                          k_min=k_min,
                          k_max=k_max,
                          interactive_plot=True)
    def QuantifyExportClick(self):
        results, composite_spectrum, standard_spectra,k_min,k_max = self.GetQuantification()
        if results == None:
            return 0
        IR_fitter.PlotSuperposition(results,composite_spectrum, standard_spectra,
                          k_min=k_min,
                          k_max=k_max,
                          interactive_plot=True)
        filepath = filedialog.asksaveasfilename()
        if filepath == None:
            self.status.set('Export aborted.')
        else:
            with open(filepath,'w') as f:
                f.write("wavenumber / cm^-1 , absorbance_{}, {}".format(composite_spectrum.name,','.join(['absorbance_{}*{:.0f}nm/{:.0f}nm'.format(s.name,results['d_vec'][m],s.thickness) for m,s in enumerate(standard_spectra)])  + os.linesep))
                for k in range(len(composite_spectrum.wavenumber_cut)):
                    values = [composite_spectrum.wavenumber_cut[k],composite_spectrum.absorbance_cut[k],*[s.absorbance_cut[k]*results['d_vec'][m] for m,s in enumerate(standard_spectra)]]
                    f.write(','.join(['{:e}'.format(v) for v in values]) + os.linesep)
            self.status.set(filepath + ' exported.')
    def GetSelectedSpectra(self):
        indices = self.listbox.curselection()
        spectra = []
        for index in indices:
            filepath = str(self.listbox.get(index))
            name = os.path.splitext(os.path.split(filepath)[1])[0]
            self.status.set("Estimate baseline of {} ...".format(name))
            self.statusline.update()
            spectra.append(self.GetSpectrumWithCurrentSettings(name,filepath))
        if len(indices) == 0:
            self.status.set("No spectrum chosen")  
        return spectra
    def GetQuantification(self):
        error_return_value = [None]*5
        index = self.listbox.curselection()
        if len(index) != 1:
            self.status.set("Error: Select exactly one composite spectrum to quantify!")
            return error_return_value
        else:
            k_min = float(eval(self.quantification_kmin.get()))
            k_max = float(eval(self.quantification_kmax.get()))
            standard_spectra = []
            filepaths = list(self.listbox.get(0,tk.END))
            if len(filepaths) < 2:
                self.status.set("Error: There are no standard spectra")
                return error_return_value
            else:
                self.status.set("")
            composition_filepath = filepaths.pop(index[0])
            for filepath in filepaths:
                name = os.path.splitext(os.path.split(filepath)[1])[0]
                self.status.set("Estimating baseline of {} ...".format(name))
                self.statusline.update()
                chunks = name.split('_')
                if len(chunks) < 2 or chunks[-1] != "nm":
                    self.status.set("Error: Name of standard has to have _thickness_nm at the end, where thickness is a number")
                    return error_return_value
                thickness = float(chunks[-2])
                spectrum = self.GetSpectrumWithCurrentSettings(name,filepath,thickness=thickness,normalize_by_thickness=True)
                standard_spectra.append(spectrum)
            composition_name = os.path.split(composition_filepath)[1]
            self.status.set("Estimating baseline of {} ...".format(composition_name))
            self.statusline.update()
            composite_spectrum = self.GetSpectrumWithCurrentSettings(composition_name,composition_filepath)
            results = IR_fitter.CalculateSuperposition(composite_spectrum, standard_spectra,k_min=k_min, k_max=k_max)
            d_vec,d_error_vec,F_vec,F_error_vec = results["d_vec"],results["d_error_vec"],results["F_vec"],results["F_error_vec"]
            txt_list = ['Quantification of sample {}:'.format(composite_spectrum.name)]
            for k,s in enumerate(standard_spectra):
                txt_list.append('d_{} = {}'.format(s.name,IR_fitter.GetErrorString(d_vec[k],d_error_vec[k])))
                txt_list.append('F_{} = {}'.format(s.name,IR_fitter.GetErrorString(F_vec[k],F_error_vec[k])))
            txt_list.append('d = {}'.format(IR_fitter.GetErrorString(np.sum(d_vec),np.sum(d_error_vec)))) 
            self.quantification_text.insert(tk.END,os.linesep.join(txt_list+[os.linesep]*2))
            self.status.set("Done")
            self.statusline.update()
            return results, composite_spectrum, standard_spectra,k_min,k_max
    def GetSpectrumWithCurrentSettings(self,name,filepath,thickness=None,normalize_by_thickness=False):
        spectrum = IR_fitter.absorbance_spectrum(name=name,
                   datafile_path=filepath,
                   thickness=thickness,
                   normalize_by_thickness=normalize_by_thickness,
                   k_min = float(eval(self.baseline_kmin.get())),
                   k_max = float(eval(self.baseline_kmax.get())),
                   r = float(eval(self.r.get())),
                   p = float(eval(self.p.get())))
        return spectrum
        
root = tk.Tk()
app = Application(root)
root.mainloop()
