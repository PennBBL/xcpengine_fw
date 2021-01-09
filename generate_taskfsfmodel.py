#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:


#AZEEZ ADEBIMPE PENN BBL

from argparse import (ArgumentParser, RawTextHelpFormatter)
import json
import numpy as np
import pandas as pd
from scipy.stats import gamma

def get_parser():
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description=' generate design.fsf and hrfconvolved  matrix')   
    parser.add_argument(
        '-o', '--out', action='store', required=True,
        help='outdir')
    parser.add_argument(
        '-r', '--tr', action='store', required=True,
        help='repetition time')
    parser.add_argument(
        '-c', '--customreg', action='store', required=False,
        help='custom regressors')
    parser.add_argument(
        '-t', '--taskconv', action='store', required=False,
        help='  FSL design template')

    return parser
opts            =   get_parser().parse_args()

# read the task contrast

t_rep=np.asarray(opts.tr, dtype='float64')
taskconx=[]
#read conlvolved task
if opts.taskconv:
    taskconv=pd.read_csv(opts.taskconv,sep='\t',skiprows=5,header=None).to_numpy()
    taskconx = np.delete(taskconv, [-1], axis=1)

# define hrf
def hrf(times):
    """ Return values for HRF at given times """
     # Gamma pdf for the peak
    peak_values = gamma.pdf(times, 6)
     # Gamma pdf for the undershoot
    undershoot_values = gamma.pdf(times, 12)
     # Combine them
    values = peak_values - 0.35 * undershoot_values
     # Scale max to 0.6
    return values / np.max(values) * 0.6


if opts.customreg:
    customreg=pd.read_csv(opts.customreg,sep=' ',header=None).to_numpy()
    hrf_times = np.arange(0, 35, t_rep)
    hrf_signal = hrf(hrf_times)
    N=len(hrf_signal)-1 #number to remove
    taskcon=np.zeros(customreg.shape)
    customreg=customreg.astype('float64')
    for i in np.arange(0,customreg.shape[1]):
        tt=np.convolve(customreg[:,i],hrf_signal)
        taskcon[:,i]=tt[:-N]
if taskcon.any() and len(taskconx)>0:
    if taskconv.shape[0] != taskconv.shape[0]:
        nv = taskcon.shape[0]-taskconv.shape[0]-1
        taskx = taskcon[nv:-1:,]
    else:
        taskx = taskcon
    tasknuissance = np.concatenate((taskx,taskconx),axis=1)
else: 
    if taskcon.any() and not taskconx:
        tasknuissance=taskcon
    elif taskconx.any() and not taskcon: 
        tasknuissance=taskcon

#this can be used fo task regressed if possible
np.savetxt(opts.out+'taskhrfconvolved.txt', tasknuissance, delimiter=' ')
