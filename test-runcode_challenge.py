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

#
# We define the input of arcfinder code
#

script = argv[0]
inputlist = argv[1]
classlist = argv[2]

# case 'g': inputlist is a list of fits images input filename (primary band)

if len(argv) < 3:
    sys.exit("Usage: {0}".format(sys.argv[0]))

# The line command parameters of arcfinder.exe are :

ds9_args = ""

csvfile = open(classlist, 'rb')
reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
FILE_STAT = open("challenge_stats.txt","w")
FILE_STAT.write("image_number arcfinder is_lens\n")

FILE_LIST = open(inputlist,"r", 0)
for line in FILE_LIST:
	path, filename = os.path.split(line)
	filename= filename[:-1]
	input = filename.split('.fits')
	print 'input fits image is %s path is %s filename %s' % (input[0],path, filename)

	hdulist = pyfits.open(path+'/'+filename)

	xx=int(hdulist[0].header['naxis1']/2)	# case 'x': image x center
	yy=int(hdulist[0].header['naxis2']/2)	# case 'y': image y center
	ww=hdulist[0].header['naxis1']	# case 'w': image width
	hh=hdulist[0].header['naxis2']	# case 'h': image height
	name_out1 = "result/out1_"+input[0]	# case 'o': tabulated arcfinder output
	name_out2 = "result/out2_"+input[0]	# case 's': lists all the pixels belonging to each arc candidate
	image_noise = -99				# case 'n': user provided sigma - image noise - the noise is internally
									# computed, if user defined add a "-n"+image_noise in arcfinder 
	name_mask = "" 					# case 'm': mask filename (optional)
	name_thresh = "thresh.data"		# case 't': threshold setting filename
	
	# we define all parameters of name_thresh
	# Line 1 has parameters corresponding to the smoothing filter used on the image.
	
	l1p1_smoothingsize = 7  # l1p1 - corresponds to a window size within which the smoothing is performed and 
							# this process is iterated over the complete image.
							
	l1p2_mexicanb2 =  5		# l1p2 - corresponds to the b^2 in the Mexican-hat filter applied to every pixel (x,y) in the image. 
							# The filter is given by M(x,y)=exp−[(x2+y^2)/b^2] −0.5exp−[(x^2+y^2)/2b^2].
							
	l1p3_verbose= 0			# l1p3 - a value of 1 will turn on verbose printing and 
							# outputs a smoothed image ar_sm.fits, default value is 0.
								
	# Line 2 has parameters corresponding to the detection of elongated features 
	# which are used for calculating an elongation estimator for every pixel within the image.

	l2p1_elongsize = 7		# l2p1-translates to a window size in units of pixels within which the local 
							# direction of elongation is estimated. This is done by calculating second order 
							# moments of the surface brightness distribution within this window. 
							# A local elongation estimator is assigned to the pixel at the center 
							# of the window and this process is repeated for every pixel in the input image. 
							# The code uses 2×p1+1 as the window size. Typical values for p1 are 3 to 7 pixels 
							# which will translate to window sizes of 7 to 15 pixels, respectively.
							
	l2p2_elongestim = 1.	# l2p2-is a fractional value for a threshold on the elongation estimator, 
							# given by p2×noise×(2p1+1). The smaller (larger) p2 values lead to fainter 
							# (brighter) detections.
							
	l2p3_verbose = 0		# l2p3-allows verbose printing of numbers in-between the process and ar_dt.fits 
							# which visually shows the effect of varying the parameters p1 and p2. 
							# Set this parameter to 1 to turn on the verbose printing else set it to 0.
				
	# Line 3 has parameters corresponding to connecting contiguous pixels with elongation estimator above some thresholds and 
	# measurement of candidate arc properties. The parameters up to p8 play role in the step 1 where the skeleton of the arc is constructed 
	# using the elongation estimator. In step 2, the rest of the neighbouring pixels, that is, the flesh of the arc is 
	# constructed for which p9 to p14 are required.
				
	l3p1_windowsizeconnect = 6	# l3p1- corresponds to the window size (2p1+1) centred on a pixel 
								# within which neighbouring pixels will be connected. This process is repeated for every pixel.
								
	l3p2_elongthreshold = 1.	# l3p2-threshold on the elongation estimator to accept a pixel 
								# (within the window given by p1) as part of a candidate arc 
								# and connect with neigbouring pixels, if they satisfy the same. 
								
	l3p3_minarcarea = 10		# l3p3-minimum accepted area of the candidate arc (step 1) in units of pixels. 
								# Default value is 10 and may not require modification.
								
	l3p4_maxpixcount = 1.e-10	# l3p4-maximum allowed value for the brightest pixel belonging to a candidate arc in the units of pixel counts. 
								# Since stars have extremely high pixel counts, setting a reasonable upper limit 
								# rejects any false positives in/around stars. This value should be calibrated 
								# with a test image consisting of stars and likely arc candidates.
								
	l3p5_maxarcsb = 1.5			# l3p5-threshold on the mean surface brightness value per pixel and is used as p5×σ. 
								# Higher values will allow only brighter arcs to be detected. 
								# This parameter value needs to be calibrated as per the requirement.
								
	l3p6_imagemargin = 3		# l3p6-number of pixels to be excluded from the boundary of the image 
								# during the execution of the code. This is useful when the images 
								# have bad/masked data at the boundaries and need not be searched for arc detection. 
								# Alternatively, one can restrict the image size to be scanned via the -w and -h option 
								# when running the code.
								
	l3p7_arcminlength = 7.		# l3p7-minimum acceptable length of the arc in units of pixels
								# Default value is 7 and may not require any modification.
								
	l3p8_arcminlwratio =  2.	# l3p8-minimum acceptable length-to-width ratio of the arc in units of pixels. 
								# The width of the arc is defined to be area/length. 
								# Default value is 2 and may not require modification.
								
	l3p9_arcfluxweight = 0.65	# l3p9 × meanflux -> g
	
	l3p10_arcfluxweight = 0.65	# l3p10 x meanflux -> s
	
	l3p11_window = 7			# l3p11 ->  2×l3p11+1. The flesh of the arc is recovered by introducing thresholds 
								# on the mandatory input image ( g) and a duplicated image which is smoothed with a kernel ( s). 
								# This is repeated within every window (given by p11) centred on every pixel in the images. 
								# Default values may need modification as per requirement.
								
	l3p12_arcminarea = 10		# l3p12- minimum area of final arc
	
	l3p13_arcminwidth = 1.		# l3p13- minimum width of final arc
	
	l3p14_arcmaxwidth = 10.		# l3p14-, and maximum width of the final arc feature	
								# needs to satisfy. Default values (in units of pixels) may be modified.
								
	l3p15_verbose = 0			# p15-default value is 0. If set to 1, will print extra numbers and ar_out.fits 
								# which allows to see the output of the code at the end of step 1 
								# (showing the skeleton of the arc) in a FITS format. 
								# If set to 2, will print some more numbers during the process of candidate detection 
								# with some help.
	# other definitions
				
	# here we start a loop to probe systematically the behaviour of the arcfinder under a
	# range of value for any of the above parameters.
	
	#
	# begin loop
	#
	for iter in range(0,1,1):
	
	#
	# variation on some parameters
	#
	#	image_noise =  10**-(iter+1)
	#	l1p2_mexicanb2 = iter
	#	l2p1_elongsize = iter
	#	l2p2_elongestim = (iter+1.)/2.
	#	l3p1_windowsizeconnect = iter+1
	#	l3p2_elongthreshold = 1.*(iter+1)/3.
	#	l3p3_minarcarea = iter
	# 	l3p4_maxpixcount = 10**-(iter)
	#	l3p5_maxarcsb = 10**-(iter)
	#	l3p6_imagemargin = 3
	#	l3p7_arcminlength = 1.*iter
	#	l3p8_arcminlwratio =  2.
	#	l3p9_arcfluxweight = 0.65
	#	l3p10_arcfluxweight = 0.65
	#	l3p11_window = 7
	#	l3p12_arcminarea = 10
	#	l3p13_arcminwidth = 1.
	#	l3p14_arcmaxwidth = 10.
	
		name_tresh = name_thresh + "_" + str(iter)
	
		# Open file $name_thresh
	
		FILE_THRESDATA = open(name_tresh, "w", 0)
	
	#lets write the thresh.data file used by arcfinder code
	
		header_l1 = str(l1p1_smoothingsize) +" "+ str(l1p2_mexicanb2)  +" "+ str(l1p3_verbose) + "\n"
		FILE_THRESDATA.write(header_l1)
		
		header_l2 = str(l2p1_elongsize)  +" "+ str(l2p2_elongestim)  +" "+ str(l2p3_verbose) + "\n"
		FILE_THRESDATA.write(header_l2)
		
		header_l3 = str(l3p1_windowsizeconnect)  +" "+ str(l3p2_elongthreshold)  +" "+\
		str(l3p3_minarcarea)  +" "+ str(l3p4_maxpixcount)  +" "+ str(l3p5_maxarcsb)  +" "+\
		str(l3p6_imagemargin)  +" "+ str(l3p7_arcminlength)  +" "+ str(l3p8_arcminlwratio)  +" "+\
		str(l3p9_arcfluxweight)  +" "+ str(l3p10_arcfluxweight)  +" "+ str(l3p11_window)  +" "+\
		str(l3p12_arcminarea)  +" "+ str(l3p13_arcminwidth)  +" "+ str(l3p14_arcmaxwidth)  +" "+\
		str(l3p15_verbose)+ "\n"
		
		FILE_THRESDATA.write(header_l3)
		FILE_THRESDATA.close()
				
	# definition of the command line argument of arcfinder (based on the above parameters)
	
		arcfinder_args = "./arcfinder.exe " +" -g "+path+"/"+filename+ " -n "+str(image_noise)+" -x "+\
		str(xx)+" -y "+str(yy)+" -w "+str(ww)+" -h "+str(hh)+" -o "+name_out1+"_"+str(iter)+\
		" -s "+name_out2+"_"+str(iter)+" -t "+ name_tresh
	
		print "\n",arcfinder_args
	
	### output file out1-* have the following parameters listed per detected arc:
	#		RA (hh mm ss.sss) 
	#		DEC(dd mm ss.ss)
	#		x (pix)
	#		y (pix) 
	#		area (pix)
	#		r circ (radius of a circle going through the arc in pix)
	#		peak flux (counts)
	#		integrated flux (counts)
	#		integrated flux of second band if provided (counts)
	#		length (pix)
	#		width (pix)
	#		mflag
		
	### output file out2-* have the following parameters listed per detected arc:
	#		label ###### A1, A2, A3, ... ######
	#		x (pix)
	#		y (pix)
	# 		pixel value of image1
	#		pixel value of image2 if provided
	#		elongation estimator (dimensionless).
	
	### Run the arcfinder code on the shell command line 
	### with the OMP_NUM_THREADS option that defines the number of cores to be used.
				
		subprocess.call(arcfinder_args,shell=True)
		
	# if l1p3_verbose is on,  smoothed image (filtered with mexican hat) ar_sm_*.fits are created 
	
		if l1p3_verbose > 0:
			subprocess.call("mv ar_sm.fits "+"result/ar_sm_"+input[0]+"_"+str(iter)+".fits", shell=True)
		
	# if l2p3_verbose is on,  detection image (selection based on l2p1 and l2p2 parameters) ar_dt_*.fits are created 
	
		if l2p3_verbose > 0:
			subprocess.call("mv ar_dt.fits "+"result/ar_dt_"+input[0]+"_"+str(iter)+".fits", shell=True)
				
	# if l3p15_verbose is on,  out image (selection based on l3p* parameters) ar_out_*.fits are created
						
		if l3p15_verbose > 0:
			subprocess.call("mv ar_out.fits "+"result/ar_out_"+input[0]+"_"+str(iter)+".fits", shell=True)
	
		fac1 = xx - ww/2
		fac2 = yy - hh/2
					
	### Create .reg file which can be seen by loading through the contour option in ds9 overlaid on the inputfits
			
		name_plotreg = "plot_"+input[0]+"_"+str(iter)+".reg" # ds9 region file where arc positions are stored.
	
	# Open file $name_plotreg
				
		FILE_REG = open(name_plotreg, "w", 0)
		
	# Open file out1*
	
		FILE_OUT1 = open(name_out1+"_"+str(iter), "r")
	
	# read file out1* line by line, and save coord x y of each arc
	
		line_out1 = FILE_OUT1.readlines()
		for i in range(0,len(line_out1)):
			out1_params = line_out1[i].split( )
			print name_out1+"_"+str(iter), out1_params, fac1, fac2
			xarc = int(out1_params[6])-fac1
			yarc = int(out1_params[7])-fac2
				
	# write in file $name_plotreg position x,y of each arc selected in out1*
	
			FILE_REG.write("circle("+str(xarc)+","+str(yarc)+",7) # color= green font=\"helvetica 10 bold\"  text={"+str(i)+"}\n")
		
		FILE_OUT1.close()
		FILE_REG.close()
		
#		ds9_args +=  input[0]+"_"+str(iter)+".fits "+ path+"/"+filename+" -region "+ name_plotreg+" -zoom 1 -scale zscale"
#		subprocess.call("ds9 "+ds9_args, shell=True))
#		subprocess.call("ds9 ar_*_"+input[0]+"_"+str(iter)+".fits "+ path+"/"+filename+" -region "+ name_plotreg+" -zoom 2 -scale zscale &", shell=True)

#
# We store the detection per image stat in output image challenge_stats.txt
#
		dump,image_number = filename.split('imageEUC_VIS-')
		image_number, dump = image_number.split('.fits')
		for row in reader:
			if image_number == row['ID']:
				flag_lens = row['is_lens']
				break
		if (len(line_out1)>0):
			FILE_STAT.write(image_number+" 1 "+flag_lens+"\n")
		else:
			FILE_STAT.write(image_number+" 0 "+flag_lens+"\n")
	#
	# end loop 
	#
