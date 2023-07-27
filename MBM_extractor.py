# -*- coding: utf-8 -*-
"""
Output extraction and plotting script for INCHEM-Py.
A detailed description of this file can be found within the user manual.

Copyright (C) 2019-2021
David Shaw : david.shaw@york.ac.uk
Nicola Carslaw : nicola.carslaw@york.ac.uk

All rights reserved.

This file is additional to INCHEM-Py.

INCHEM-Py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

INCHEM-Py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with INCHEM-Py.  If not, see <https://www.gnu.org/licenses/>.

This script inputs the out_data.pickle files from model runs of INCHEM-Py
from specified output directories, saves and plots the species given in
species_to_plot in a csv and a png respectively. These are saved in the
output_folder
"""

'''
Variables to change
'''

nroom = 2     # number of rooms
nchem = 3     # number of iterations
main_dir = '20230726_145738_Test_Serial'

#directories of data to extract and plot
# out_directories=[
#     '20230727_160445_Bergen_urban']

#species to extract and plot
species_to_extract=['LIMONENE','BENZENE','TOLUENE','OH_reactivity',
                 'OH_production','J1']
#All species will be saved to a seperate csv for each input directory.
#A maximum of three seperate graphs will be made; species concentrations,
#reactivity, and production.

#times to plot from and to
start_time = 0
end_time = 3600

scale = "hours"
#can be "hours", "minutes", "seconds"

#folder to save csv and png graphs to output_folder. Can already exist or
#it will be created
output_folder = "extracted_outputs"

#should the y scale be log or not. Boolean
log_plot = False

'''
Extract and plot the data
'''
#import required packages
import pickle
import os
import matplotlib.pyplot as plt
import numpy as np

#define dictionary of output dataframes from out_directories
for iroom in range(0,nroom):
    out_directories = []
    for ichem in range (0,nchem):
        out_directories.append('%s/%s_%s' % (main_dir,'room{:02d}'.format(iroom+1),'c{:04d}'.format(ichem)))
    print(out_directories)
    print("---------")
    # out_data={}
    # for i in out_directories:
    #     print(i)
    # with open("%s/out_data.pickle" % i,'rb') as handle:
    #     out_data[i]=pickle.load(handle)

# #get the current working directory and create the output folder
# #if it doesn't exist
# path=os.getcwd()
# if not os.path.exists('%s/%s' % (path,output_folder)):
#     os.mkdir('%s/%s' % (path,output_folder))

# #create and save csvs
# for i in out_data:
#     out_data[i].to_csv("%s/%s/%s.csv" % (path,output_folder,i),
#                        columns = species_to_extract)
