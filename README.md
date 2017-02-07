# arcfinder

arcfinder is a python script based on Alard arcfinder code (https://arxiv.org/abs/astro-ph/0606757v1)
 
 Alard original code in C has been debugged and modified into a C version that runs on
 my Mac OS Sierra 10.12.3

 The present release contains: 
 
 - the C code: check readme.txt 
 a makefile allows you to compile with reference files installed by macport.
 - python scripts:
 optimization-arcfinder.py: run loops on some parameters of arcfinder
 optimized_arcfinder.pym run arcfinder once on one set (hopefully optiumized) of parameters		
 stat_class.py: compute the efficiency of arcfinder on SL Challenge

