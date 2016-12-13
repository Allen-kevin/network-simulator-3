#!/usr/bin/env python
#file:file_to_file.py
#The function of this scripts is to change file's content to another format that we want,
#Have some thing in some file which we needn't, sach as timeout and sleep, so we should 
#againt it.
#Our target is record a data that is the sum of packet received per 100ms.

import os
import os.path
import shutil

timeout = open('/home/wanwenkai/cubic/data/public_data/tcp-simulator/timeoutfile.txt','w')
foldpath = '/home/wanwenkai/cubic/detail_discription_scripts/tcp-simulator/P1P2P3'
newfoldpath = '/home/wanwenkai/cubic/detail_discription_scripts/tcp-simulator/UDP_P1P2P3'

folds = os.listdir(foldpath)
folds.sort()

for line in folds:
	#get path of fold,line is just a name of fold in folds, not a path and not a file.
	fold = foldpath+'/'+line
	newpath = newfoldpath+'/'+line

	if os.path.isdir(fold):

		files = os.listdir(fold)
		files.sort()

		for file in files:

			#if not os.path.isdir(file):
			last_time = 0.0
			writefile =  open(newpath+'/'+file,'w')
			f = open(fold+'/'+file)
			lines = f.readlines()

			#initial
			first_line = lines[0]
			init_odom = first_line.split()
			init_time = float(init_odom[0])

			sum_bytes = 0
			sum = 0
			numbers_time = init_time

			print file
			interval = 0.0
			#timeout_num = 0
			for line in range(len(lines)):
				odom = lines[line].split()
				
				#if have line is timeout or sleep, we calculate the sum time of timeout add sleep
				#and read next line.
					if odom[0] == 'TimeOut' or odom[0] == 'Sleep':
					interval = float(odom[1]) + interval
					write_timeout_and_sleep = '%s %s\n'%(file,lines[line])
					timeout.write(write_timeout_and_sleep)
					continue

				#if this line is not timeout and sleep, we should record it's information
				numbers_float = map(float,odom)
				#get the sum of packet in this file
				sum_bytes = sum_bytes + numbers_float[1]
				last_time = numbers_float[0]
				#numbers_time is the last time we stop.
				if numbers_float[0] - interval - numbers_time > 0.1:
					numbers_time = numbers_float[0] - interval
					#numbers_time = n
					write_str = '%.2f %.2f\n'%(numbers_float[0] - init_time,sum)
					writefile.write(write_str)
					sum = 0
					sum = sum + numbers_float[1]
				else :
					sum = sum + numbers_float[1]
				
			f.close()
			str_1 = '# total data (network-layer): %.2f bytes (%.2fMbit)\n'%(sum_bytes,sum_bytes*8/(1024*1024))
			str_2 = '# throughput (network-layer): %.2fbytes/s\n'%(sum_bytes/(last_time - init_time - interval))
			writefile.write(str_1)
			writefile.write(str_2)
			writefile.close()
timeout.close()

