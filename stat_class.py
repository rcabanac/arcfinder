#!/usr/bin/env python
#-*-coding:utf-8 -*

import os
import subprocess

from sys import argv

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pyfits
import csv
import pymc as mc

#
# We define the input of arcfinder code
#

script = argv[0]
inputlist = argv[1]
classlist = argv[2]
n = eval(argv[3])
n_lens = 0
n_notlens = 0
i=0
FILE_LIST = open(inputlist,"r", 0)
for line in FILE_LIST:
	path, filename = os.path.split(line)
	filename= filename[:-1]
	input = filename.split('.fits')
	print 'input fits image is %s path is %s filename %s' % (input[0],path, filename)
	dump,image_number = filename.split('imageEUC_VIS-')
	image_number, dump = image_number.split('.fits')
	csvfile = open(classlist, 'rb')
	reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		if image_number == row['ID'] and i<n:
			flag_lens = row['is_lens']
			if flag_lens == "1":
				n_lens = n_lens +1
			if flag_lens == "0":
				n_notlens = n_notlens + 1
			i=i+1
print "lens = ",n_lens, "not lens = ", n_notlens