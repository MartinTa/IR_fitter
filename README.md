# IR_fitter
Python script (IR_fitter.py) as well as graphical user interface (GUI_IR_fitter.py) to read IR absorbance spectra. It allows to baseline correct and plot the spectra as well as to quantify them using direct calibration with spectra of pure components. It was tested using Python 3.5. It requires scipy, matplotlib and jcamp.
To install them, it is convenient to use Miniconda: https://conda.io/miniconda.html, which includes conda (located in the installation folder under Scripts) to install scipy by simply issuing as Administrator in command line:  
conda install scipy  
conda install matplotlib  
Further, jcamp should be installed by pip (which is also in the folder Scripts) using the following command:  
pip install jcamp==1.1