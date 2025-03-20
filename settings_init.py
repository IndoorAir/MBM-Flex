# -*- coding: utf-8 -*-
"""
"""

# Import modules
import os
import sys
import datetime
from pandas import read_csv

from modules.mr_transport import cross_ventilation_path

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
total_seconds_to_integrate = 3600*6     # NB: MUST BE A MULTIPLE OF tchem_only !!
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

# This function purely outputs a graph to the
# output folder of a list of selected species and a CSV of concentrations.
# If the species do not exist in the run then a key error will cause it to fail
output_graph = False
output_species = ['O3','O3OUT']

# INCHEM-Py calculates the rate constant for each reaction at every time point
# Setting reactions_output to True saves all reactions and their assigned constant
# to reactions.pickle and adds all calculated reaction rates to the out_data.pickle
# file which will increase its size substantially. Surface deposition rates are also
# added to the out_data.pickle file for analysis.
reactions_output = True

# Setting the main output folder in the current working directory
path = os.getcwd()
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
