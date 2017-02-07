#!/usr/bin/env python
#-*-coding:utf-8 -*

import os
import subprocess

from sys import argv

filename = argv[1]
file = open(filename,"r")
array = file.readlines()

notlens = 0
lens = 0
falsepositive = 0
falsenegative = 0
for line in array[1:]:
	id, arcfinder, islens = line.split(' ')
#	print "id",id, "arc",arcfinder, "islens",islens
	if eval(arcfinder) == eval(islens):
		if eval(islens) == 0:
			notlens = notlens + 1
		else:
			lens = lens + 1
	elif eval(arcfinder) == 1:
		falsepositive= falsepositive+1
	else:
		falsenegative = falsenegative+1
print "lens = ", lens,"\n", "not lens =",notlens,"\n","false positive = ",falsepositive, "\n", "false negative = ",falsenegative,"\n"
