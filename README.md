# IR_fitter
Python script to read IR absorbance spectra. It allows to baseline correct and plot the spectra as well as to quantify them using direct calibration with spectra of pure components. It was tested using Python 3.5. It requires scipy and jcamp.
To install them under Windows, it is convenient to use Miniconda: https://conda.io/miniconda.html, which includes conda (located in the installation folder under Scripts) to install scipy by simply issuing as Administrator: 
conda install scipy
Further, jcamp should be installed by pip (which is also in the folder Scripts) using the following command which installs the latest version (Python3 compatible):
pip install https://github.com/nzhagen/jcamp/tarball/master
