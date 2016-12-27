#!/usr/bin/env python

import os
import matplotlib
matplotlib.use ('agg')
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
import fileinput


def change_TCP_congestion (cong):
	if cong == 0:
		print ("congestion control is cubic")
		os.system ('echo cubic > /proc/sys/net/ipv4/tcp_congestion_control')
	elif cong == 1:
		print ("congestion control is veno")
		os.system ('echo veno > /proc/sys/net/ipv4/tcp_congestion_control')
	elif cong == 2:
		print ("congestion control is vegas")
		os.system ('echo vegas > /proc/sys/net/ipv4/tcp_congestion_control')
	else:
		print ("congestion control is westwood")
		os.system ('echo westwood > /proc/sys/net/ipv4/tcp_congestion_control')

def change_TCP_retransmission (re):
	if re == 0:
		print ("retransmission algorithm is RH")
		os.system ('echo RH > /proc/sys/net/ipv4/tcp_retransmission_algorithm')
	elif re == 1:
		print ("retransmission algorithm is PRR")
		os.system ('echo PRR > /proc/sys/net/ipv4/tcp_retransmission_algorithm')
	elif re == 2:
		print ("retransmission algorithm is SARR")
		os.system ('echo SARR > /proc/sys/net/ipv4/tcp_retransmission_algorithm')
	else:
		print ("retransmision algorithm is PQRC")
		os.system ('echo PQRC > /proc/sys/net/ipv4/tcp_retransmission_algorithm')


os.system ('cat /proc/net/tcpprobe > /home/wanwenkai/data/probe.txt &')
os.system ('pid_probe=$!')
os.system ('tcpdump -i eth10 tcp -w /home/wanwenkai/data/dump.pcap &')
os.system ('pid_dump=$!')
os.system ('sleep 1')

for cong in range (0,2):
	change_TCP_congestion (cong)
	for re in range (0,2):
		change_TCP_retransmission (re)
		for time in range (2):
			print ("this is %d test"%time)
			os.system ('iperf -c 192.168.123.212 -i 1 -t 10')

os.system ('sleep 1')
os.system ('kill $pid_probe')
os.system ('kill $pid_dump')
