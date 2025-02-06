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

# =============================================================================================== #
# Basic model settings

# Choose the chemical mechanism
# full    : the complete MCM (5833 species, 17224 reactions)
# subset  : a subset of the MCM (2575 species, 7778 reactions)
# reduced : the RCS mechanism (51 species, 137 reactions)
# minimal : the ESCS mechanism (10 species, 10 reactions)
mechanism = 'reduced'

particles = False   # set to True if particles are included
                    # NB: the chemical mechanism must include at least one of
                    # a-pinene, b-pinene, limonene

INCHEM_additional = False   # set to True to include the additional INCHEM mechanism

custom = False   # Custom reactions that are not in the MCM or in the INCHEM mechanism
                 # The format of this file is described in `custom_input.txt`

diurnal = True   # Diurnal outdoor concentrations. Boolean

city = 'London_urban'   # Source city of outdoor concentrations of O3, NO, NO2, and PM2.5
                        # Options are 'London_urban', 'London_suburban' or 'Bergen_urban'
                        # Changes to outdoor concentrations can be done in `outdoor_concentrations.py`
                        # See the INCHEM-Py manual for details of sources and fits.

date = '21-06-2020'   # Day of simulation in format DD-MM-YYYY

lat = 45.4   # Latitude of simulation location

faspect = 180   # Angle of the front side of the building (deg N)
               # 0 if building is facing N, 90 if building is facing E, etc...

Cp_coeff = [0.3,-0.2] # Pressure coefficients of the building [upwind,downwind]
                      # Cp is an empirical parameter that is a function of the air flow
                      # around the building: it depends on wind direction and speed,
                      # position and orientation of the building surfaces, presence of
                      # neighboring buildings and other obstructions to air flow.
                      #
                      # TODO: add more options for different buildings

ambient_press = 1013.0   # ambient pressure (mbar) is assumed to be constant, and is the same in all rooms
ambient_temp = 293.0     # ambient temperature (K) is assumed to be constant
                         # NB: the indoor temperature of each room is set in the
                         # corresponding `config_rooms/mr_tvar_room_params_*.csv` file.

# Average body surface area of adults and children (m^2)
bsa_adult = 1.8
bsa_child = 1.1

# =============================================================================================== #
# Integration settings and time control

dt = 150     # Time between outputs (s), simulation may fail if this is too large
             # also used as max_step for the scipy.integrate.ode integrator
t0 = 0       # time of day, in seconds from midnight, to start the simulation

# Set duration of chemistry-only integrations between simple treatments of
# transport (assumed separable)
tchem_only = 300     # NB: must be < 3600 seconds (1 hour)

# Set total duration of the model run in seconds (86400 seconds is 1 day)
total_seconds_to_integrate = 3600/6     # NB: MUST BE A MULTIPLE OF tchem_only !!
end_of_total_integration = t0 + total_seconds_to_integrate

# Calculate nearest whole number of chemistry-only integrations,
# approximating seconds_to_integrate
nchem_only = round(total_seconds_to_integrate/tchem_only)

if nchem_only == 0:
    nchem_only = 1

#print('total_seconds_to_integrate set to',total_seconds_to_integrate)
#print('tchem_only set to',tchem_only)
#print('nchem_only therefore set to',nchem_only)

seconds_to_integrate = tchem_only
#print('Seconds_to_integrate set to:',seconds_to_integrate)

# =============================================================================================== #
# Output settings

# An output pickle file is automatically saved so that all data can be recovered
# at a later date for analysis. The custom name of the model run applies to the
# output folder name and settings file copy name.
custom_name = 'TestSerial'

# INCHEM-Py calculates the rate constant for each reaction at every time point
# Setting reactions_output to True saves all reactions and their assigned constant
# to reactions.pickle and adds all calculated reaction rates to the out_data.pickle
# file which will increase its size substantially. Surface deposition rates are also
# added to the out_data.pickle file for analysis.
reactions_output = True

# This function purely outputs a graph to the
# output folder of a list of selected species and a CSV of concentrations.
# If the species do not exist in the run then a key error will cause it to fail
output_graph = False
output_species = ['O3','O3OUT']

# Setting the main output folder in the current working directory
path=os.getcwd()
now = datetime.datetime.now()
output_main_dir = ("%s_%s" % (now.strftime("%Y%m%d_%H%M%S"),custom_name))
os.mkdir('%s/%s' % (path,output_main_dir))

# =============================================================================================== #
#                           DO NOT CHANGE THE CODE BELOW
#
# The remaining settings of MBM-Flex are set in the following files (see the Manual for details):
# 1. additional chemical reactions: `custom_input.txt` (if custom=True)
# 2. initial concentrations of gas-phase species: `initial_concentrations.txt`
# 3. parameters and variables of each room: `*.csv` files in `room_config/` directory
# =============================================================================================== #

# select chemical mechanism
if mechanism == 'full':
    filename = 'chem_mech/mcm_v331.fac'
elif mechanism == 'subset':
    filename = 'chem_mech/mcm_subset.fac'
elif mechanism == 'reduced':
    filename = 'chem_mech/rcs_2023.fac'
    particles = False # ensure particles are not active with the 'reduced' mechanism
elif mechanism == 'minimal':
    filename = 'chem_mech/escs_v1.fac'
    particles = False # ensure particles are not active with the 'minimal' mechanism
else:
    sys.exit('! ERROR: please provide a valid mechanism (full, subset, reduced) !')
print('Chemical mechanism set to:',filename)

# directory with room configuration files
config_dir = 'config_rooms/'

# Information on the building, includes:
# - rooms on each floor, identified by a number
# - openings (number, size, height from the gound) between each room and between each room and outside
tcon_building = read_csv(config_dir+'mr_tcon_building.csv')

# Find the shortest sequence of rooms connecting left-right (lr_sequence) and
# front-back (fb_sequence) sides of the building. These sequences are used to
# calculate the advection flow, as a function of ambient wind data.
lr_sequence = cross_ventilation_path(tcon_building,'LR')
fb_sequence = cross_ventilation_path(tcon_building,'FB')
#print('lr_sequence:',lr_sequence,'\nfb_sequence:',fb_sequence)

# Information on ambient wind (used for the calculation of advection and exchange flows)
# - wind speed (in m/s)
# - wind direction (in deg N)
tvar_params = read_csv(config_dir+'mr_tvar_wind_params.csv')

secsfrommn = tvar_params['seconds_from_midnight'].tolist()
mrwindspd = tvar_params['wind_speed'].tolist()
mrwinddir = tvar_params['wind_direction'].tolist()
#print('mrwindspd:',mrwindspd,'\nmrwinddir:',mrwinddir)

# ambient air density (assuming dry air), in kg/m3
rho = (100*ambient_press) / (287.050 * ambient_temp)

# --------------------------------------------------------------------------- #

# READ INPUT DATA: physical characteristics of the building and of the rooms
#
# Room parameters that do not change with time: `mr_tcon_room_params.csv`
# - number of rooms
# - volume of each room
# - surface area in each room
# - type of light in each room
# - type of glass (windows) in each room
# - types of surface in each room (as percent coverage)
tcon_params = read_csv(config_dir+'mr_tcon_room_params.csv')

nroom = len(tcon_params['room_number']) # number of rooms (each room treated as one box)

mrvol = tcon_params['volume_in_m3'].tolist()
mrsurfa = tcon_params['surf_area_in_m2'].tolist()
mrlightt = tcon_params['light_type'].tolist()
mrglasst = tcon_params['glass_type'].tolist()

mrsoft = tcon_params['percent_soft'].tolist()
mrpaint = tcon_params['percent_paint'].tolist()
mrwood = tcon_params['percent_wood'].tolist()
mrmetal = tcon_params['percent_metal'].tolist()
mrconcrete = tcon_params['percent_concrete'].tolist()
mrpaper = tcon_params['percent_paper'].tolist()
mrlino = tcon_params['percent_lino'].tolist()
mrplastic = tcon_params['percent_plastic'].tolist()
mrglass = tcon_params['percent_glass'].tolist()
mrother = tcon_params['percent_other'].tolist()

# --------------------------------------------------------------------------- #

# READ INPUT DATA: physical and chemical variables of the rooms
#
# Room parameters that change with time and emissions of chemical species
all_mrtemp = []
all_mrrh = []
all_mracrate = []
all_mrlswitch = []

all_mradults = []
all_mrchildren = []

all_mremis = {}
all_timemis = []

for iroom in range(0,nroom):

    # Physical parameters of each room variable with time: `mr_tvar_room_params_*.csv`
    # - temperature (K)
    # - relative humidity (%)
    # - outdoor/indoor exchange rate (s^-1)
    # - light switch (on/off)
    #
    # N.B.: in MBM-Flex the outdoor/indoor exchange rate (acrate) accounts only for
    #       the "leakage" of the building (e.g. gaps around closed windows and doors).
    #       The indoor/outdoor exchange via open apertures is calculated by the transport
    #       module as a function of ...
    tvar_params = read_csv(config_dir+'mr_tvar_room_params_'+str(iroom+1)+'.csv')

    secsfrommn = tvar_params['seconds_from_midnight'].tolist()
    mrtemp = tvar_params['temp_in_kelvin'].tolist()
    mrrh = tvar_params['rh_in_percent'].tolist()
    mracrate = tvar_params['airchange_in_per_second'].tolist()
    mrlswitch = tvar_params['light_switch'].tolist()
    #print('mracrate=',mracrate)

    mrtemplist = [[x,y] for x,y in zip(secsfrommn,mrtemp)]
    #print('mrtemplist=',mrtemplist)

    mracrlist = dict(zip(secsfrommn,mracrate))
    #print('mracrlist=',mracrlist)

    all_mrtemp.append(mrtemplist)
    all_mrrh.append(mrrh)
    all_mracrate.append(mracrlist)
    all_mrlswitch.append(mrlswitch)
    #print('all_mracrate=',all_mracrate)

    # People in each room variable with time: `mr_tvar_expos_params_*.csv`
    # - number of adults
    # - number of children (10 years old)
    tvar_params = read_csv(config_dir+'mr_tvar_expos_params_'+str(iroom+1)+'.csv')

    secsfrommn = tvar_params['seconds_from_midnight'].tolist()
    mradults = tvar_params['n_adults'].tolist()
    mrchildren = tvar_params['n_children'].tolist()

    all_mradults.append(mradults)
    all_mrchildren.append(mrchildren)
    #print('all_mradults=',all_mradults)

    # Emissions of chemical species in each room variable with time: `mr_room_emis_params_*.csv`
    #
    # NB: when using timed emissions it's suggested that the start time and end times are
    # divisible by dt and that (start time - end time) is larger then 2*dt to avoid the
    # integrator skipping any emissions over small periods of time.
    mremis_params = read_csv(config_dir+'mr_room_emis_params_'+str(iroom+1)+'.csv')

    mremis_species = mremis_params['species'].tolist()

    mremis_tmp = {}
    for column in mremis_params.columns[1:]:
        tstart = int(column[8:])
        tstop = tstart + 3600 - 1
        mremis_tmp[column] = [[tstart,tstop,value] for value in mremis_params[column].tolist()]

    mremis = {}
    for i, species in enumerate(mremis_species):
        mremis[species] = [mremis_tmp[column][i] for column in mremis_params.columns[1:]]

    all_mremis[iroom] = mremis
    #print('all_mremis(',iroom,')=',all_mremis[iroom])

    # switch emissions OFF if the csv file for this room is empty
    if len(mremis) == 0:
        all_timemis.append(False)
    else:
        all_timemis.append(True)

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

    # --------------------------------------------------------------------------- #
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

        # Place any species you wish to remain constant in the below dictionary. Follow the format.
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
        volume = mrvol[iroom]*1e6 # TODO: account for volume of people in the room

        # Surface to volume ratio of the room (cm^-1) with and without people
        #AV = ((surface_room + surface_people)/volume_room)/100  # Factor of 1/100 converts from m^-1 to cm^-1
        #AV_empty = (surface_room/volume_room)/100

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
        #print('surfaces_AV=',surfaces_AV)

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

        if __name__ == "__main__":
            from modules.inchem_main import run_inchem
            run_inchem(filename, particles, INCHEM_additional, custom, rel_humidity,
                       M, const_dict, ACRate, diurnal, city, date, lat, light_type,
                       light_on_times, glass, volume, initials_from_run,
                       initial_conditions_gas, timed_emissions, timed_inputs, dt, t0,
                       iroom, ichem_only, path, output_folder,
                       seconds_to_integrate, custom_name, output_graph, output_species,
                       reactions_output, H2O2_dep, O3_dep, adults,
                       children, surface_area, __file__, temperatures, spline)
