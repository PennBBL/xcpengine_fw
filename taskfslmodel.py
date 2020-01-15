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
        '-f', '--taskfiledir', action='store', required=True,
        help='event file')
    parser.add_argument(
        '-t', '--template', action='store', required=True,
        help='  FSL design template')

    return parser
opts            =   get_parser().parse_args()


filedir=opts.taskfiledir
taskfile=filedir +'/task.json'
with open(taskfile, 'r') as contrastfile:
     data_contrast=contrastfile.read()
objcon=json.loads(data_contrast)

eventname=objcon['eventname']
contrast=objcon['contrast']

if contrast:
    tasklist=list(contrast.keys())
    weight=list(contrast.values())
    template1=opts.template
    filex = open(template1,"a") #append mode
    tevenr="set "+"fmri(evs_real)" + " " + str(len(eventname)) + "\n"
    teveno="set "+"fmri(evs_orig)" + " " + str(len(eventname)) + "\n"
    evvox="set "+"fmri(evs_vox)" + " " + str(0) + "\n"
    nco="set "+"fmri(ncon_orig)" + " " + str(len(tasklist)) + "\n"
    ncr="set "+"fmri(ncon_real)" + " " + str(len(tasklist)) + "\n"
    filex.write(tevenr)
    filex.write(teveno)
    filex.write(evvox)
    filex.write(nco)
    filex.write(ncr)
    for i in np.arange(0,len(eventname)):
        c=i+1
        eventfile=filedir+'/'+eventname[i]+'.txt'
        eventt="set "+"fmri(evtitle"+str(c)+")" + " " + '"' + eventname[i] + '"' + "\n"
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
        for k in np.arange(0,len(eventname)):
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
    filex.close()
