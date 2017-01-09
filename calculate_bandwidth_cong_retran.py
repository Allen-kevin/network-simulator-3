#!/usr/bin/env python

##########################################################################################
# This scripts use to deal data that producted through different combination of          #
# congestion control and retransmission algorithm.                                       #
# Distenation is to calculate the mean throughput and utilization of bandwidth           #
##########################################################################################
import os
import numpy as np

#global variance
bandwidth = 100
#Each experiment was repeated 4 times.
length = 4

def filter_data ():
	#Reading source file which had record all information that producted through TCP sender
	readfile = open ('delay_loss.txt', 'r')
	writefile = open ('filter_delay_loss.txt', 'w')

	lines = readfile.readlines ()

	#filtering unuseless line and writing those information that we need into the file call
	#filter_delay_loss.txt 
	for i in range (len (lines)):
		if 'Mbits/sec' in lines[i]:
			writefile.write (lines[i])

	#close readfile and writefle
	readfile.close ()
	writefile.close ()

#jugement one line was reproducted by which congestion control, begain 32 line belong to cubic, 
#next 32 line belong to veno, again next 32 line belong to vegas, and last 32 line belong to westwood.
def tag_congestion (i, step):
	if 0 <= i < step:
		cong = 'cubic'
	elif step <= i < step*2:
		cong = 'veno'
	elif step*2 <= i < step*4:
		cong = 'vegas'
	else:
		cong = 'westwood'
	return cong

#jugement one line belong to which retransmission algorithm. there are two retransmission algorithm,
#their be executed in turn after each one be executed sixteen times.
def tag_retransmission (i, step):
	global length
	for k in range (0, step, 2):
		if length*4*k <= i < length*4*(k + 1):
			retran = 'SARR-PRO'
			break
		if length*4*(k + 1) <= i < length*4*(k + 2):
			retran = 'PQRC-PRO'
			break
	return retran

#jugement one line belong to which awnd_threshold.
def tag_awnd_ex (i, step):
	global length
	for awnd in range (0, step, 4):
		if length*awnd <= i < length*(awnd + 1): 
			awnd_thresh = '1/2'
			break
		if length*(awnd + 1) <= i < length*(awnd + 2):
			awnd_thresh = '3/4'
			break
		if length*(awnd + 2) <= i < length*(awnd + 3):
			awnd_thresh = '7/8'
			break
		if length8(awnd + 3) <= i < length+(awnd + 4):
			awnd_thresh = '15/16'
			break
	return awnd_thresh

def insert_tag ():
	readfile = open ('filter_delay_loss.txt', 'r')
	writefile = open ('end_delay_loss.txt', 'w')
	#import global variance.
	global length
	global bandwidth

	lines = readfile.readlines ()
	count = 0
	sum = 0
	for i in renge (len (lines)):

		cong_step = 8*length
		re_step = len (lines)/(4*length)
		cong_thresh_step = len (lines)/length

		cong = tag_congestion (i, cong_step)
		retran = tag_retransmission (i, re_step)
		awnd_thresh = tag_awnd_ex (i, cong_thresh_step)
		
		#Each experiment was repeated 5 times, and we need to calculate the mean throughput.
		odom = lines[i].split ()
		count += 1
		sum += float (odom[6])
		if count == length:
			count = 0
			mean_thput = sum*1.0/length
			#cong representative congestion control, retran representative retransmission algorithm.
			#mean_thput is mean mean throughput.
			str_write = 'cong %s retran %s cong_thresh %s BW %.3f utilization %.3f\n'%(cong, retran, awnd_thresh, mean_thput, mean_thput/bandwidth)
			writefile.write (str_write)
			sum = 0
	#close readfile and writefile	
	readfile.close ()
	writefile.close ()

filter_data ()
insert_tag ()
