# -*- coding: utf-8 -*-

# This script reads a specified pickle file created by an MBM-Flexmodel run, 
# It saves the variables given by the user (vars_to_extract) to a csv file for each room. 
# If the variable exist outdoors, it is saved in a separate csv file.
# All csv files are stored in the extracted_outputs folder, inside the main output directory.
# An excel filename can optionally be provided, in which case the data will also be output to an excel file

# Import modules
import os
import pickle
import pandas as pd

# =============================================================================================== #
# User-specified model variables to extract

pickle_file = 'results.pkl'
extracted_outputs_folder = 'extracted_outputs'
extracted_excel_filename = None

# Model variables to extract - Note that there is no need to include outdoors variables:
# if the variable exist outdoors it will be extracted automatically
vars_to_extract = [
    'O3','NO','NO2','HONO','HNO3','CO','APINENE','BPINENE','LIMONENE',
    'BENZENE','TOLUENE','TCE','OH','HO2','CH3O2','RO2','H2O','M',
    'H2O2','adults','children',
    'OH_reactivity','OH_production','J4','temp','ACRate','tsp','tspx',
                    ]

# Load the datafile

with open(pickle_file, 'rb') as handle:
    data = pickle.load(handle)

# =============================================================================================== #
# Extract the selected variables and save them to one csv files per room, plus one csv files for
# outdoors concentrations

for room_name, room_pd in data.items():

    # create the extracted_outputs folder if it doesn't exist
    path = os.getcwd()
    if not os.path.exists(f'{path}/{extracted_outputs_folder}'):
        os.mkdir(f'{path}/{extracted_outputs_folder}')

    # extract those variables listed in vars_to_extract that exist in the data
    existing_vars_to_extract = (v for v in vars_to_extract if v in room_pd.columns)
    room_pd.to_csv(f'{path}/{extracted_outputs_folder}/{room_name}.csv',
                   columns=existing_vars_to_extract, index_label='Time')

    # extract those variables listed in vars_to_extract that exist in the outdoor data
    outvars_to_extract = (v+'OUT' for v in vars_to_extract if v+'OUT' in room_pd.columns)
    room_pd.to_csv(f'{path}/{extracted_outputs_folder}/{room_name}_outdoor.csv',
                   columns=outvars_to_extract, index_label='Time')


# =============================================================================================== #
# Optional: Extract the selected variables and save them to one excel file with one sheet per room

if extracted_excel_filename:
    with pd.ExcelWriter(f'{path}/{extracted_outputs_folder}/{extracted_excel_filename}.xlsx') as writer:
        for room_name, room_pd in data.items():
            existing_vars_to_extract = list(v for v in vars_to_extract if v in room_pd.columns)
            room_pd.to_excel(writer, columns=existing_vars_to_extract, index_label='Time', sheet_name=room_name)

print(f'\n*** Selected variables extracted and saved to {extracted_outputs_folder}/ ***')
