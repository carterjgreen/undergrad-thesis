# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:57:31 2020

@author: Carter
"""

import numpy as np
import scipy.signal as sg

D0 = 3.4e-3 # Gathered experimentally
lam = 3e8/(24.1e9)


def sar(Data, k, window=True):
    if window:
        Win = np.hanning(Data.shape[0])
        ScaWin = Win.sum()
        Win = np.tile(Win, (Data.shape[1], 1)).T
        Data = Data * Win / ScaWin
        
    output = np.zeros((Data.shape[0], Data.shape[1] - k), dtype="float64")
    for i in range(0, Data.shape[1] - k):
        output[:, i] = Data[:, i : i + k].sum(axis=1)

    return np.fft.rfft(output, axis=0)


def sar2(Data, k, window=True):
    if window:
        Win = np.hanning(Data.shape[0])
        ScaWin = Win.sum()
        Win = np.tile(Win, (Data.shape[1], 1)).T
        Data = Data * Win / ScaWin
        
    h = np.ones((1, k))
    output = sg.convolve(h, Data, mode='valid')
    
    return np.fft.rfft(output, axis=0)


def focused_sar(Data, k, kf, window =True):
    b = k //2
    d = np.abs(np.arange(-b, b + 1, dtype=int)*D0)
    Range = np.fft.rfftfreq(Data.shape[0], 1e-6)*3e8/(2*kf)
    X, Y = np.meshgrid(d, Range)
    xi = np.divide(2*np.pi*X**2, (lam*Y), out=np.zeros_like(X), where=Y!=0) 
    phase_corr = np.exp(1j*xi)
    
    if window:
        Win = np.hanning(Data.shape[0])
        ScaWin = Win.sum()
        Win = np.tile(Win, (Data.shape[1], 1)).T
        Data = Data * Win / ScaWin 
        
    data_freq = np.fft.rfft(Data, axis=0)
    
    output = np.zeros((data_freq.shape[0], data_freq.shape[1] - k), dtype="complex128")
    for i in range(0, data_freq.shape[1] - k):
        output[:, i] = (data_freq[:, i : i + k] * phase_corr).sum(axis=1)
        
    return output

    