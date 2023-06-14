# -*- coding: utf-8 -*-
"""
User set variable input file for INCHEM-Py. 
A detailed description of this file can be found within the user manual.

Copyright (C) 2019-2021 
David Shaw : david.shaw@york.ac.uk
Nicola Carslaw : nicola.carslaw@york.ac.uk

All rights reserved.

This file is part of INCHEM-Py.

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





# JGL: Added further module imports
import csv
from pandas import *
import sys
from math import ceil
import os
import datetime
import shutil





filename = 'mcm_v331.fac' # facsimile format input filename

particles = True # Are we including particles. Boolean

INCHEM_additional = True #Set to True if additional reactions from the INCHEM are being used
#that do not appear in the MCM download

custom = False # Custom reactions that are not in the MCM included?
# Format of this file is in an included custom file called custom_input.txt.


# JGL: Moved settings re emissions to here     
"""
Timed concentrations
"""
timed_emissions = True # is there a species, or set of species that has a forced density change
# at a specific point in time during the integration? If so then this needs to be set to True
# and the dictionary called timed_inputs needs to be populated. This takes the following form:
# timed_inputs = {species1:[[start time (s), end time (s), rate of increase in (mol/cm^3)/s]],
#                 species2:[[start time (s), end time (s), rate of increase in (mol/cm^3)/s]]}
# JGL: The relevant parameters are read in from room-specific csv files, mr_room_emis_params_[iroom+1] where 0 ≤ iroom ≤ nroom and iroom=0 is reserved for outdoors
nemis_species = 2 # JGL: Number of species for which emission parameters are provided in said files


nroom = 3 # JGL: Number of rooms (each room treated as one box); NB room index, iroom will start from 0

#all_secsfrommn = []
all_mrtemp = []
all_mrrh = []
all_mrpres = []
all_mraer = []
all_mrls = []
all_mrlswitch = []

all_mremis = {}

for iroom in range(0, nroom):
    
    tvar_params = read_csv("mr_tvar_room_params_"+str(iroom+1)+".csv")

    secsfrommn = tvar_params['seconds_from_midnight'].tolist()
    mrtemp = tvar_params['temp_in_kelvin'].tolist()
    mrrh = tvar_params['rh_in_percent'].tolist()
    mrpres = tvar_params['pressure_in_pascal'].tolist()
    mraer = tvar_params['aer_in_per_second'].tolist()
    mrlswitch = tvar_params['light_switch'].tolist()
    #print('mrtemp=',mrtemp)
    
    all_mrtemp.append(mrtemp)
    all_mrrh.append(mrrh)
    all_mrpres.append(mrpres)
    all_mraer.append(mraer)
    all_mrlswitch.append(mrlswitch)
    
    mremis_params = read_csv("mr_room_emis_params_"+str(iroom+1)+".csv")
    mremis_species = mremis_params['species'].tolist()
    mremis_tstart1 = mremis_params['tstart1_in_seconds'].tolist()
    mremis_tend1 = mremis_params['tend1_in_seconds'].tolist()
    mremis_emis1 = mremis_params['emis1_in_molcm-3sec-1'].tolist()
    mremis_tstart2 = mremis_params['tstart2_in_seconds'].tolist()
    mremis_tend2 = mremis_params['tend2_in_seconds'].tolist()
    mremis_emis2 = mremis_params['emis2_in_molcm-3sec-1'].tolist()
    mremis_tstart3 = mremis_params['tstart3_in_seconds'].tolist()
    mremis_tend3 = mremis_params['tend3_in_seconds'].tolist()
    mremis_emis3 = mremis_params['emis3_in_molcm-3sec-1'].tolist()
    mremis_tstart4 = mremis_params['tstart4_in_seconds'].tolist()
    mremis_tend4 = mremis_params['tend4_in_seconds'].tolist()
    mremis_emis4 = mremis_params['emis4_in_molcm-3sec-1'].tolist()
    mremis_tstart5 = mremis_params['tstart5_in_seconds'].tolist()
    mremis_tend5 = mremis_params['tend5_in_seconds'].tolist()
    mremis_emis5 = mremis_params['emis5_in_molcm-3sec-1'].tolist()
    mremis_tstart6 = mremis_params['tstart6_in_seconds'].tolist()
    mremis_tend6 = mremis_params['tend6_in_seconds'].tolist()
    mremis_emis6 = mremis_params['emis6_in_molcm-3sec-1'].tolist()
    
    mremis = {}
    for iemis_species in range(0, nemis_species):
        mremis [mremis_species[iemis_species]] = [mremis_tstart1[iemis_species],mremis_tend1[iemis_species],mremis_emis1[iemis_species]],\
         [mremis_tstart2[iemis_species],mremis_tend2[iemis_species],mremis_emis2[iemis_species]],\
         [mremis_tstart3[iemis_species],mremis_tend3[iemis_species],mremis_emis3[iemis_species]],\
         [mremis_tstart4[iemis_species],mremis_tend4[iemis_species],mremis_emis4[iemis_species]],\
         [mremis_tstart5[iemis_species],mremis_tend5[iemis_species],mremis_emis5[iemis_species]],\
         [mremis_tstart6[iemis_species],mremis_tend6[iemis_species],mremis_emis6[iemis_species]]
    all_mremis [iroom] = mremis        
    print('all_mremis(',iroom,')=',all_mremis[iroom])   
    

tcon_params = read_csv("mr_tcon_room_params.csv")

mrvol = tcon_params['volume_in_m3'].tolist()
mrsurfa = tcon_params['surf_area_in_m2'].tolist()
mrlightt = tcon_params['light_type'].tolist()
mrglasst = tcon_params['glass_type'].tolist()


# JGL: Moved assignment of dt, t0 and seconds_to_integrate to here
"""
Integration
"""
dt = 150                        # Time between outputs (s), simulation may fail if this is too large 
t0 = 0                          # time of day, in seconds from midnight, to start the simulation
total_seconds_to_integrate = 4800    # how long to run the model in seconds (86400*3 will run 3 days) #JGL: renamed total_[seconds_to_integrate]

end_of_total_integration = t0+total_seconds_to_integrate


tchem_only = 600 # JGL: Set length of chemistry-only integrations (between simple treatments of transport; assumed separable); NB MUST BE < 3600 SECONDS
nchem_only = round (total_seconds_to_integrate/tchem_only) # JGL: Calculate nearest whole number of chemistry-only integrations approximating seconds_to_integrate
if nchem_only == 0:
    nchem_only = 1
print('total_seconds_to_integrate set to',total_seconds_to_integrate)
print('tchem_only set to',tchem_only)
print('nchem_only therefore set to',nchem_only)
seconds_to_integrate = tchem_only
print('seconds_to_integrate set to',seconds_to_integrate)


for ichem_only in range (0,nchem_only): #JGL: Loop over chemistry-only integration periods
    print('ichem_only=',ichem_only)
    
    if ichem_only>0:     
        #(1) ADD SIMPLE TREATMENT OF TRANSPORT HERE
        if (__name__ == "__main__") and (nroom >=2):
            from modules.mr_transport import calc_transport
            calc_transport(custom_name,ichem_only,tchem_only,nroom,mrvol)
            
        #(2) Update t0; adjust time of day to start simulation (seconds from midnight), reflecting splitting total_seconds_to_integrate into nchem_only x tchem_only
        t0 = t0 + tchem_only
    
    #JGL: Determine time index for tvar_params, itvar_params: NB ASSUMES TCHEM_ONLY < 3600 SECONDS (TIME RESOLUTION OF TVAR_PARAMS DATA) 
    end_of_tchem_only = t0 + tchem_only
    t0_corrected = t0-((ceil(t0/86400)-1)*86400)
    end_of_tchem_only_corrected = end_of_tchem_only-((ceil(t0/86400)-1)*86400)
    if end_of_tchem_only_corrected<=86400:
        mid_of_tchem_only = 0.5*(t0_corrected + end_of_tchem_only_corrected)
    else:
        mid_of_tchem_only = (0.5*(t0_corrected + end_of_tchem_only_corrected))-86400
        if mid_of_tchem_only < 0:
            mid_of_tchem_only = mid_of_tchem_only + 86400
    itvar_params = ceil(mid_of_tchem_only/3600)-1
    print('t0=',t0)
    print('end_of_tchem_only=',end_of_tchem_only) 
    print('mid_of_tchem_only=',mid_of_tchem_only) 
    print('itvar_params=',itvar_params)       
 
    
    for iroom in range (0,nroom): #JGL: Within each chemistry-only intergation period, loop over rooms
        print('iroom=',iroom)
    
    
        # JGL: Determine temp, rel_humidity and M from tvar_params data
        temp = all_mrtemp[iroom][itvar_params] # temperature in Kelvin
        #print('temp=',temp)
        rel_humidity = all_mrrh[iroom][itvar_params] # relative humidity (presumably in %)
        #print('rel_humidity=',rel_humidity)
        M = (all_mrpres[iroom][itvar_params]/(8.3144626*temp))*(6.0221408e23/1e6) # number density of air (molecule cm^-3)
        #print('M=',M)
        AER = all_mraer[iroom][itvar_params] # Air exchange rate in [fraction of room] per second
        #print('AER=',AER)   
        light_type = mrlightt[iroom].strip()
        #print('light_type=',light_type)
        glass = mrglasst[iroom].strip()
        #print('glass=',glass)
    
    
        HMIX = (mrsurfa[iroom]/mrvol[iroom])/100 #NB Factor of 1/100 converts units from m-1 to cm-1
        print('HMIX=',HMIX)
    
        lotstr='['
        for ihour in range (0,24):
            if (ihour==0 and all_mrlswitch[iroom][ihour]==1) or (ihour>0 and all_mrlswitch[iroom][ihour]==1 and all_mrlswitch[iroom][ihour-1]==0):
                lotstr=lotstr+'['+str(ihour)+','
            if (ihour>0 and all_mrlswitch[iroom][ihour]==0 and all_mrlswitch[iroom][ihour-1]==1):
                lotstr=lotstr+str(ihour)+'],'
            if (ihour==23 and all_mrlswitch[iroom][ihour]==1):
                lotstr=lotstr+str(ihour+1)+'],'
        lotstr=lotstr.strip(",")
        lotstr=lotstr+']'
        if end_of_total_integration>86400:
            lotstr=lotstr.strip("[]")
            nrep=ceil(end_of_total_integration/86400)
            lotstr='['+((nrep-1)*('['+lotstr+'],'))+'['+lotstr+']]'       
        print('lotstr=',lotstr)
        if lotstr=="[]":
            light_type="off"
        print('light_type=',light_type)
        if light_type!="off":
            light_on_times=eval(lotstr)
            print('light_on_times=',light_on_times)
    

        # JGL: Now determining temp, rel_humidity and M from tvar_params
        #temp = 293.         # temperature in Kelvin
        #rel_humidity = 50.  # relative humidity
        #M = 2.51e+19        # number density of air (molecule cm^-3)


        #sys.exit()


        # place any species you wish to remain constant in the below dictionary. Follow the format
        const_dict = {
            'O2':0.2095*M,
            'N2':0.7809*M,
            'H2':550e-9*M,
            'saero':1.3e-2, #aerosol surface area concentration
            'CO':2.5e12,
            'CH4':4.685E13,
            'SO2':2.5e10}

        # JGL: Now determining AER from mr_tvar_params_[room number]
        """
        Outdoor indoor exchange
        """
        #AER = 0.5/3600  # Air exchange rate per second
        diurnal = True     # diurnal outdoor concentrations. Boolean
        city = "Bergen_urban" #source city of outdoor concentrations of O3, NO, NO2, and PM2.5
        # options are "London_urban", "London_suburban" or "Bergen_urban"
        # Changes to outdoor concentrations can be done in outdoor_concentrations.py
        # See the INCHEM-Py manual for details of sources and fits
    
        # JGL: Now determining light_type and glass from tcon_params, and light_on_times from tvar_params
        """
        Photolysis
        """
        date = "21-06-2020"  # day of simulation in format "DD-MM-YYYY"
        lat = 45.4         # Latitude of simulation location
        #light_type="Incand"  # Can be "Incand", "Halogen", "LED", "CFL", "UFT", "CFT", "FT", or "off"
        #"off" sets all light attenuation factors to 0 and therefore no indoor lighting is present.
        #light_on_times=[[7,19],[31,43],[55,67],[79,91]] 
        #[[light on time (hours), light off time (hours)],[light on time (hours),light_off_time (hours)],...]
        #glass="glass_C" # Can be "glass_C", "low_emissivity", "low_emissivity_film", or "no_sunlight".
        #"no_sunlight" sets all window attenuation factors to 0 and therefore no light enters from outdoors.

        # JGL: Now determining HMIX from mr_tcon_params
        """
        Surface deposition
        """
        # The surface dictionary exists in surface_dictionary.py in the modules folder.
        # To change any surface deposition rates of individual species, or to add species
        # this file must be edited. Production rates can be added as normal reactions
        # in the custom inputs file. To remove surface deposition HMIX can be set to 0.
        # HMIX is the surface to volume ratio (cm^-1)
        #HMIX = 0.02 #0.01776


        # JGL: Moved settings re init concs inside ichem_only loop; after first chem-only integration, init concs taken from previous output
        #"""
        #Initial concentrations in molecules/cm^3 saved in a text file
        #"""
        #initials_from_run = False
        ## initial gas concentrations can be taken from a previous run of the model. 
        ## Set initials_from_run to True if this is the case and move a previous out_data.pickle
        ## to the main folder and rename to in_data.pickle. The code will then take this
        ## file and extract the concentrations from the time point closest to t0 as 
        ## initial conditions.

        ## in_data.pickle must contain all of the species required, including particles if used.

        ## If initials_from_run is set to False then initial gas conditions must be available
        ## in the file specified by initial_conditions_gas, the inclusion of particles is optional.
        #initial_conditions_gas = 'initial_concentrations.txt'


        # JGL: Moved settings re emissions outside ichem_only and iroom loops; timed_inputs assigned below based on room-specific parameter string constructed above
        """
        Timed concentrations
        """
        #timed_emissions = False # is there a species, or set of species that has a forced density change
        ## at a specific point in time during the integration? If so then this needs to be set to True
        ## and the dictionary called timed_inputs (below) needs to be populated

        # When using timed emissions it's suggested that the start time and end times are divisible by dt
        # and that (start time - end time) is larger then 2*dt to avoid the integrator skipping any 
        # emissions over small periods of time.

        ## the dictionary should be populated as
        ## timed_inputs = {species1:[[start time (s), end time (s), rate of increase in (mol/cm^3)/s]],
        ##                 species2:[[start time (s), end time (s), rate of increase in (mol/cm^3)/s]]}
        #timed_inputs = {"LIMONENE":[[36720,37320,5e8],[37600,38000,5e8]],
        #                "APINENE":[[36800,37320,5e8]]}
        
        timed_inputs = all_mremis [iroom]
        print('timed_inputs=', timed_inputs)


        # JGL: Moved the following assignment of dt, t0 and seconds_to_integrate higher up
        #"""
        #Integration
        #"""
        #dt = 120                        # Time between outputs (s), simulation may fail if this is too large 
                                         # also used as max_step for the scipy.integrate.ode integrator
        #t0 = 0                          # time of day, in seconds from midnight, to start the simulation
        #seconds_to_integrate = 86400    # how long to run the model in seconds (86400*3 will run 3 days)


        """
        Output
        """
        # An output pickle file is automatically saved so that all data can be recovered
        # at a later date for analysis. 
        custom_name = 'Test_20230602_Serial'
        print('custom_name=',custom_name)

        # This function purely outputs a graph to the 
        # output folder of a list of selected species and a CSV of concentrations. 
        # If the species do not exist in the run then a key error will cause it to fail
        output_graph = True #Boolean
        output_species = ['O3',"O3OUT","tsp"]


        """
        Run the simulation
        """

        
        """
        Initial concentrations in molecules/cm^3 saved in a text file #JGL: Moved and updated settings re init concs here
        """
        
        if ichem_only == 0:
            initials_from_run = False #JGL: for first chem-only integration, init concs must be taken from initial_conditions_gas; for now, same file/same concs for all rooms
            
            # If initials_from_run is set to False then initial gas conditions must be available
            # in the file specified by initial_conditions_gas, the inclusion of particles is optional.
            initial_conditions_gas = 'initial_concentrations.txt'
        
            
            # initial gas concentrations can be taken from a previous run of the model. 
            # Set initials_from_run to True if this is the case and move a previous out_data.pickle
            # to the main folder and rename to in_data.pickle. The code will then take this
            # file and extract the concentrations from the time point closest to t0 as 
            # initial conditions.

            # in_data.pickle must contain all of the species required, including particles if used.
        
        else:
            initials_from_run = True #JGL: for all but the first chem-only integration, init concs taken from previous room-specific output
            #shutil.copyfile('%s/%s/%s' % (path,output_folder,'out_data.pickle'), '%s/%s' % (path,'in_data_c'+str(ichem_only)+'_r'+str(iroom+1)+'.pickle'))
            
        #JGL: Moved assignment of path and output_folder to settings.py and passed these to inchem_main.py
        '''
        setting the output folder in current working directory
        '''
        path=os.getcwd()
        now = datetime.datetime.now()
        #output_folder = ("%s_%s" % (now.strftime("%Y%m%d_%H%M%S"), custom_name))
        output_folder = ("%s_%s_%s" % (custom_name,'c'+str(ichem_only),'r'+str(iroom+1))) # JGL: Includes chemistry-only integration number and room number)
        os.mkdir('%s/%s' % (path,output_folder))
        with open('%s/__init__.py' % output_folder,'w') as f:
            pass
        print('Creating folder:', output_folder)


        if __name__ == "__main__":
            from modules.inchem_main import run_inchem
            run_inchem(filename, particles, INCHEM_additional, custom, temp, rel_humidity,
                       M, const_dict, AER, diurnal, city, date, lat, light_type, 
                       light_on_times, glass, HMIX, initials_from_run,
                       initial_conditions_gas, timed_emissions, timed_inputs, dt, t0, iroom, ichem_only, path, output_folder, #JGL added iroom, ichem_only, path and output_folder
                       seconds_to_integrate, custom_name, output_graph, output_species)
