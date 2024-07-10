# -*- coding: utf-8 -*-
'''
Functions for transport in MBM-Flex
'''

import pickle
import re
import pandas as pd
from math import cos


def connecting_room_sequence(sequence_old, info_room):
    '''
    Given a list of room sequences, this function creates a new list of room
    sequences which include the number of each room that connects to
    the last room in each sequence.

    inputs:
        sequence_old = initial list of room sequences
        info_room = list of all the rooms that connect to a room

    returns:
        sequence_new = final list of room sequences
    '''

    # select only rooms that are connected to other rooms
    nroom = len(info_room)
    sequence_tmp = []
    if nroom != 0:
        for n in range(nroom):
            sequence_tmp.append(sequence_old)

    # add numbers of rooms that connect to the last rooms in each
    # room sequence
    sequence_new = []
    next_room = info_room['rdest'].values
    for n in range(len(sequence_tmp)):
        if type(sequence_tmp[n]) != list:
            sequence_new.append([sequence_tmp[n]] + [next_room[n]])
        else:
            sequence_new.append(sequence_tmp[n] + [next_room[n]])
    sequence_new.sort()
    return sequence_new


def cross_ventilation_path(info_building,ventil_dir):
    '''
    This function finds the shortest path between a room with an opening on the left (or front) side
    and a room with an opening on the right (or back) side of a building.

    inputs:
        info_building = dataframe describing the connections between rooms and with outdoors
        ventil_dir = direction of cross ventilation ('LR' for left/right; 'FB' for front/back)

    returns:
        io_sequence = sequence of rooms connecting the left/right or front/back sides
    '''

    # choose left/right or front/back direction
    if ventil_dir == 'LR':
        ventil_entry = 'Left'
        ventil_exit = 'Right'
        ventil_str = 'left/right'
    elif ventil_dir == 'FB':
        ventil_entry = 'Front'
        ventil_exit = 'Back'
        ventil_str = 'front/back'
    else:
        print('Input error: specify LR or FB direction')
        return -1


    # get number of floors
    info_floor = info_building['floor']
    nfloor = info_floor.drop_duplicates().tolist()

    # loop over each floor
    for nf in nfloor:
        print('now on floor:', nf)

        # -------------------------------------------------------------------------
        # count number of openings on the left and right side of the building
        noside_entry = 0
        noside_exit = 0
        for nr in range(len(info_building)):
            if info_building.loc[nr,'floor'] == nf:
                if (info_building.loc[nr,'rdest'] == 0) and (info_building.loc[nr,'oarea'] > 0) and (info_building.loc[nr,'oside'] == ventil_entry):
                    noside_entry  = noside_entry + 1
                if (info_building.loc[nr,'rdest'] == 0) and (info_building.loc[nr,'oarea'] > 0) and (info_building.loc[nr,'oside'] == ventil_exit):
                    noside_exit  = noside_exit + 1

        # one opening on each side of the building
        if (noside_entry == 1) and (noside_exit == 1):
            side_entry = info_building.loc[(info_building['rdest'] == 0) & (info_building['oarea'] > 0) & (info_building['oside'] == ventil_entry)]
            side_exit = info_building.loc[(info_building['rdest'] == 0) & (info_building['oarea'] > 0) & (info_building['oside'] == ventil_exit)]

            roside_entry = side_entry.loc[side_entry['floor'] == nf]['rorig'].values[0]
            roside_exit = side_exit.loc[side_exit['floor'] == nf]['rorig'].values[0]

            print('\trooms with opening on the', ventil_str, 'sides:', roside_entry, roside_exit)

            # the left and right openings are in the same room
            if roside_entry == roside_exit:
                print('\t-->', ventil_str, 'cross ventilation is treated as enhanced indoor-outdoor exchange on floor', nf)
                exploring_cv = False
            # the left and right openings are in different rooms, so there can be cross ventilation
            elif roside_entry != roside_exit:
                exploring_cv = True

        # at least one side of the building has no openings
        if (noside_entry != 1) or (noside_exit != 1):
            print('\t-->', ventil_str, 'cross ventilation does not occur on floor', nf)
            exploring_cv = False

        # multiple openings on either side of the building
        # NB: this needs to be implemented at a later stage
        if (noside_entry > 1) or (noside_exit > 1):
            print('\tWARNING: please specify only one', ventil_str, 'aperture on floor', nf)
            exploring_cv = False

        # -------------------------------------------------------------------------
        # determine the shortest path connecting the left and the right sides of the building
        if exploring_cv == True:
            io_sequence = []
            tmp_sequence = [[roside_entry]]
            info_floor = info_building.loc[(info_building['floor'] == nf) & (info_building['rdest'] != 0) & (info_building['oarea'] > 0)]
            while exploring_cv == True:
                # on each floor find the rooms connected to other rooms, starting from the room with opening on the left side of
                # the building and create a list of possible room sequences that connect both sides of the building
                seq2 = []
                #print('*** new sequence:', tmp_sequence)
                for i in range(len(tmp_sequence)):
                    #print('now doing:', tmp_sequence[i])
                    info_room = info_floor.loc[info_building['rorig'] == tmp_sequence[i][-1]]

                    seq1 = connecting_room_sequence(tmp_sequence[i], info_room)
                    seq2 = seq2 + seq1

                # find the sequence which contains a room with an opening on the right side of the building
                # and ensure that it does not also have an opening on the left side
                seq3 = []
                for j in range(len(seq2)):
                    io_path = seq2[j]
                    if io_path[-1] == roside_exit:
                        io_sequence = io_path.copy()
                        print('\t-->', ventil_str, 'cross ventilation occurs via rooms', io_sequence, 'on floor', nf)
                        exploring_cv = False
                    if io_path.count(io_path[-1]) == 1:
                        seq3.append(io_path)

                tmp_sequence = seq3.copy()

                # stop if there is no possible sequence connecting the left and right sides of the building
                if len(tmp_sequence) == 0:
                    exploring_cv = False
                    print('\t-->', ventil_str, 'cross ventilation is not possible on floor', nf)

            # add 0 for outdoors at the beginning and end of the sequence
            io_sequence = [0] + io_sequence + [0]
        else:
            io_sequence = [0]

    return io_sequence


def wind_components(faspect,winddir,windspd):
    '''
    For a building with a given orientation (relative to N), this function determines
    the component of wind parallel to the left/right and to the front/right
    ventilation paths of the building. The ventilation paths are determine by the
    function cross_ventilation_path().

    inputs:
        faspect = angle of the building front
        winddir = wind direction
        windspd = wind speed

    returns:
        windspd_lr = wind component parallel to left/right ventilation path
        windspd_fb = wind component parallel to left/right ventilation path
    '''
    # windspd_lr is the wind component parallel to left/right cross ventilation path:
    # * positive = left to right
    # * negative = right to left
    windspd_lr = windspd * cos((faspect + 90) - winddir)

    # windspd_fb is the wind component parallel to front/back cross ventilation path:
    # * positive = front to back
    # * negative = back to front
    windspd_fb = windspd * (-1 * cos(winddir - faspect))

    return windspd_lr,windspd_fb


def flow_advection():
    '''
    '''
    print("ok")

def set_wind_flows(faspect,nroom,lr_sequence,fb_sequence,winddir,windspd):
    '''
    Function to assign the advection fluxes across rooms, based on wind forcings.

    inputs:
        faspect = angle of the building front
        nroom = number of rooms in the building
        lr_sequence = sequence of rooms connecting the left/right sides of the building
        fb_sequence = sequence of rooms connecting the front/back sides of the building
        winddir = wind direction
        windspd = wind speed

    returns:
        trans_params = array with the advection fluxes
    '''
    # left/right and front/back wind components
    lr_windspd,fb_windspd = wind_components(faspect,winddir,windspd)

    # calculate advection fluxes with a placeholder function
    lr_fluxadv = 999 #flux_advection(lr_sequence, lr_windspd)
    fb_fluxadv = 999 #flux_advection(fb_sequence, fb_windspd)

    # empty data frame with all values set to zero
    trans_params = pd.DataFrame(index=range(nroom+1), columns=range(nroom+1))
    trans_params.fillna(0, inplace=True)

    # add left/right advection flows to `trans_params` array
    for i in range(len(lr_sequence)-1):
        iroom_trans_orig = lr_sequence[i]
        iroom_trans_dest = lr_sequence[i+1]

        if trans_params.loc[iroom_trans_orig,iroom_trans_dest] == 0:
            if lr_windspd > 0:
                print('left-to-right advection flow:', iroom_trans_orig, '->', iroom_trans_dest, '=', lr_fluxadv)
                trans_params.loc[iroom_trans_dest,iroom_trans_orig] = lr_fluxadv
            elif lr_windspd < 0:
                print('right-to-left advection flow:', iroom_trans_dest, '->', iroom_trans_orig, '=', lr_fluxadv)
                trans_params.loc[iroom_trans_orig,iroom_trans_dest] = -lr_fluxadv # TODO: assuming right-left flux is negative
            else:
                print('\tleft/right cross ventilation does not occur')

    # add front/back advection flows to `trans_params` array
    for j in range(len(fb_sequence)-1):
        iroom_trans_orig = fb_sequence[j]
        iroom_trans_dest = fb_sequence[j+1]
        if trans_params.loc[iroom_trans_orig,iroom_trans_dest] == 0:
            if fb_windspd > 0:
                print('front-to-back advection flow:', iroom_trans_orig, '->', iroom_trans_dest, '=', fb_fluxadv)
                trans_params.loc[iroom_trans_dest,iroom_trans_orig] = fb_fluxadv
            elif fb_windspd < 0:
                print('back-to-front advection flow:', iroom_trans_dest, '->', iroom_trans_orig, '=', fb_fluxadv)
                trans_params.loc[iroom_trans_orig,iroom_trans_dest] = -fb_fluxadv # TODO: assuming back-front flux is negative
            else:
                print('\tfront/back cross ventilation does not occur')

    return trans_params


def set_exchange_flows(info_building,lr_sequence,fb_sequence,trans_params):
    '''
    Function to assign the exchange fluxes between rooms. The exchange fluxes are different
    depending on whether cross-ventilation (i.e. advection) occurs, which is assigned by
    the set_wind_flows() function, and whether there is an opening to outdoors.

    inputs:
        info_building = dataframe describing the connections between rooms (indoor) and with outdoors
        lr_sequence = sequence of rooms connecting the left/right sides of the building
        fb_sequence = sequence of rooms connecting the front/back sides of the building
        trans_params = array with the advection fluxes

    returns:
        trans_params = array with the advection and the exchange fluxes
    '''
    # -----------------------------------------------------------------------------------------------------------
    # Identify type of apertures and assign the correct category (as placeholder for the exchange fluxes)

    # CATEGORY 1: apertures at the borders of rooms through which cross-ventilation occurs
    #             indoor-indoor = YES
    #             indoor-outdoor = YES
    print('* CAT 1 apertures')
    # loop over each all combinations of origin/destination rooms
    for iroom_trans_orig in range(len(trans_params)):
        for iroom_trans_dest in range(len(trans_params)):
            # ignore if the origin and destination rooms are the same
            if iroom_trans_dest != iroom_trans_orig:
                # assign exchange flux only if no advection flux has been assigned
                if (trans_params.loc[iroom_trans_orig,iroom_trans_dest] == 0) and (trans_params.loc[iroom_trans_dest,iroom_trans_orig] == 0):
                    # loop over each room in the building
                    for nr in range(len(info_building)):
                        # pick the origin and destination rooms, ensure there is an opening (ie, oarea>0)
                        if (info_building.loc[nr,'rorig'] == iroom_trans_orig) and (info_building.loc[nr,'rdest'] == iroom_trans_dest) and (info_building.loc[nr,'oarea'] > 0):
                            # -------------------------------------------------------------
                            # aperture belongs to category 1 if the origin room is present in the list of rooms
                            # with cross ventilation (either left/right or front/back)
                            if (info_building.loc[nr,'rorig'] in lr_sequence) or (info_building.loc[nr,'rorig'] in fb_sequence):
                                trans_params.loc[iroom_trans_orig,iroom_trans_dest] = 111
                                trans_params.loc[iroom_trans_dest,iroom_trans_orig] = trans_params.loc[iroom_trans_orig,iroom_trans_dest]
                                print('\t', iroom_trans_orig, '->', iroom_trans_dest)

    # CATEGORY 2: apertures at the borders of rooms through which no cross-ventilation occurs
    #             indoor-indoor = NO
    #             indoor-outdoor = YES
    print('* CAT 2 apertures')
    # loop over each all combinations of origin/destination rooms
    for iroom_trans_orig in range(len(trans_params)):
        for iroom_trans_dest in range(len(trans_params)):
            # ignore if the origin and destination rooms are the same
            if iroom_trans_dest != iroom_trans_orig:
                # assign exchange flux only if no advection flux has been assigned
                if (trans_params.loc[iroom_trans_orig,iroom_trans_dest] == 0) and (trans_params.loc[iroom_trans_dest,iroom_trans_orig] == 0):
                    # loop over each room in the building
                    for nr in range(len(info_building)):
                        # pick the origin and destination rooms, ensure there is an opening (ie, oarea>0)
                        if (info_building.loc[nr,'rorig'] == iroom_trans_orig) and (info_building.loc[nr,'rdest'] == iroom_trans_dest) and (info_building.loc[nr,'oarea'] > 0):
                            # -------------------------------------------------------------
                            # aperture belongs to categories 2-4 if the origin room is not present in the list of rooms
                            # with cross ventilation (either left/right or front/back)
                            if (info_building.loc[nr,'rorig'] not in lr_sequence) or (info_building.loc[nr,'rorig'] not in fb_sequence):
                                # -------------------------------------------------------------
                                # aperture belongs to category 2 if the destination is outdoor
                                if iroom_trans_dest == 0:
                                    trans_params.loc[iroom_trans_orig,iroom_trans_dest] = 222
                                    trans_params.loc[iroom_trans_dest,iroom_trans_orig] = trans_params.loc[iroom_trans_orig,iroom_trans_dest]
                                    print('\t', iroom_trans_orig, '->', iroom_trans_dest)

    # CATEGORY 3: apertures at the borders of rooms through which no cross-ventilation occurs
    #             indoor-indoor = YES, in rooms with outdoor apertures
    #             indoor-outdoor = NO
    print('* CAT 3 apertures')
    # loop over each all combinations of origin/destination rooms
    for iroom_trans_orig in range(len(trans_params)):
        for iroom_trans_dest in range(len(trans_params)):
            # ignore if the origin and destination rooms are the same
            if iroom_trans_dest != iroom_trans_orig:
                # assign exchange flux only if no advection flux has been assigned
                if (trans_params.loc[iroom_trans_orig,iroom_trans_dest] == 0) and (trans_params.loc[iroom_trans_dest,iroom_trans_orig] == 0):
                    # loop over each room in the building
                    for nr in range(len(info_building)):
                        # pick the origin and destination rooms, ensure there is an opening (ie, oarea>0)
                        if (info_building.loc[nr,'rorig'] == iroom_trans_orig) and (info_building.loc[nr,'rdest'] == iroom_trans_dest) and (info_building.loc[nr,'oarea'] > 0):
                            # -------------------------------------------------------------
                            # aperture belongs to categories 2-4 if the origin room is not present in the list of rooms
                            # with cross ventilation (either left/right or front/back)
                            if (info_building.loc[nr,'rorig'] not in lr_sequence) or (info_building.loc[nr,'rorig'] not in fb_sequence):
                                # -------------------------------------------------------------
                                # aperture belongs to categories 3-4 if the destination is indoor
                                if iroom_trans_dest != 0:
                                    # -------------------------------------------------------------
                                    # aperture belongs to category 3 if the origin has an aperture to outdoor
                                    info_room = info_building.loc[info_building['rorig'] == iroom_trans_orig]
                                    if len(info_room.loc[info_room['rdest'] == 0]) != 0:
                                        trans_params.loc[iroom_trans_orig,iroom_trans_dest] = 333
                                        trans_params.loc[iroom_trans_dest,iroom_trans_orig] = trans_params.loc[iroom_trans_orig,iroom_trans_dest]
                                        print('\t', iroom_trans_orig, '->', iroom_trans_dest)

    # CATEGORY 4: apertures at the borders of rooms through which no cross-ventilation occurs
    #             indoor-indoor = YES, in rooms without outdoor apertures
    #             indoor-outdoor = NO
    print('* CAT 4 apertures')
    # loop over each all combinations of origin/destination rooms
    for iroom_trans_orig in range(len(trans_params)):
        for iroom_trans_dest in range(len(trans_params)):
            # ignore if the origin and destination rooms are the same
            if iroom_trans_dest != iroom_trans_orig:
                # assign exchange flux only if no advection flux has been assigned
                if (trans_params.loc[iroom_trans_orig,iroom_trans_dest] == 0) and (trans_params.loc[iroom_trans_dest,iroom_trans_orig] == 0):
                    # loop over each room in the building
                    for nr in range(len(info_building)):
                        # pick the origin and destination rooms, ensure there is an opening (ie, oarea>0)
                        if (info_building.loc[nr,'rorig'] == iroom_trans_orig) and (info_building.loc[nr,'rdest'] == iroom_trans_dest) and (info_building.loc[nr,'oarea'] > 0):
                            # -------------------------------------------------------------
                            # aperture belongs to categories 2-4 if the origin room is not present in the list of rooms
                            # with cross ventilation (either left/right or front/back)
                            if (info_building.loc[nr,'rorig'] not in lr_sequence) or (info_building.loc[nr,'rorig'] not in fb_sequence):
                                # -------------------------------------------------------------
                                # aperture belongs to categories 3-4 if the destination is indoor
                                if iroom_trans_dest != 0:
                                    # -------------------------------------------------------------
                                    # aperture belongs to category 3 if the origin does not have an aperture to outdoor
                                    info_room = info_building.loc[info_building['rorig'] == iroom_trans_orig]
                                    if len(info_room.loc[info_room['rdest'] == 0]) == 0:
                                        trans_params.loc[iroom_trans_orig,iroom_trans_dest] = 444
                                        trans_params.loc[iroom_trans_dest,iroom_trans_orig] = trans_params.loc[iroom_trans_orig,iroom_trans_dest]
                                        print('\t', iroom_trans_orig, '->', iroom_trans_dest)

    return trans_params


def get_trans_vars(all_var_list):
    '''
    Function to obtain a list of indoor species and a list of outdoor species, excluding any other variable
    that cannot be transported across rooms (e.g. reaction rates, surface concentrations, constants, etc...)

    inputs:
        all_var_list = complete list of variables from the restart pickle file

    returns:
        indoor_var_list = list of indoor variables that can be transported
        outdoor_var_list = list of outdoor variables that can be transported
    '''

    # indoor variables that cannot be transported
    in_patterns = [
        re.compile(r'.+SURF$'),  # concentrations on surfaces
        re.compile(r'^J\d+'),    # photolysis rates
        re.compile(r'^YIELD.+'), # yields from materials
        re.compile(r'^AV.+'),    # surface/volume ratios
        re.compile(r'^vd.+'),    # deposition velocities
        re.compile(r'^r\d+')     # reaction rates
    ]

    # outdoor variables
    out_pattern = re.compile(r'.*OUT$')

    # constants, rate coefficients, and other variables
    reserved_list = ['ACRate','cosx','secx','M','temp','H2O','PI','AV','adults','children','O2','N2','H2','saero',
                     'OH_reactivity','OH_production','KDI','K8I','FC9','NC13','NCD','FC12','KMT14','CNO3','KMT05',
                     'F17','K140','KFPAN','KPPNI','K20','KMT06','KCH3O2','K7I','NC14','NCPPN','F3','K10I','KRD',
                     'KR10','NC1','K3I','NC17','K12I','NC4','K14I','K150','K200','F20','KMT16','K160','F19','KR7',
                     'FC2','F16','N19','KR3','KMT20','KHOCL','F13','KC0','KMT04','KRPPN','F9','K130','KMT10','KR19',
                     'KMT02','K4I','KMT01','FC14','KR14','NC7','K170','KBPPN','K190','NC3','K15I','KR15','KCI','FCPPN',
                     'F15','FC4','KR12','KMT17','KR13','K298CH3O2','K80','KMT19','FC15','K90','K17I','NC','K20I','F4',
                     'K4','N20','KNO3AL','KROSEC','KNO3','CCLNO3','K70','F8','KRO2HO2','FC20','K14ISOM1','KMT09','FC16',
                     'FPPN','KROPRIM','F12','K19I','NC8','FCD','KRO2NO3','KMT18','NC12','KMT07','FC3','KRC','F1','FCC',
                     'KR16','CCLHO','KMT13','F10','K100','K40','KCLNO3','FC7','F7','FC','NC10','KR2','FC17','CN2O5','KR4',
                     'FC8','KMT11','KMT15','KAPNO','K1I','KBPAN','NC9','FC19','KMT03','K3','K16I','KR20','KPPN0','F2',
                     'K10','FC1','KR1','KMT08','KAPHO2','KMT12','F14','KR17','FC13','KR8','K2I','K2','FC10','KDEC','KD0',
                     'NC16','K13I','KR9','KN2O5','K30','K1','K9I','KRO2NO','K120','FD','NC2','NC15']

    # create list of indoor and a list of outdoor variables that can be transported
    outdoor_var_list =[]
    indoor_var_list=[]
    for i in all_var_list:
        matched = False
        for j in in_patterns:
            if j.match(i):
                matched = True
                break
            elif i in reserved_list:
                matched = True
                break
        if not matched:
            if out_pattern.match(i):
                outdoor_var_list.append(i)
            else:
                indoor_var_list.append(i)

    return indoor_var_list, outdoor_var_list


def calc_transport(output_main_dir,custom_name,ichem_only,tchem_only,nroom,mrvol,trans_params):
    '''
    Main function to apply transport (advection and exchange fluxes). This function is called
    following each integration (ichem_only) of duration `tchem_only` in the primary loop.

    inputs:
        output_main_dir = main output folder
        custom_name = name of the model run
        ichem_only = index of the chemistry-only integration periods
        tchem_only = duration of the chemistry-only integration periods
        nroom = number of rooms in the building
        mrvol = volume of each room
        trans_params = array with the advection and the exchange fluxes

    returns:
        None
    '''
    # --------------------------------------------------------------------------- #
    # Create a dictionary with the concentrations of each species in each room before transport.
    # This is the final output data from the previous integration step.
    data_before_trans={}
    for iroom in range(0,nroom):
        out_dir = ("%s/%s_%s" % (output_main_dir,'room{:02d}'.format(iroom+1),'c{:04d}'.format(ichem_only-1)))
        with open(("%s/%s" % (out_dir,'restart_data.pickle')),'rb') as handle:
            data_before_trans[iroom]=pickle.load(handle)

    # Make list of vaariables that can be transported (indoor and outdoor).
    all_var_list = list(data_before_trans[0])
    indoor_var_list, outdoor_var_list = get_trans_vars(all_var_list)

    # Create a dictionary for the concentrations of each species in each room after transport.
    # This will be used to initialize the next integration step.
    data_after_trans={k: 0 for k in range(0,nroom)}
    for k in range(nroom):
        data_after_trans[k] = pd.DataFrame(columns=all_var_list)

    # --------------------------------------------------------------------------- #
    # Account for indoor-indoor transport

    # Loop over all rooms from the point of view of the origin of fluxes.
    # N.B.: index 0 of `data_before_trans` and `data_after_trans` refers to room 1,
    #       index 0 of `trans_params` refers to outdoor.
    for iroom_trans_orig in range(0,nroom):

        # Populate `data_after_trans` with the number of molecules of each species before transport.
        # Converting from concentrations (molecules/cm3) to numbers of molecules in room.
        # The room volume (mrvol) is specified in m3.
        data_after_trans[iroom_trans_orig] = data_before_trans[iroom_trans_orig] * (mrvol[iroom_trans_orig] * 1.0E6)

        # Loop over all rooms from the point of view of the destination of fluxes.
        for iroom_trans_dest in range(0,nroom):

            # Only apply fluxes between rooms where `trans_params` prescribes a non-zero (+ve) flux
            # from one room (not outdoors) to a different room (not outdoors)
            if (iroom_trans_dest != iroom_trans_orig) and (trans_params.loc[(iroom_trans_orig+1),(iroom_trans_dest+1)] != 0):

                xx=1e-5 # TODO: remove after implementation of flow functions

                for in_var in indoor_var_list:

                    # Reduce number of molecules of each species in room of ORIGIN after transport
                    # to account for outbound flux.
                    # Fluxes in `trans_params` are specified in m3/s and the time between calls to
                    # the calc_transport() function, i.e. `tchem_only`, is specified in s.
                    data_after_trans[iroom_trans_orig][in_var] = data_after_trans[iroom_trans_orig][in_var] - (trans_params.loc[(iroom_trans_orig+1),(iroom_trans_dest+1)]*xx * tchem_only * 1.0E6 * data_before_trans[iroom_trans_orig][in_var])

                    # Increase number of molecules of each species in room of DESTINATION after transport
                    # to account for inbound flux.
                    # Fluxes in `trans_params` are specified in m3/s and the time between calls to
                    # the calc_transport() function, i.e. `tchem_only`, is specified in s.
                    data_after_trans[iroom_trans_dest][in_var] = data_after_trans[iroom_trans_dest][in_var] + (trans_params.loc[(iroom_trans_orig+1),(iroom_trans_dest+1)]*xx * tchem_only * 1.0E6 * data_before_trans[iroom_trans_orig][in_var])

                    #print('|------->', iroom_trans_orig, iroom_trans_dest, '>>>>>>>>>>', trans_params.loc[(iroom_trans_orig+1),(iroom_trans_dest+1)])
                    #print('|------->', data_before_trans[iroom_trans_orig], data_before_trans[iroom_trans_dest])
                    #print('|------->', data_after_trans[iroom_trans_orig], data_after_trans[iroom_trans_dest])
                    #print('Exchange Flows:', (iroom_trans_orig+1), '--->', (iroom_trans_dest+1), ' = ', trans_params.loc[(iroom_trans_orig+1),(iroom_trans_dest+1)])

    # --------------------------------------------------------------------------- #
    # Account for indoor-outdoor transport

    # Loop over all rooms from the point of view of the origin of fluxes.
    # N.B.: index 0 of `data_before_trans` and `data_after_trans` refers to room 1,
    #       index 0 of `trans_params` refers to outdoor.

    # outdoor to indoor
    for iroom_trans_dest in range(0,nroom):
        if trans_params.loc[(iroom_trans_dest+1),0] != 0:
            
            # Loop over all species for which there outdoor data, i.e. <speciesname>OUT
            for out_var in outdoor_var_list:
                in_var = out_var[:-3] 
                if (in_var in indoor_var_list):
                    # Increase number of molecules of each species in room by the number of molecules coming from outdoors
                    data_after_trans[iroom_trans_dest][in_var] = data_after_trans[iroom_trans_dest][in_var] + (trans_params.loc[(iroom_trans_dest+1),0]*xx * tchem_only * 1.0E6 * data_before_trans[iroom_trans_dest][in_var])

    # indoor to outdoor
    for iroom_trans_orig in range(0,nroom):
        if trans_params.loc[0,(iroom_trans_orig+1)] != 0:
            
            # Loop over all species for which there outdoor data, i.e. <speciesname>OUT
            for out_var in outdoor_var_list:
                in_var = out_var[:-3] 
                if (in_var in indoor_var_list):
                    # Decrease number of molecules of each species in room by the number of molecules going to outdoors
                    data_after_trans[iroom_trans_orig][in_var] = data_after_trans[iroom_trans_orig][in_var] - (trans_params.loc[0,(iroom_trans_orig+1)]*xx * tchem_only * 1.0E6 * data_before_trans[iroom_trans_orig][in_var])

    # ---------------------------------------------------------------------------
    # Output concentrations (molecules/cm3) to a restart file to initialise
    # the next integration step of duration `tchem_only`.

    #Loop over all rooms from the point of view of the origin of fluxes; recall, index 0 of output_data_after_transport refers to room 1
    for iroom_trans_orig in range(0, nroom):

        #Convert numbers of molecules of each species after transport back to concentrations (molecules/cm3), assuming room volume, mrvol, is specified in m3
        data_after_trans[iroom_trans_orig] = data_after_trans[iroom_trans_orig] / (mrvol[iroom_trans_orig]*1.0E6)

        #Overwrite restart_data.pickle file with concentrations following transport
        output_folder = ("%s/%s_%s" % (output_main_dir,'room{:02d}'.format(iroom_trans_orig+1),'c{:04d}'.format(ichem_only-1)))
        with open(("%s/%s" % (output_folder,'restart_data.pickle')),'wb') as handle:
            pickle.dump(data_after_trans[iroom_trans_orig],handle)

    return None
