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

# Import modules
import os
import sys
import datetime
from math import ceil
from pandas import read_csv

from modules.mr_transport import cross_ventilation_path, set_advection_flows, set_exchange_flows, calc_transport

from multiprocessing import Pool # Parallel

# =============================================================================================== #


#print('Number of CPUs in the system: {}'.format(os.cpu_count()))

# Necessary to add cwd to path when script run by SLURM, e.g., on BlueBEAR (since it executes a copy)
#sys.path.append(os.getcwd())

# --------------------------------------------------------------------------- #
def parallel_room_integrations(iroom, ichem_only, temp, rel_humidity, M, AER, light_type, glass, AV, light_on_times, timed_inputs,
                               custom_name, filename, particles, INCHEM_additional, custom, timed_emissions, dt, t0, seconds_to_integrate,
                               output_graph, output_species):
    '''
    '''

    print('Inside parallel_room_integrations, iroom=',iroom,'ichem_only=',ichem_only)

    # JGL: Determine temp, rel_humidity and M from tvar_params data
#    temp = all_mrtemp[iroom][itvar_params] # temperature in Kelvin
#    #print('temp=',temp)
#    rel_humidity = all_mrrh[iroom][itvar_params] # relative humidity (presumably in %)
#    #print('rel_humidity=',rel_humidity)
#    M = (all_mrpres[iroom][itvar_params]/(8.3144626*temp))*(6.0221408e23/1e6) # number density of air (molecule cm^-3)
#    #print('M=',M)
#    AER = all_mraer[iroom][itvar_params] # Air exchange rate in [fraction of room] per second
#    #print('AER=',AER)
#    light_type = mrlightt[iroom].strip()
#    #print('light_type=',light_type)
#    glass = mrglasst[iroom].strip()
#    #print('glass=',glass)


#    AV = (mrsurfa[iroom]/mrvol[iroom])/100 #NB Factor of 1/100 converts units from m-1 to cm-1
    #print('AV=',AV)

#    lotstr='['
#    for ihour in range (0,24):
#        if (ihour==0 and all_mrlswitch[iroom][ihour]==1) or (ihour>0 and all_mrlswitch[iroom][ihour]==1 and all_mrlswitch[iroom][ihour-1]==0):
#            lotstr=lotstr+'['+str(ihour)+','
#        if (ihour>0 and all_mrlswitch[iroom][ihour]==0 and all_mrlswitch[iroom][ihour-1]==1):
#            lotstr=lotstr+str(ihour)+'],'
#        if (ihour==23 and all_mrlswitch[iroom][ihour]==1):
#            lotstr=lotstr+str(ihour+1)+'],'
#    lotstr=lotstr.strip(",")
#    lotstr=lotstr+']'
#    if end_of_total_integration>86400:
#        lotstr=lotstr.strip("[]")
#        nrep=ceil(end_of_total_integration/86400)
#        lotstr='['+((nrep-1)*('['+lotstr+'],'))+'['+lotstr+']]'
#    #print('lotstr=',lotstr)
#    if lotstr=="[]":
#        light_type="off"
#    #print('light_type=',light_type)
#    if light_type!="off":
#        light_on_times=eval(lotstr)
#        #print('light_on_times=',light_on_times)


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

    # JGL: Now determining AV from mr_tcon_params
    """
    Surface deposition
    """
    # The surface dictionary exists in surface_dictionary.py in the modules folder.
    # To change any surface deposition rates of individual species, or to add species
    # this file must be edited. Production rates can be added as normal reactions
    # in the custom inputs file. To remove surface deposition AV can be set to 0.
    # AV is the surface to volume ratio (cm^-1)
    #AV = 0.02 #0.01776


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

#    timed_inputs = all_mremis [iroom]
#    print('timed_inputs=', timed_inputs)


    # JGL: Moved the following assignment of dt, t0 and seconds_to_integrate higher up
    #"""
    #Integration
    #"""
    #dt = 150                        # Time between outputs (s), simulation may fail if this is too large
                                     # also used as max_step for the scipy.integrate.ode integrator
    #t0 = 0                          # time of day, in seconds from midnight, to start the simulation
    #seconds_to_integrate = 86400    # how long to run the model in seconds (86400*3 will run 3 days)


    """
    Run the simulation
    """


    """
    Initial concentrations in molecules/cm^3 saved in a text file #JGL: Moved and updated settings re init concs here
    """

    initial_conditions_gas = 'initial_concentrations.txt'

    if ichem_only == 0:
        initials_from_run = False #JGL: for first chem-only integration, init concs must be taken from initial_conditions_gas; for now, same file/same concs for all rooms

        # If initials_from_run is set to False then initial gas conditions must be available
        # in the file specified by initial_conditions_gas, the inclusion of particles is optional.
        #initial_conditions_gas = 'initial_concentrations.txt'


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


    #if __name__ == "__main__":
    from modules.inchem_main import run_inchem
    run_inchem(filename, particles, INCHEM_additional, custom, temp, rel_humidity,
                    M, const_dict, AER, diurnal, city, date, lat, light_type,
                    light_on_times, glass, AV, initials_from_run,
                    initial_conditions_gas, timed_emissions, timed_inputs, dt, t0, iroom, ichem_only, path, output_folder, #JGL added iroom, ichem_only, path and output_folder
                    seconds_to_integrate, custom_name, output_graph, output_species)

    return

# --------------------------------------------------------------------------- #
def run_parallel_room_integrations(nroom, ichem_only, all_mrtemp, all_mrrh, all_mrpres, all_mraer, mrlightt, mrglasst,
                                   itvar_params, mrvol, mrsurfa, all_mrlswitch, all_mremis, custom_name, filename,
                                   particles, INCHEM_additional, custom, dt, t0, seconds_to_integrate,
                                   output_graph, output_species): # Parallel
    '''
    '''

    print('Inside run_parallel_room_integrations, nroom=',nroom,' and ichem_only=',ichem_only)

    room_inputs=[[0 for x in range(22)] for y in range(nroom)]
    for iroom in range(nroom):
        #print('iroom=',iroom)

        light_type=mrlightt[iroom].strip()
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
        #print('lotstr=',lotstr)
        if lotstr=="[]":
            light_type="off"
        #print('light_type=',light_type)
        if light_type!="off":
            light_on_times=eval(lotstr)
            #print('light_on_times=',light_on_times)

        room_inputs[iroom][0] = iroom
        room_inputs[iroom][1] = ichem_only
        room_inputs[iroom][2] = all_mrtemp[iroom][itvar_params] # temperature in Kelvin
        room_inputs[iroom][3] = all_mrrh[iroom][itvar_params] # relative humidity (presumably in %)
        room_inputs[iroom][4] = (all_mrpres[iroom][itvar_params]/(8.3144626*all_mrtemp[iroom][itvar_params]))*(6.0221408e23/1e6) # number density of air (molecule cm^-3)
        room_inputs[iroom][5] = all_mraer[iroom][itvar_params] # Air exchange rate in [fraction of room] per second
        room_inputs[iroom][6] = light_type
        room_inputs[iroom][7] = mrglasst[iroom].strip()
        room_inputs[iroom][8] = (mrsurfa[iroom]/mrvol[iroom])/100 #AV; NB Factor of 1/100 converts units from m-1 to cm-1
        room_inputs[iroom][9] = light_on_times
        room_inputs[iroom][10] = all_mremis [iroom]
        room_inputs[iroom][11] = custom_name
        room_inputs[iroom][12] = filename
        room_inputs[iroom][13] = particles
        room_inputs[iroom][14] = INCHEM_additional
        room_inputs[iroom][15] = custom
        room_inputs[iroom][16] = timed_emissions
        room_inputs[iroom][17] = dt
        room_inputs[iroom][18] = t0
        room_inputs[iroom][19] = seconds_to_integrate
        room_inputs[iroom][20] = output_graph
        room_inputs[iroom][21] = output_species


        print('room_inputs=',room_inputs[iroom])


    print('Inside run_parallel_room_integrations, room_inputs=',room_inputs)
    with Pool() as pool:
        pool.starmap(parallel_room_integrations,room_inputs)
        #pool.join()


# =============================================================================================== #


if __name__ == '__main__':
    from settings_init import *
    
    # =========================================================================== #
    
    # PRIMARY LOOP: run for the duration of tchem_only, then execute the
    # transport module (`mr_transport.py`) and reinitialize the model,
    # then run again until end_of_total_integration
    for ichem_only in range (0,nchem_only): # loop over chemistry-only integration periods
    
        """
        Transport between rooms
    
        Accounted starting from the second chemistry-only step (ichem_only=1, 2, 3, etc...)
        """
        if ichem_only > 0:
    
            # (1) Add simple treatment of transport between rooms here
            if (__name__ == "__main__") and (nroom >= 2):
                # convection flows
                trans_params = set_advection_flows(faspect,Cp_coeff,nroom,tcon_building,lr_sequence,fb_sequence,mrwinddir[itvar_params],mrwindspd[itvar_params],rho)
                # TODO: calculate exchange flows
                ##trans_params = set_exchange_flows(tcon_building,lr_sequence,fb_sequence,trans_params)
                # apply inter-room transport of gas-phase species and particles
                calc_transport(output_main_dir,custom_name,ichem_only,tchem_only,nroom,mrvol,trans_params)
                print('==> transport applied at iteration:', ichem_only)
            else:
                print('==> transport not applied at iteration:', ichem_only)
    
            # (2) Update t0; adjust time of day to start simulation (seconds from midnight),
            #     reflecting splitting total_seconds_to_integrate into nchem_only x tchem_only
            t0 = t0 + tchem_only
    
        # Determine time index for tvar_params, itvar_params
        # NB: assumes tchem_only < 3600 seconds (time resolution of tvar_params data)
        end_of_tchem_only = t0 + tchem_only
        t0_corrected = t0-((ceil(t0/86400)-1)*86400)
        end_of_tchem_only_corrected = end_of_tchem_only-((ceil(t0/86400)-1)*86400)
        if end_of_tchem_only_corrected <= 86400:
            mid_of_tchem_only = 0.5*(t0_corrected + end_of_tchem_only_corrected)
        else:
            mid_of_tchem_only = (0.5*(t0_corrected + end_of_tchem_only_corrected))-86400
            if mid_of_tchem_only < 0:
                mid_of_tchem_only = mid_of_tchem_only + 86400
        itvar_params = ceil(mid_of_tchem_only/3600)-1
        #print('t0=',t0)
        #print('end_of_tchem_only=',end_of_tchem_only)
        #print('mid_of_tchem_only=',mid_of_tchem_only)
        #print('itvar_params=',itvar_params)

        run_parallel_room_integrations(nroom, ichem_only, all_mrtemp, all_mrrh, all_mrpres, all_mraer, mrlightt, mrglasst,
                                       itvar_params, mrvol, mrsurfa, all_mrlswitch, all_mremis, custom_name, filename,
                                       particles, INCHEM_additional, custom, dt, t0, seconds_to_integrate,
                                       output_graph, output_species)
