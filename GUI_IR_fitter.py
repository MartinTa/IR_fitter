# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 08:57:41 2017

@author: MartinT
"""

# import the library
from appJar import gui
import IR_fitter, os
import numpy as np

app = gui()
app.setGeometry(600,500)

def press(btn):
    if btn == "remove":
        items = app.getListItems("components")
        for item in items:
            app.removeListItem("components", item)
    elif btn == "brows/add":
        file = app.openBox(title=None, dirName=None, fileTypes=None, asFile=False)
        app.addListItem("components",file)
    elif btn == "plot absorbance":
        filepaths = app.getListItems("components")
        for filepath in filepaths:
            name = os.path.split(filepath)[1]
            spectrum = GetSpectrumWithCurrentSettings(name,filepath)
            IR_fitter.PlotAbsorbances(spectrum)
    elif btn == "browse":
        file = app.openBox(title=None, dirName=None, fileTypes=None, asFile=False)
        app.setEntry("e1",file) 
    elif btn == "plot copolymer absorbance":
        filepath = app.getEntry("e1")
        name = os.path.split(filepath)[1]
        spectrum = GetSpectrumWithCurrentSettings(name,filepath)
    elif btn == "quantify":
        k_min = float(eval(app.getEntry(k_min_name_quantification)))
        k_max = float(eval(app.getEntry(k_max_name_quantification)))
        component_spectra = []
        filepaths = app.getAllListItems("components")
        for filepath in filepaths:
            name = os.path.split(filepath)[1]
            chunks = name.split('_')
            if len(chunks) < 2 or chunks[-1] != "nm.DX":
                print("Error: name of component has to have _thickness_nm.DX at the end, where thickness is a number")
                return 1
            thickness = float(chunks[-2])
            spectrum = GetSpectrumWithCurrentSettings(name,filepath,thickness=thickness,normalize_by_thickness=True,)
            component_spectra.append(spectrum)
        filepath = app.getEntry("e1")
        name = os.path.split(filepath)[1]
        composite_spectrum = GetSpectrumWithCurrentSettings(name,filepath)
        parameters = IR_fitter.CalculateSuperposition(composite_spectrum, component_spectra,k_min=k_min, k_max=k_max)
        IR_fitter.PlotSuperposition(parameters,composite_spectrum, component_spectra,
                          k_min=k_min,
                          k_max=k_max,
                          interactive_plot=True,
                          output_folder=os.getcwd())
                          
def GetSpectrumWithCurrentSettings(name,filepath,thickness=None,normalize_by_thickness=False):
    spectrum = IR_fitter.absorbance_spectrum(name=name,
               datafile_path=filepath,
               thickness=thickness,
               normalize_by_thickness=normalize_by_thickness,
               k_min = float(eval(app.getEntry(k_min_name_baseline))),
               k_max = float(eval(app.getEntry(k_max_name_baseline))),
               r = float(eval(app.getEntry(r_name))),
               p = float(eval(app.getEntry(p_name))))
    return spectrum
             
             
app.startTabbedFrame("tabbedFrame")
app.startTab("main")

app.setFont(15)
app.startLabelFrame("components list")
app.setSticky("news")
app.setExpand("both")
app.setStretch("both")
app.addListBox("components", [])
app.setListBoxMulti("components", multi=True)
app.addButtons(["brows/add","remove","plot absorbance"], press)
#app.setButtonBg("brows/add", "grey")
#app.setButtonBg("remove", "grey")
#app.setButtonBg("plot absorbance", "grey")
app.stopLabelFrame()

app.startLabelFrame("composit spectrum")
app.setSticky("news")
app.setExpand("both")
app.setStretch("both")
app.addEntry("e1",colspan=3)
row = app.getRow() # get current row
app.setSticky("")
app.setExpand("both")
app.setStretch("both")
app.addButton("browse", press,row,0)
#app.setButtonBg("browse", "grey")
app.addNamedButton("plot absorbance","plot copolymer absorbance",press,row,1)
#app.setButtonBg("plot copolymer absorbance", "grey")
app.addButton("quantify",press,row,2)
#app.setButtonBg("quantify", "grey")
app.stopLabelFrame()

app.stopTab()
app.startTab("Settings")

app.setSticky("nw")
app.setExpand("both")
app.setStretch("column")
app.startLabelFrame("baseline settings")

row = app.getRow() # get current row
k_min_name_baseline = "k_min (1/cm) = "
app.addLabelEntry(k_min_name_baseline,row,0)
app.setEntry(k_min_name_baseline, "800")
k_max_name_baseline = "k_max (1/cm) = "
app.addLabelEntry(k_max_name_baseline,row+1,0)
app.setEntry(k_max_name_baseline, "np.inf")
r_name = "r = "
app.addLabelEntry(r_name,row,1)
app.setEntry(r_name, "1E8")
p_name = "p = "
app.addLabelEntry(p_name,row+1,1)
app.setEntry(p_name, "0.005")
app.stopLabelFrame()

app.startLabelFrame("quantification settings")
row = app.getRow() # get current row
k_min_name_quantification = "k_min (1/cm) =  "
app.addLabelEntry(k_min_name_quantification,row,0)
app.setEntry(k_min_name_quantification, "1000")
k_max_name_quantification = "k_max (1/cm) =  "
app.addLabelEntry(k_max_name_quantification,row+1,0)
app.setEntry(k_max_name_quantification, "2000")
app.stopLabelFrame()

#app.stopTab()
#app.startTab("output")
#app.setSticky("nw")
#app.setExpand("both")
#app.setStretch("column")
#app.addMessage("mess","initial message")
#
##.setMessage(title, text)
#
app.stopTab()
app.stopTabbedFrame()
app.go()


#