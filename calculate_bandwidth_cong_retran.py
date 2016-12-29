#!/usr/bin/env python

##########################################################################################
# This scripts use to deal data that producted through different combination of          #
# congestion control and retransmission algorithm.                                       #
# Distenation is to calculate the mean throughput and utilization of bandwidth           #
##########################################################################################
import os
import numpy as np

def filter_data ():
	#Reading source file which had record all information that producted through TCP sender
	readfile = open ('OR_AS_delay_100ms_loss_0.01.txt', 'r')
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

def insert_tag ():
	readfile = open ('filter_delay_loss.txt', 'r')
	writefile = open ('end_or_as_delay_100ms_loss_0.01.txt', 'w')

	lines = readfile.readlines ()
	bandwidth = 100
	#Each experiment was repeated 5 times.
	length = 5
	count = 0
	sum = 0
	#jugement one line was reproducted by which congestion control, begain 20 line belong to cubic, 
	#next 20 line belong to veno, again next 20 line belong to vegas, and last 20 line belong to westwood.
	for i in range (len (lines)):
		if 0 <= i < length*4:
			cong = 'cubic'
		elif length*4 <= i < length*8:
			cong = 'veno'
		elif length*8 <= i < length*12:
			cong = 'vegas'
		else :
			cong = 'westwood'
		
		#jugement one line belong to which retransmission algorithm.
		for k in range (4):
			if length*4*k <= i < length*(4*k + 1):
				retran = 'RH'
			if length*(4*k + 1) <= i < length*(4*k + 2):
				retran = 'PRR'
			if length*(4*k + 2) <= i < length*(4*k + 3):
				retran = 'SARR'
			if length*(4*k + 3) <= i < length*(4*k + 4):
				retran = 'PQRC'
		#Each experiment was repeated 5 times, and we need to calculate the mean throughput.
		odom = lines[i].split ()
		count += 1
		sum += float (odom[6])
		if count == length:
			count = 0
			mean_thput = sum*1.0/length
			#cong representative congestion control, retran representative retransmission algorithm.
			#mean_thput is mean mean throughput.
			str_write = 'cong %s retran %s BW %.3f utilization %.3f\n'%(cong, retran, mean_thput, mean_thput/bandwidth)
			writefile.write (str_write)
			sum = 0
	#close readfile and writefile	
	readfile.close ()
	writefile.close ()

filter_data ()
insert_tag ()
