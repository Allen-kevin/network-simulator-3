import os
import matplotlib
matplotlib.use('agg')
import numpy as np
import matplotlib.pyplot as plt

top = '/home/wanwenkai/pqsa_simulator/rate_distribute/'

#path = '/home/wanwenkai/pqsa_simulator/rate_window_class/'
path = '/home/wanwenkai/pqsa_simulator/rate_window_class/downlink_600000/win_310000/period_2000000/'
#count line of a file
def linecount(filename):
    return len(open(filename, 'r').readlines())

def mkdir_save_path(filename):
    print 'mkdir_save_path'
    path_str = filename.split('/')
    str = os.path.join(top, path_str[-4])
    if not os.path.isdir(str):
        os.mkdir(str)
    str = os.path.join(str, path_str[-3])
    if not os.path.isdir(str):
        os.mkdir(str)
    str = os.path.join(str, path_str[-2])
    return str
    
#figure rate distribution
def figure_distribution(filelength, filename):
    print 'figure_distribution'
    data = np.loadtxt(filename)
    plt.figure()
    x = range(0, filelength, 1)
    plt.plot(x, data[:, -1], 'o')
    plt.xlabel('time/s')
    plt.ylabel('rate')
    save_path = mkdir_save_path(filename)
    plt.savefig(save_path + '_rate_distribution.pdf', format='pdf')

def find_distribution(path):
    for filename in os.listdir(path):
        if filename.startswith('distri'):
            filename = os.path.join(path, filename)
            filelength = linecount(filename)
            figure_distribution(filelength, filename)
'''
def get_path(path):
    for dir in os.listdir(path):
        if os.path.isfile(dir):
            find_distribution(path)
            return
        if os.path.isdir(dir):
            winpath = os.path.join(path, dir)
            get_path(winpath)

if __name__ == '__main__':
    get_path(path)
'''
find_distribution(path)

