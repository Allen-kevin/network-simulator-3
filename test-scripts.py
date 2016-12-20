#!/usr/bin/env python

import os
import matplotlib
matplotlib.use ('agg')
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
import fileinput

m_delay = 0.045
m_exp_time = 0.1

def generate_downlink (which_txt):
	downlink_mean_throughput = open ('./data-ns3/vegas/'+str (which_txt)+'_mean_throughput.txt','w')
	path = '/home/wanwenkai/same_bandwidth/'+str (which_txt)+'_mean_bw'
	files = os.listdir (path)
	files.sort ()
	Istrue = 1
	init_file = 0
	num_line = 0
	while (Istrue):
		readfile = open (path+'/'+files[init_file])
		writefile = open ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/downlink.txt','w')
		
		lines = readfile.readlines()
		sum_packet = 0
		start_time = 0.0

		time_len = len (lines) - 2

		if float (time_len) > 30100:
			Istrue = 0
			print ("%s"%(files[init_file]))
			for line in range (len(lines) - 2):
				odom = lines[line].split()
				numbers_float = map(float,odom)
				write_str = '%.3f%s\n'%(numbers_float[1]*8.0*10/(1024*1024),'Mbps')
				writefile.write(write_str)
				num_line += 1
			sum_odom = lines[-2].split ()
			write_str = 'downklink.txt mean throuthput %.3f\n'%(float (sum_odom[4])*8.0*10/(num_line*1024*1024))
			downlink_mean_throughput.write (write_str)
		else:
			init_file += 1
			writefile.close ()
			continue
				
		readfile.close ()
		writefile.close ()
		downlink_mean_throughput.close ()
			

def read_TCP_congestion_vegas (old_alpha, old_beta, alpha, beta):
	num = 0
	for line in fileinput.input ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/src/internet/model/tcp-vegas.cc',backup='bak',inplace=1):
		num = num + 1
		if num == 44: 
			line = line.replace (old_alpha, alpha)
		if num == 48:
			line = line.replace (old_beta, beta)
		if num == 61:
	   		line = line.replace (old_alpha, alpha)	
	 	if num == 62:
	 		line = line.replace (old_beta, beta)
		print line.rstrip()
	fileinput.close ()

def cal_mean_throughput (alpha, which_txt):
	readrx = open ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/TcpVariantsComparison-next-rx.data','r')
	write_mean_throughput = open ('./data-ns3/vegas/'+str (which_txt)+'_mean_throughput.txt','a')

	rxlines = readrx.readlines ()		
	rx_lastline = rxlines[-1]
	rx_last = rx_lastline.split ()
	last_float = map (float,rx_last)

	mean_throughput = last_float[1]*8.0/(last_float[0]*1024*1024)
	write_str = '%d %.3f\n'%(alpha,mean_throughput)
	write_mean_throughput.write (write_str)

	readrx.close ()
	write_mean_throughput.close ()

	return mean_throughput

def cal_Queue_Delay ():
	readtx = open ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/TcpVariantsComparison-next-tx.data','r')
	readrx = open ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/TcpVariantsComparison-next-rx.data','r')

	writefile = open ('downlink_time.txt','w')

	txlines = readtx.readlines ()
	rxlines = readrx.readlines ()
	n = 0
	for line in range (len (rxlines) - 3):
		rx_odom = rxlines[line].split ()
		rx_numbers_float = map (float, rx_odom)
		tx_odom = txlines[line + 1].split ()
		tx_numbers_float = map (float, tx_odom)
		#calculate the time that a datapacket from the sender to receive
		interval_time = rx_numbers_float[0] - tx_numbers_float[1]
		#write the interval_time in downlink_time.txt
		write_str = '%.3f %.3f\n'%(rx_numbers_float[0],interval_time)
		writefile.write (write_str)

	readtx.close ()
	readrx.close ()
	writefile.close ()

def pro_queuedelay_time (line, alpha):
	readtx = open ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/TcpVariantsComparison-next-tx.data','r')
	readrx = open ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/TcpVariantsComparison-next-rx.data','r')

	writefile = open ('./data-ns3/vegas/'+str (line)+'_pro_queuedelay_time.txt','a')

	txlines = readtx.readlines ()
	rxlines = readrx.readlines ()
	delay_num = 0

	rline = 0
	tline = 0
	rx_odom = rxlines[rline].split ()
	rx_numbers_float = map (float, rx_odom)
	tx_odom = txlines[tline].split ()
	tx_numbers_float = map (float, tx_odom)

	while (1):
		if rline != len (rxlines) - 3: 
			if rx_numbers_float[1] == tx_numbers_float[1]:
				#calculate the time a datapacket from the sender to receive
				interval_time = rx_numbers_float[0] - tx_numbers_float[0]
				if interval_time - m_delay < m_exp_time:
					delay_num += 1
				rline += 1
				tline += 1
				rx_odom = rxlines[rline].split ()
				rx_numbers_float = map (float, rx_odom)
				tx_odom = txlines[tline].split ()
				tx_numbers_float = map (float, tx_odom)
			else:
				tline += 1
				tx_odom = txlines[tline].split ()
				tx_numbers_float = map (float, tx_odom)
		else:
			break
		#write the interval_time in downlink_time.txt
	write_str = '%d %.3f\n'%(alpha, delay_num*1.0/len (rxlines))
	writefile.write (write_str)

	readtx.close ()
	writefile.close ()
	
	return delay_num*1.0/len (rxlines)

def figure_time (): 
	data = np.loadtxt ('downlink_time.txt')
	plt.figure ()
	plt.plot (data[:,0],data[:,1],'r-')
	plt.xlabel ('time/s')
	plt.ylabel ('downlink-time')
	plt.savefig ('queue_delay.pdf')
	plt.close ()

def pro_queuedelay_time_figure (line): 
	data = np.loadtxt ('./data-ns3/vegas/'+str (line)+'_pro_queuedelay_time.txt')
	plt.figure ()
	plt.plot (data[:,0],data[:,1],'or-',label="queue delay")
	plt.xlabel ('time/s')
	plt.ylabel ('proportion')
	plt.savefig ('./data-ns3/vegas/'+str (line)+'_pro_queue_delay.pdf',format='pdf')

	plt.close ()

def Diff_parameters_figure (line):
	data1 = np.loadtxt ('./data-ns3/vegas/'+str (line)+'_mean_throughput.txt')
	data2 = np.loadtxt ('./data-ns3/vegas/'+str (line)+'_pro_queuedelay_time.txt')

	fig = plt.figure ()
	ax1 = fig.add_subplot (111)
	ax1.plot (data1[:,0], data1[:,1], 'b-', linewidth=2, label="throughput")
	
	ax2 = ax1.twinx ()
	ax2.plot (data1[:,0], data2[:,1], 'r-', linewidth=2, label="delay")
	
	ax1.set_xlabel ('alpha')
	ax1.set_ylabel ('throughput/Mb')
	ax2.set_ylabel ('delay/ms')
	
	ax1.set_xlim (0, 40)
	ax1.set_ylim (0,5.0)
	ax2.set_ylim (0,1.0)

	ax1.legend (loc=(.02, .94), fontsize=8, shadow=True)
	ax2.legend (loc=(.02, .9), fontsize=8, shadow=True)
	plt.savefig ('./data-ns3/vegas/'+str (line)+'_Diff_parameters.pdf', format='pdf')

##########################################################################

m_target_pro = 0.65
m_default_interval = 2 

for line in range (0,4):

	m_alpha = 2
	m_beta = 4
	m_old_alpha = 2
	m_old_beta = 4
	last_thput = 0
	IsTrue = 1

	generate_downlink (line)
	while (IsTrue):
		print(" %d < level < %d, alpha = %d\n"%(line, line+1, m_alpha))
		read_TCP_congestion_vegas (str (m_old_alpha), str (m_old_beta), str (m_alpha), str (m_beta))
		os.system ('./waf --run scratch/tcp-variants-comparison --command-template="%s --tracing=1"')
		current_thput = cal_mean_throughput (m_alpha, line)
		current_pro = pro_queuedelay_time (line, m_alpha)
		print current_pro
		if current_pro > m_target_pro:
			last_thput = current_thput
			m_old_alpha = m_alpha
			m_old_beta = m_beta
			m_alpha += m_default_interval
			m_beta += m_default_interval
		else:
			IsTrue = 0		
	#pro_queuedelay_time_figure (line)
	#Diff_parameters_figure (line):
	read_TCP_congestion_vegas (str (m_alpha), str (m_beta), "2", "4")
