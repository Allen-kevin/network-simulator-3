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
	path = '/home/wanwenkai/same_hours/time_'+str (which_txt)
	files = os.listdir (path)
	files.sort ()
	Istrue = 1
	init_file = 0

	while (Istrue):
		readfile = open (path+'/'+files[init_file])
		writefile = open ('/home/wanwenkai/workspace/ns-allinone-3.26/ns-3.26/downlink.txt','w')
		
		lines = readfile.readlines()
		sum_packet = 0
		start_time = 0.0

		end_time_odom = lines[-3]
		end_time = end_time_odom.split ()

		if float (end_time[0]) > 3500:
			Istrue = 0
			for line in range (len(lines) - 2):
				odom = lines[line].split()
				numbers_float = map(float,odom)
				write_str = '%.3f%s\n'%(numbers_float[1]*8.0*10/(1024*1024),'Mbps')
				writefile.write(write_str)

			sum_odom = lines[-2].split ()
			write_str = 'downklink.txt mean throuthput %.3f\n'%(float (sum_odom[4])*8.0/(float (end_time[0])*1024*1024))
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

	for line in range (len (rxlines) - 3):
		rx_odom = rxlines[line].split ()
		rx_numbers_float = map (float, rx_odom)
		tx_odom = txlines[line + 1].split ()
		tx_numbers_float = map (float, tx_odom)

		#calculate the time that a datapacket from the sender to receive
		interval_time = rx_numbers_float[0] - tx_numbers_float[1]
		if interval_time - m_delay < m_exp_time:
			delay_num += 1 
		#write the interval_time in downlink_time.txt
	print delay_num
	print len(rxlines)
	write_str = '%d %.3f\n'%(alpha, delay_num*1.0/len (rxlines))
	writefile.write (write_str)

	readtx.close ()
	readrx.close ()
	writefile.close ()

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

##########################################################################


for line in range (8,16):

	m_alpha = 2
	m_beta = 4
	m_old_alpha = 2
	m_old_beta = 4
	init_mean = 0
	
	print ("hours = %d, alpha = %d\n ",line, m_alpha)
	generate_downlink (line)
	while (1):

		read_TCP_congestion_vegas (str (m_old_alpha), str (m_old_beta), str (m_alpha), str (m_beta))
		os.system ('./waf --run scratch/tcp-variants-comparison --command-template="%s --tracing=1"')
		throughput = cal_mean_throughput (m_alpha, line)
		#cal_Queue_Delay ()
		pro_queuedelay_time (line, m_alpha)
		#figure_time ()
		if throughput > init_mean:
			init_mean = throughput
		else:
			break
		m_old_alpha = m_alpha
		m_old_beta = m_beta
		m_alpha += 1
		m_beta += 1

	pro_queuedelay_time_figure (line)
	read_TCP_congestion_vegas (str (m_alpha), str (m_beta), "2", "4")
