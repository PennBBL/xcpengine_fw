#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

from argparse import (ArgumentParser, RawTextHelpFormatter)
import json 
import numpy as np 
import pandas as pd
from scipy.stats import gamma

def get_parser():
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description=' write the report for xcpEngine ')
    parser.add_argument(
        '-e', '--eventfile', action='store', required=True,
        help='event file')
    parser.add_argument(
        '-o', '--out', action='store', required=True,
        help='outdir')
    parser.add_argument(
        '-r', '--tr', action='store', required=True,
        help='repetition time')
    parser.add_argument(
        '-c', '--contrast', action='store', required=False,
        help='contrasts list in json file')
    parser.add_argument(
        '-t', '--template', action='store', required=False,
        help=' upper part of FSL design template')
    
    return parser
opts            =   get_parser().parse_args()

# read the task contrast

t_rep=np.asarray(opts.tr, dtype='float64')
#read the event time 
events=pd.read_csv(opts.eventfile,sep='\t')
columnname=events.columns
eventtime=events.as_matrix()
timecolumn=t_rep*np.arange(1,eventtime.shape[0]+1,1)
trcolumn=t_rep+0*np.arange(1,eventtime.shape[0]+1,1)

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

hrf_times = np.arange(0, 35, t_rep)
hrf_signal = hrf(hrf_times)
N=len(hrf_signal)-1 #number to remove
#convole the stimulus timing with the task 
# may be used for taskregressed
taskcon=np.zeros(eventtime.shape)

for i in np.arange(0,eventtime.shape[1]):
     tt=np.convolve(eventtime[:,i],hrf_signal)
     taskcon[:,i]=tt[:-N]

#this can be used fo task regressed if possible
np.savetxt(opts.out+'taskhrfconvolved.txt', taskcon, delimiter=' ')

if opts.contrast:
    contrast=opts.contrast
    with open(contrast, 'r') as contrastfile: 
         data_contrast=contrastfile.read()
    objcont=json.loads(data_contrast)
    tasklist=list(objcont.keys())
    weight=list(objcont.values())
    template1=opts.template
    filex = open(template1,"a") #append mode 
    tevenr="set "+"fmri(evs_real)" + " " + str(eventtime.shape[1]) + "\n"
    teveno="set "+"fmri(evs_orig)" + " " + str(eventtime.shape[1]) + "\n"
    evvox="set "+"fmri(evs_vox)" + " " + str(0) + "\n"
    nco="set "+"fmri(ncon_orig)" + " " + str(len(tasklist)) + "\n"
    ncr="set "+"fmri(ncon_real)" + " " + str(len(tasklist)) + "\n"
    filex.write(tevenr)
    filex.write(teveno)
    filex.write(evvox)
    filex.write(nco)
    filex.write(ncr)
    for i in np.arange(0,eventtime.shape[1]):
        c=i+1
        dd=np.column_stack((timecolumn,trcolumn,eventtime[:,i]))
        eventfile=opts.out+'/event'+str(c)+'.txt'
        np.savetxt(eventfile,dd, delimiter=' ',fmt='%d')
        eventt="set "+"fmri(evtitle"+str(c)+")" + " " + '"' + columnname[i] + '"' + "\n"
        eventshape="set "+"fmri(shape"+str(c)+")" + " " + str(3) + "\n"
        eventtemp="set "+"fmri(tempfilt_yn"+str(c)+")" + " " + str(1) + "\n"
        eventcustom="set "+"fmri(custom"+str(c)+")" + " " + '"' + eventfile + '"' + "\n"
        eventconv="set "+"fmri(convolve"+str(c)+")" + " " + str(3) + "\n"
        orhtho="set "+"fmri(ortho"+str(c)+"."+str(0)+")" + " " + str(0) + "\n"
        conphase="set "+"fmri(convolve_phase"+str(c)+")" + " " + str(0) + "\n"
        derivey="set "+"fmri(deriv_yn"+str(c)+")" + " " + str(0) + "\n"
        filex.write(eventt) 
        filex.write(eventshape) 
        filex.write(eventtemp) 
        filex.write(eventcustom)
        filex.write(eventconv)
        filex.write(orhtho)
        filex.write(derivey)
        filex.write(conphase)
        for k in np.arange(0,eventtime.shape[1]):
            h=k+1
            orhtho1="set "+"fmri(ortho"+str(c)+"."+str(h)+")" + " " + str(0) + "\n"
            filex.write(orhtho1)
    for i in np.arange(0,len(tasklist)):
        c=i+1
        ctdisplay="set " +"fmri(conpic_real."+str(c)+")" + " " + str(1) + " \n"
        ctname="set " +"fmri(conname_real."+str(c)+")" + " " + '"' + tasklist[i]+ '"'+ "\n"
        ctpdisplay="set " +"fmri(conpic_orig."+str(c)+")" + " " + str(1) + "\n"
        conpic="set " +"fmri(conname_orig."+str(c)+")" + " " + '"' + tasklist[i]+ '"'+  "\n"
        filex.write(ctdisplay)
        filex.write(ctname)
        filex.write(ctpdisplay)
        filex.write(conpic)
        for j in np.arange(0,len(weight[1])):
            p=j+1
            ctreal="set " +"fmri(con_real"+str(c)+"."+str(p)+")"+ " " + str(weight[i][j])+"\n"
            ctorig="set " +"fmri(con_orig"+str(c)+"."+str(p)+")"+ " " + str(weight[i][j])+"\n"
            filex.write(ctreal)
            filex.write(ctorig)
        if sum(weight[i]) == 1:
            ftestr="set " +"fmri(ftest_real"+str(1)+"."+str(c)+")"+ " " + str(1) + "\n"
            ftesto="set " +"fmri(ftest_orig"+str(1)+"."+str(c)+")"+ " " + str(1) + "\n"
            filex.write(ftestr)
            filex.write(ftesto)
        else: 
            ftestr="set " +"fmri(ftest_real"+str(1)+"."+str(c)+")"+ " " + str(0) + "\n"
            ftesto="set " +"fmri(ftest_orig"+str(1)+"."+str(c)+")"+ " " + str(0) + "\n"
            filex.write(ftestr)
            filex.write(ftesto)
    filex.close()