# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 10:42:19 2016

@author: Martin Tazreiter, Martin.Tazreiter@gmx.at
"""

import pylab as plt
import os
import numpy as np
from scipy import optimize, sparse
import matplotlib as mpl
from distutils.version import LooseVersion
import jcamp

# An absorbance spectrum measured in transmission can be read from file by initializing an absorbance_spectrum instance.
# It also calculates a baseline. The spectrum as well as the baseline can thereafter be plotted by the function PlotAbsorbances.
# Quantitative analysis procedure:
# 1. Initialization of 'pure' sample spectra providing their thickness and normalize_by_thickness=True
# 2. Initialization of 'composite' sample spectrum 
# 3. Using function CalculateSuperposition to get parameters, they also get printed to standard output
# 4. Using function PlotSuperposition to plot the fitted spectrum with all its components

# Simple example is given at the end of this script which may be tested by simply running this script.
# It saves the spectrum plot with fit in the working directory

class absorbance_spectrum():     
    def __init__(self,name,datafile_path,thickness=None,normalize_by_thickness=False,k_min=-np.inf,k_max=np.inf,r=1E8,p=0.005):
        self.name = name
        self.datafile_path = datafile_path
        self.thickness = thickness # nm
        self.normalize_by_thickness = normalize_by_thickness
        self.k_min,self.k_max = k_min, k_max
        self.r, self.p = r, p
        self.wavenumber, self.absorbance = self.ReadJcampFile()
        if self.normalize_by_thickness:
            self.absorbance /= self.thickness
        self.transmittance = 10**(-self.absorbance)
        #data in wavenumber range for baseline:
        logical = np.logical_and(self.wavenumber>self.k_min,self.wavenumber<self.k_max)
        self.wavenumber_cut = self.wavenumber[logical]
        self.absorbance_cut = self.absorbance[logical]
        self.baseline = self.GetBaselineAls()
        #and for the wavenumber range for fitting, set by GetCoefficients:
        self.wavenumber_cut_fit = None
        self.absorbance_corr_cut_fit = None
        self.baseline_cut_fit = None
    def ReadDataPointTable(self):
        with open(self.datafile_path) as f:
            lines = f.read().splitlines()
        wavenumber = np.zeros(len(lines))
        absorbance = np.zeros(len(lines))
        for n,line in enumerate(lines):
            wavenumber[n],absorbance[n] = line.split()[0:2]   
        return wavenumber, absorbance 
    def ReadJcampFile(self):
        jcamp_dict = jcamp.JCAMP_reader(self.datafile_path)
        if jcamp_dict['x'][1]<jcamp_dict['x'][0]: # wavenumber will be used ascending during script execution
            wavenumber,absorbance = np.flipud(jcamp_dict['x']), np.flipud(jcamp_dict['y'])
        else:
            wavenumber,absorbance = jcamp_dict['x'], jcamp_dict['y']
        return wavenumber, absorbance 
    def GetBaselineAls(self,i_max=100):
        A = self.absorbance_cut
        L = len(A)
        D = sparse.csc_matrix(np.diff(np.eye(L), 2))
        w = np.ones(L)
        w_new = np.ones(L)
        for i in range(i_max):
            W = sparse.spdiags(w, 0, L, L)
            Z = W + self.r * D.dot(D.transpose())
            z = sparse.linalg.spsolve(Z, w*A)
            w_new = self.p * (A > z) + (1-self.p) * (A < z)
            if np.all(w_new == w):
                print('Baseline calculation converged after {} iterations'.format(i))
                return z
            w = w_new
        print('Warning: Baseline calculation not converged after {} iterations! (bad parameters?)'.format(i_max))
        return z
    
def GetErrorString(value,error):
    #Returns string giving value +/- error both with a precision determined by the first two significant digits of the error value
    error_to_two_digit = round(error, 1-int(np.floor(np.log10(abs(error)))))
    ndigits = 1-int(np.floor(np.log10(error_to_two_digit)))
    value_rounded = round(value,ndigits)
    error_rounded = round(error,ndigits)
    value_str = ('{:.' + str(max(ndigits,0)) + 'f}').format(value_rounded)
    error_str = ('{:.' + str(max(ndigits,0)) + 'f}').format(error_rounded)
    string = value_str + ' +/- ' + error_str
    return string
    
def GetFontsAndSetMPLproperties():
    font = {'size' : 11}
    axis_font = font
    legend_font = {'size' : 9}
    dpi = 600
    mpl.rcParams['savefig.dpi'] = dpi
    mpl.rc('font', **font)
    mpl.rcParams.update({'figure.autolayout': True})
    major_size, major_width, minor_size, minor_width  = 5,1.5,3,1
    mpl.rcParams['xtick.major.size'] = major_size
    mpl.rcParams['xtick.major.width'] = major_width
    mpl.rcParams['xtick.minor.size'] = minor_size
    mpl.rcParams['xtick.minor.width'] = minor_width
    mpl.rcParams['ytick.major.size'] = major_size
    mpl.rcParams['ytick.major.width'] = major_width
    mpl.rcParams['ytick.minor.size'] = minor_size
    mpl.rcParams['ytick.minor.width'] = minor_width
    mpl.rcParams['axes.linewidth'] = 1
    if LooseVersion(mpl.__version__) >= LooseVersion('2.0.0'): # can only be set using this version or above
        mpl.rcParams['hatch.linewidth'] = 1.0  # previous ps and Agg hatch linewidth
    return  axis_font, legend_font
        
def PlotAbsorbances(samples,plot_baseline=True,plot_original=True,plot_bscorrected=False):
    if not isinstance(samples,list):
        samples = [samples]
    axis_font, legend_font = GetFontsAndSetMPLproperties()
    for s in samples:
        fig = plt.figure(figsize=(12/2.54,8/2.54))
        ax0 = fig.add_subplot(111)
        ax0.invert_xaxis()
        plt.locator_params(nbins=6)
        if plot_original:
            ax0.plot(s.wavenumber,s.absorbance*1E4,label='data',color='k')  
        if plot_baseline:
            ax0.plot(s.wavenumber_cut,s.baseline*1E4,label='baseline',color='r') 
        if plot_bscorrected:
            ax0.plot(s.wavenumber_cut,(s.absorbance_cut-s.baseline)*1E4,label=s.name+'_corrected') 
        legend = plt.legend()    
        legend.draggable(True)
        plt.title(s.name)
        ax0.set_xlabel('wavenumber / cm$^{-1}$')
        ax0.set_ylabel('absorbance / 10$^{-4}$nm$^{-1}$')
        plt.show()#block=False) block=False, not working yet under linux
    
def GetCoefficients(composite_sample, pure_samples,k_min=-np.inf,k_max=np.inf):
    logical = np.logical_and(composite_sample.wavenumber_cut>k_min,composite_sample.wavenumber_cut<k_max)
    composite_sample.wavenumber_cut_fit = composite_sample.wavenumber_cut[logical]
    composite_sample.absorbance_corr_cut_fit = (composite_sample.absorbance_cut-composite_sample.baseline)[logical]
    for ps in pure_samples:
        ps.wavenumber_cut_fit = composite_sample.wavenumber_cut_fit
        ps.absorbance_corr_cut_fit = np.interp(ps.wavenumber_cut_fit,ps.wavenumber_cut,(ps.absorbance_cut-ps.baseline))
    basis_functions = np.vstack([s.absorbance_corr_cut_fit for s in pure_samples]).transpose()
    x,rnorm = optimize.nnls(basis_functions,composite_sample.absorbance_corr_cut_fit)
    S = np.sum((np.dot(basis_functions,x)-composite_sample.absorbance_corr_cut_fit)**2)
    n,m = basis_functions.shape
    x_var = np.abs(S/(n-m)*np.diag(np.linalg.inv(np.dot(basis_functions.transpose(),basis_functions))))
    return x, np.sqrt(x_var)  
      
def CalculateSuperposition(composite_sample, pure_samples,thickness_error_absolute=1,thickness_error_relative=0.01,k_min = 1000, k_max = 2000): 
    d_vec, sig_vec = GetCoefficients(composite_sample, pure_samples,k_min,k_max)
    d_error_vec = sig_vec + thickness_error_absolute + d_vec*thickness_error_relative
    F_vec = d_vec/np.sum(d_vec)
    F_error_vec = np.nan_to_num(d_error_vec/np.sum(d_vec)+d_vec*np.sum(d_error_vec)/np.sum(d_vec)**2)#F_vec*(d_error_vec/d_vec+np.sum(d_error_vec)/np.sum(d_vec)))
    F_error_vec = np.maximum(F_error_vec,np.ones_like(F_error_vec)*0.01)
    print('Superposition of sample {} calculated:'.format(composite_sample.name))
    for k,s in enumerate(pure_samples):
        print('d_{} = {}'.format(s.name,GetErrorString(d_vec[k],d_error_vec[k])))
        print('F_{} = {}'.format(s.name,GetErrorString(F_vec[k],F_error_vec[k])))
    print('d = {}'.format(GetErrorString(np.sum(d_vec),np.sum(d_error_vec))))    
    parameters = F_vec, F_error_vec, d_vec, d_error_vec
    return parameters 
    
def PlotSuperposition(parameters,composite_sample, pure_samples,k_min=None,k_max=None,interactive_plot=False,output_folder=None):
    F_vec, F_error_vec, d_vec, d_error_vec = parameters
    if not interactive_plot:
        plt.ioff()
        plt.close()
    axis_font, legend_font = GetFontsAndSetMPLproperties()
    fig = plt.figure(figsize=(12/2.54,8/2.54))
    ax0 = fig.add_subplot(111)
    plt.locator_params(nbins=6)
    ax0.plot(composite_sample.wavenumber,composite_sample.absorbance,linewidth = 2,label='data',color='r')
    fill_colors=['b','g','m','r','c','m','k']
    hatches=['/'*3,'\\'*3,'-'*3,'*'*3,'o'*3,'O'*3,'.'*3]
    composite_sample_baseline_cut_fit = composite_sample.baseline[np.logical_and(composite_sample.wavenumber_cut>k_min,composite_sample.wavenumber_cut<k_max)]
    for k,s in enumerate(pure_samples):
        ax0.fill_between(s.wavenumber_cut_fit,composite_sample_baseline_cut_fit,d_vec[k]*s.absorbance_corr_cut_fit+composite_sample_baseline_cut_fit,label='fit {}'.format(s.name),alpha=0.5,linewidth=0,color=fill_colors[k],hatch=hatches[k])
    absorbance_fit = np.dot(d_vec,np.vstack([s.absorbance_corr_cut_fit for s in pure_samples]))+composite_sample_baseline_cut_fit
    ax0.plot(composite_sample.wavenumber_cut_fit,absorbance_fit,'k--',dashes=(3,3),label = 'fit',linewidth = 2)
    ax0.plot(composite_sample.wavenumber_cut,composite_sample.baseline,linewidth=1.5,color='k',label='baseline')    
    ax0.set_xlabel('wavenumber / cm$^{-1}$')
    ax0.set_ylabel('absorbance')
    min_,max_ = np.min(absorbance_fit), np.max(absorbance_fit)
    ax0.set_ylim([min_-(max_-min_)/10,max_+(max_-min_)/10])
    if k_min != None:
        ax0.set_xlim([k_min,ax0.get_xlim()[1]])
    if k_max != None:
        ax0.set_xlim([ax0.get_xlim()[0],k_max])
    legend = ax0.legend(loc='best',prop=legend_font,handlelength=3)
    legend.draggable(True)
    ax0.invert_xaxis()
    if output_folder != None:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        plt.savefig(os.path.join(output_folder,'FTIR_' + composite_sample.name + '.png'))  
    if interactive_plot:
        plt.show()

if __name__ == '__main__':
    EGDMA = absorbance_spectrum(name='EGDMA',
                   datafile_path=os.path.join('test_spectra','EGDMA_292_nm.DX'),
                   thickness=292,
                   normalize_by_thickness=True,
                   k_min = 800)
    MAA = absorbance_spectrum(name='MAA',
                 datafile_path=os.path.join('test_spectra','MAA_2020_nm.DX'),
                 thickness=2020,
                 normalize_by_thickness=True,
                 k_min = 800)
                  
    composite_spectrum = absorbance_spectrum(name='copolymer',
                   datafile_path=os.path.join('test_spectra','copolymer.DX'))

    PlotAbsorbances([EGDMA,MAA],plot_baseline=True,plot_original=True,plot_bscorrected=False)
    k_min = 1000
    k_max = 2000
    pure_sample_spectra = [MAA,EGDMA]
    parameters = CalculateSuperposition(composite_spectrum, pure_sample_spectra,k_min=k_min, k_max=k_max)
    PlotSuperposition(parameters,composite_spectrum, pure_sample_spectra,
                      k_min=k_min,
                      k_max=k_max,
                      interactive_plot=True,
                      output_folder=os.getcwd())
                      
