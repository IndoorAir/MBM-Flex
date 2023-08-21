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
"""

# This script reads the `out_data.pickle` files from all iterations of an MBM-Flex
# model run in a specified output directory, and saves the variables given by the
# user (vars_to_extract) to a csv file for each room. If the variable exist outdoors,
# it is saved in a separate csv file. All csv files are stored in the "extracted_outputs/"
# folder, inside the main output directory.

# Import modules
import os
import pandas as pd

# =============================================================================================== #
# User-specified model variables to extract

main_output_dir = '20230816_125453_TestSerial'   # folder with all outputs of the model run
nroom = 3    # number of rooms

total_seconds_to_integrate = 3600*24   # total duration of the model run (see `settings_serial.py`)

tchem_only = 300   # duration of chemistry-only integrations (see `settings_serial.py`)
nchem = int(total_seconds_to_integrate/tchem_only)

# Model variables to extract - Note that there is no need to include outdoors variables:
# if the variable exist outdoors it will be extracted automatically
vars_to_extract = [
    'O3','NO','NO2','HONO','HNO3','CO','APINENE','BPINENE','LIMONENE',
    'BENZENE','TOLUENE','TCE','OH','HO2','CH3O2','RO2','H2O','M',
    'H2O2','adults','children',
    'OH_reactivity','OH_production','J4','temp','ACRate','tsp','tspx',
                    ]

# The "extracted_outputs" folder where the csv files are saved is inside `main_output_dir`
output_folder = ('%s/extracted_outputs' % main_output_dir)

# =============================================================================================== #
# Extract the selected variables and save them to one csv files per room, plus one csv files for
# outdoors concentrations

for iroom in range(0,nroom):

    # directories of data to extract
    out_directories = []
    for ichem in range (0,nchem):
        out_directories.append('%s/%s_%s' % (main_output_dir,'room{:02d}'.format(iroom+1),'c{:04d}'.format(ichem)))

    # dictionary of output dataframes from out_directories
    out_data = {}
    for i in out_directories:
        with open('%s/out_data.pickle' % i, 'rb') as handle:
            df = pd.read_pickle(handle)
            out_data[i] = df.drop(df.index[-1])

    # create the extracted_outputs folder if it doesn't exist
    path=os.getcwd()
    if not os.path.exists('%s/%s' % (path,output_folder)):
        os.mkdir('%s/%s' % (path,output_folder))

    # join all output for a room and save it to the corresponding csv file
    out_merged = pd.concat(out_data.values())
    out_merged.to_csv('%s/%s/%s_%s.csv' % (path,output_folder,main_output_dir,'room{:02d}'.format(iroom+1)),
                      columns=vars_to_extract, index_label='Time')

    # extract those variables listed in vars_to_extract that exist outdoors
    outvars_to_extract = []
    if iroom == 0: # use output of ROOM 1 for outdoor variables
        for v in vars_to_extract:
            vout = v+'OUT'
            if vout in out_merged.columns:
                outvars_to_extract.append(vout)
        out_merged.to_csv('%s/%s/%s_%s.csv' % (path,output_folder,main_output_dir,'outdoor'),
                      columns=outvars_to_extract, index_label='Time')

print('\n*** Selected variables extracted and saved to %s/ ***' % output_folder)
