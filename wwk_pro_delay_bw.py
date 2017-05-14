#!/usr/bin/python
# coding:utf-8

import os
import sys
import zipfile
import shutil 
#form collections import defaultdict

delayThsh = 100 #delay threshold
maxThput = 0  #save max throughput
top = '/root/ShappingProxyBackup20130411/pqsa_simulator/'
path = '/home/wanwenkai/pqsa_simulator/rate_window_class/'
#sourcepath = '/home/wanwenkai/pqsa_simulator/rate_window_class/'


#put files which has same window and period into a same dir
def same_period_and_window(f, winPath, period):
	periodWinPath = os.path.join(winPath, 'period_'+str(period))	
	if not os.path.isdir(periodWinPath):
		os.mkdir(periodWinPath)
	shutil.copy(f, periodWinPath)

def same_window(bandWdPath, f, win, period):
    winPath = os.path.join(bandWdPath, 'win_'+str(win))
    if not os.path.isdir(winPath):
        os.mkdir(winPath)
    same_period_and_window(f, winPath, period)

def fix_window_period(level, dir):
    bandWdPath = os.path.join(path, dir)
    if not os.path.isdir(bandWdPath):
        os.mkdir(bandWdPath)
   
    for f in os.listdir(level):
        if f.startswith('proUDP_') and f.endswith('.sum'):
            rate = int(f.split('-')[-3])
            win = int(f.split('-')[-2])
            p = f.split('-')[-1]
            p = int(p.split('.')[0])
            f = os.path.join(level, f)
            #files have same window
            same_window(bandWdPath, f, win, p)
            #same_window(bandWdPath, f, win, p)

if __name__ == '__main__':
	for dir in os.listdir(top):
		if dir.startswith('downlink'):
			level = os.path.join(top, dir)
			print level
			fix_window_period(level, dir)

    #find_rate(dirpath)
