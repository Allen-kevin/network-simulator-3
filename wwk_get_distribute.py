#/!usr/bin/python
#coding:utf-8

import os
import sys

delayThsh = 100000 #delay threshold
#path = '/home/wanwenkai/pqsa_simulator/rate_window_class/'
path = '/home/wanwenkai/pqsa_simulator/rate_window_class/downlink_200000/win_310000/period_2000000/'

def find_max_thput(path, writefile):
    global delayThsh
    maxThput = 0
    readfile = open(path + 'temp.txt', 'r')
    lines = readfile.readlines()
    count = 0
    for line in range(len(lines)):
        odom = lines[line].split()
        mapint = map(int, odom)
        if mapint[1] < delayThsh and mapint[0] > maxThput:
            maxThput = mapint[0]
            #print 'maxThput=%d'%(maxThput)
            count = line
    #print lines[count]
    writefile.write(lines[count])
    readfile.close()

def get_distribute(path):
    if os.path.isfile(path + 'distribute.txt'):
        os.remove(path + 'distribute.txt')
    writefile = open(path + 'distribute.txt', 'a+')

    #save minimal length of a file
    minlength = 1000
    #count = 0
    for count in range(minlength):
        tempfile = open(path + 'temp.txt', 'w')
        for fileName in os.listdir(path):
            if fileName.startswith('proUDP_') and fileName.endswith('.sum'):
                rate = int(fileName.split('-')[-3])
                #win = int(fileName.split('-')[-2])

                fileName = os.path.join(path, fileName)
                readfile = open(fileName, 'r')
                lines = readfile.readlines()
                if len(lines) < minlength:
                    continue
                    #minlength = len(lines)
                odom = lines[count].split()
                str = '%s %s %d\n'%(odom[0], odom[1], rate)
                tempfile.write(str)
                readfile.close()
        #print 'minlength = %d'%(minlength)
        tempfile.close()
        find_max_thput(path, writefile)
    writefile.close()


get_distribute(path)

'''
# when delay < 100ms,
def find_rate(path):
    #get current path
    for dir in os.listdir(path):
        if os.path.isdir(dir):
            dir = os.path.join(path, dir)
            find_rate(dir)     
        get_distribute(path)
        break

if __name__ == '__main__':
    find_rate(path)
'''
