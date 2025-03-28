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
from math import ceil
from multiprocessing import Pool

from modules.mr_transport import set_advection_flows, set_exchange_flows, calc_transport

# =============================================================================================== #


#print('Number of CPUs in the system: {}'.format(os.cpu_count()))

# Necessary to add cwd to path when script run by SLURM, e.g., on BlueBEAR (since it executes a copy)
#sys.path.append(os.getcwd())

# --------------------------------------------------------------------------- #
def parallel_room_integrations(filename, particles, INCHEM_additional, custom, rel_humidity,
                               M, const_dict, ACRate, diurnal, city, date, lat, light_type,
                               light_on_times, glass, volume, timed_emissions, timed_inputs,
                               dt, t0, iroom, ichem_only, path, seconds_to_integrate,
                               custom_name, output_graph, output_species,
                               reactions_output, H2O2_dep, O3_dep, adults,
                               children, surface_area, temperatures, spline, output_main_dir):
    '''
    This function sets the initial conditions and creates the output folders,
    then runs the simulation in parallel mode.

    Arguments are the same as run_inchem(), except for the following variables which are
    defined in this function: initials_from_run, initial_conditions_gas, output_folder,
    and __file__
    '''

    #print('Inside parallel_room_integrations(), iroom=',iroom,'ichem_only=',ichem_only)

    initial_conditions_gas = 'initial_concentrations.txt'

    """
    Initial concentrations in molecules/cm^3 saved in a text file
    """
    if ichem_only == 0:
        # for first chem-only integration, init concs is taken from initial_conditions_gas
        # for now, same file/same concs for all rooms
        initials_from_run = False

        # If initials_from_run is set to False then initial gas conditions must be available
        # in the file specified by initial_conditions_gas. Inclusion of particles is optional.
        initial_conditions_gas = 'initial_concentrations.txt'

        # initial gas concentrations can be taken from a previous run of the model.
        # Set initials_from_run to True if this is the case and move a previous out_data.pickle
        # to the main folder and rename to in_data.pickle. The code will then take this
        # file and extract the concentrations from the time point closest to t0 as
        # initial conditions.
        # NB: in_data.pickle must contain all the required species, including particles if used.
    else:
        # for all but the first chem-only integration, the initial concentrations
        # are taken from previous room-specific output
        initials_from_run = True

    """
    Output
    """
    # Each output_sub_dir is located inside output_main_dir and includes the room number (iroom)
    # and the chemistry-only integration step (ichem_only)
    output_sub_dir = ('%s_%s' % ('room{:02d}'.format(iroom+1),'c{:04d}'.format(ichem_only)))
    output_folder = ('%s/%s' % (output_main_dir,output_sub_dir))
    os.mkdir('%s/%s' % (path,output_folder))
    with open('%s/__init__.py' % output_folder,'w') as f:
        pass # file created but left empty
    #print('Creating output folder:',output_folder)

    # --------------------------------------------------------------------------- #

    """
    Run the simulation
    """

    # print("----------------------------")
    # print(filename, particles, INCHEM_additional, custom, rel_humidity)
    # print(M, const_dict, ACRate, diurnal, city, date, lat, light_type)
    # print(light_on_times, glass, volume, initials_from_run)
    # print(initial_conditions_gas, timed_emissions, timed_inputs, dt, t0)
    # print(iroom, ichem_only, path, output_folder)
    # print(seconds_to_integrate, custom_name, output_graph, output_species)
    # print(reactions_output, H2O2_dep, O3_dep, adults)
    # print(children, surface_area, __file__, temperatures, spline)

    from modules.inchem_main import run_inchem
    run_inchem(filename, particles, INCHEM_additional, custom, rel_humidity,
               M, const_dict, ACRate, diurnal, city, date, lat, light_type,
               light_on_times, glass, volume, initials_from_run,
               initial_conditions_gas, timed_emissions, timed_inputs, dt, t0,
               iroom, ichem_only, path, output_folder,
               seconds_to_integrate, custom_name, output_graph, output_species,
               reactions_output, H2O2_dep, O3_dep, adults,
               children, surface_area, __file__, temperatures, spline)

    return

# --------------------------------------------------------------------------- #
def run_parallel_room_integrations(filename, particles, INCHEM_additional, custom, diurnal, city, date, lat,
                                   ambient_press, bsa_adult, bsa_child, dt, t0, end_of_total_integration,
                                   seconds_to_integrate, custom_name, output_graph, output_species, reactions_output,
                                   path, output_main_dir, nroom, mrvol, mrsurfa, mrlightt, mrglasst, mrsoft, mrpaint,
                                   mrwood, mrmetal, mrconcrete, mrpaper, mrlino, mrplastic, mrglass, mrother,
                                   all_mrtemp, all_mrrh, all_mracrate, all_mrlswitch, all_mradults, all_mrchildren,
                                   all_mremis, all_timemis, ichem_only, itvar_params): # Parallel
    '''
    Function to set up parallel integration. First create a list of inputs for each room.
    Second provide the list of inputs to the parallel_room_integrations() function.
    '''

    #print('Inside run_parallel_room_integrations(), nroom=',nroom,' and ichem_only=',ichem_only)

    # Initialize list of inputs needed for individual rooms
    room_inputs=[[0 for x in range(36)] for y in range(nroom)]

    # SECONDARY LOOP: for each chemistry-only integration period run INCHEM-Py
    # in each room and save the output of the run in a separate directory
    for iroom in range (0,nroom): # loop over rooms
        #print('iroom=',iroom)

        """
        Temperature, humidity, air density
        """
        # Temperatures are interpolated from a list of given values (`mr_tvar_room_params_*.csv`)
        # using either a 'Linear' or a 'BSpline' interpolation method. The list has the format:
        # [[time (s), temperature (K)],[time (s), temperature (K)], ...]
        # Alternatively, a constant temperature can also be set without interpolation.
        # Details of these methods are given in the INCHEM-Py user manual.
        spline = 'Linear'  # 'Linear' interpolation, by default
        temperatures = all_mrtemp[iroom] # temperature (Kelvin)
        #print('temperatures=',temperatures)

        rel_humidity = all_mrrh[iroom][itvar_params] # relative humidity (%)
        #print('rel_humidity=',rel_humidity)

        mrt = all_mrtemp[iroom][itvar_params][1]
        M = ((100*ambient_press)/(8.3144626*mrt))*(6.0221408e23/1e6) # number density (molecule cm^-3)
        #print('mrt=',mrt,'M=',M)

        # Place any parameter that needs to remain constant in the below dictionary.
        const_dict = {
            'O2':0.2095*M,
            'N2':0.7809*M,
            'H2':550e-9*M,
            'saero':1.3e-2 # aerosol surface area concentration
        }
        #print('const_dict=',const_dict)

        """
        Outdoor indoor change rates
        """
        ACRate = all_mracrate[iroom] # air change rate (s^-1)
        #print('ACRate=',ACRate)

        """
        Photolysis
        """
        light_type = mrlightt[iroom]
        #print('light_type=',light_type)

        glass = mrglasst[iroom]
        #print('glass=',glass)

        # TODO: add more comments to this section
        lotstr='['
        for ihour in range (0,24):
            if (ihour==0 and all_mrlswitch[iroom][ihour]==1) or (ihour>0 and all_mrlswitch[iroom][ihour]==1 and all_mrlswitch[iroom][ihour-1]==0):
                lotstr=lotstr+'['+str(ihour)+','
            if (ihour>0 and all_mrlswitch[iroom][ihour]==0 and all_mrlswitch[iroom][ihour-1]==1):
                lotstr=lotstr+str(ihour)+'],'
            if (ihour==23 and all_mrlswitch[iroom][ihour]==1):
                lotstr=lotstr+str(ihour+1)+'],'
        lotstr=lotstr.strip(',')
        lotstr=lotstr+']'
        if end_of_total_integration>86400:
            lotstr=lotstr.strip("[]")
            nrep=ceil(end_of_total_integration/86400)
            lotstr='['+((nrep-1)*('['+lotstr+'],'))+'['+lotstr+']]'
        #print('lotstr=',lotstr)
        if lotstr == '[]':
            light_type = 'off'
        #print('light_type=',light_type)
        if light_type != 'off':
            light_on_times = eval(lotstr)
        #print('light_on_times=',light_on_times)

        """
        Surface deposition and breath emissions from humans
        """
        # The surface dictionary exists in surface_dictionary.py in the modules folder.
        # To change any surface deposition rates of individual species, or to add species
        # this file must be edited. Production rates can be added as normal reactions
        # in the custom inputs file. To remove surface deposition AV should be set to 0 and
        # H2O2_dep and O3_dep should be set to False.
        #
        # Schemes for deposition of O3 and H2O2 are optionally provided. These schemes
        # provide calculated surface emissions proportional to O3 and H2O2 deposition
        # to different surfaces. The schemes can be turned off or on below.
        # If either scheme is on, then AV will be calculated as a sum of the AVs given
        # for the individual surfaces.

        # switch H2O2 and O3 deposition on/off
        H2O2_dep = True
        O3_dep = True

        # Number of adults and children (10 years old) in the room
        adults = all_mradults[iroom][itvar_params]
        children = all_mrchildren[iroom][itvar_params]

        # Surface areas (cm^2) of the empty room and of the people in the room, if present
        surface_room = mrsurfa[iroom]*1e4
        surface_people = (adults*bsa_adult*1e4) + (children*bsa_child*1e4)

        # Effective volume (cm^3) of the room, accounting for the presence of people
        volume = mrvol[iroom]*1e6 # TODO: account for volume of people in the room (issue #34)

        # Deposition on different types of surface is used only if the H2O2 and O3 deposition switches
        # (H2O2_dep, O3_dep) are active, otherwise AV is used
        surface_area = {             # (cm^2)
                        'SOFT'     : surface_room * mrsoft[iroom]/100,       # soft furnishings
                        'PAINT'    : surface_room * mrpaint[iroom]/100,      # painted surfaces
                        'WOOD'     : surface_room * mrwood[iroom]/100,       # wood
                        'METAL'    : surface_room * mrmetal[iroom]/100,      # metal
                        'CONCRETE' : surface_room * mrconcrete[iroom]/100,   # concrete
                        'PAPER'    : surface_room * mrpaper[iroom]/100,      # paper
                        'LINO'     : surface_room * mrlino[iroom]/100,       # linoleum
                        'PLASTIC'  : surface_room * mrplastic[iroom]/100,    # plastic
                        'GLASS'    : surface_room * mrglass[iroom]/100,      # glass
                        'HUMAN'    : surface_people,   # humans, does not automatically include breath emissions
                        'OTHER'    : surface_room * mrglass[iroom]/100}      # other surfaces, no emissions
        #print('surface_area=',surface_area)

        """
        Timed concentrations
        """
        # Set switch for timed concentrations if there is a species, or set of species that has a
        # forced density changeat a specific point in time during the integration
        # The timed concentrations inputs are assigned using a dictionary with the following format:
        #
        # timed_inputs = {species1:[[start (s), end (s), rate of increase (mol/cm^3)/s]],
        #                 species2:[[start (s), end (s), rate of increase (mol/cm^3)/s]]}
        timed_emissions = all_timemis[iroom]
        #print(timed_emissions)

        timed_inputs = all_mremis[iroom]
        #print('timed_inputs=', timed_inputs)

        # Place any species you wish to remain constant in the below dictionary.
        # Follow the format.
        const_dict = {
            'O2':0.2095*M,
            'N2':0.7809*M,
            'H2':550e-9*M,
            'saero':1.3e-2 # aerosol surface area concentration
            }
        #print('const_dict=',const_dict)

        # Assign inputs needed for individual rooms
        room_inputs[iroom][0] = filename
        room_inputs[iroom][1] = particles
        room_inputs[iroom][2] = INCHEM_additional
        room_inputs[iroom][3] = custom
        room_inputs[iroom][4] = rel_humidity
        room_inputs[iroom][5] = M
        room_inputs[iroom][6] = const_dict
        room_inputs[iroom][7] = ACRate
        room_inputs[iroom][8] = diurnal
        room_inputs[iroom][9] = city
        room_inputs[iroom][10] = date
        room_inputs[iroom][11] = lat
        room_inputs[iroom][12] = light_type
        room_inputs[iroom][13] = light_on_times
        room_inputs[iroom][14] = glass
        room_inputs[iroom][15] = volume
        room_inputs[iroom][16] = timed_emissions
        room_inputs[iroom][17] = timed_inputs
        room_inputs[iroom][18] = dt
        room_inputs[iroom][19] = t0
        room_inputs[iroom][20] = iroom
        room_inputs[iroom][21] = ichem_only
        room_inputs[iroom][22] = path
        room_inputs[iroom][23] = seconds_to_integrate
        room_inputs[iroom][24] = custom_name
        room_inputs[iroom][25] = output_graph
        room_inputs[iroom][26] = output_species
        room_inputs[iroom][27] = reactions_output
        room_inputs[iroom][28] = H2O2_dep
        room_inputs[iroom][29] = O3_dep
        room_inputs[iroom][30] = adults
        room_inputs[iroom][31] = children
        room_inputs[iroom][32] = surface_area
        room_inputs[iroom][33] = temperatures
        room_inputs[iroom][34] = spline
        room_inputs[iroom][35] = output_main_dir
        #print('room_inputs=',room_inputs[iroom])

    # Parallelize parallel_room_integrations() function with the appropriate inputs for each room
    with Pool() as pool:
        pool.starmap(parallel_room_integrations,room_inputs)


# =========================================================================================== #


if __name__ == '__main__':

    # Include user-defined settings from `settings_init.py`
    from settings_init import *

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
                # TODO: calculate exchange flows (issue #26)
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

        # Run chemistry-only integration period in each room in parallel
        run_parallel_room_integrations(filename, particles, INCHEM_additional, custom, diurnal, city, date, lat,
                                       ambient_press, bsa_adult, bsa_child, dt, t0, end_of_total_integration,
                                       seconds_to_integrate, custom_name, output_graph, output_species, reactions_output,
                                       path, output_main_dir, nroom, mrvol, mrsurfa, mrlightt, mrglasst, mrsoft, mrpaint,
                                       mrwood, mrmetal, mrconcrete, mrpaper, mrlino, mrplastic, mrglass, mrother,
                                       all_mrtemp, all_mrrh, all_mracrate, all_mrlswitch, all_mradults, all_mrchildren,
                                       all_mremis, all_timemis, ichem_only, itvar_params)
