# ############################################################################ #
#
# Copyright (c) 2025 Roberto Sommariva, Neil Butcher, Adrian Garcia,
# James Levine, Christian Pfrang.
#
# This file is part of MBM-Flex.
#
# MBM-Flex is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License (https://www.gnu.org/licenses) as
# published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# A copy of the GPLv3 license can be found in the file `LICENSE` at the root of
# the MBM-Flex project.
#
# ############################################################################ #

from typing import List, Tuple, Dict, Any
import re
from .aperture_calculations import Fluxes
import pandas as pd


class ApertureFlowCalculator:
    """
        @brief A class used to deduce absolute changes to concentrations, caused by a flux through an aperture
        It knows which species to transport, either between rooms or to the outside
        It uses the rooms volumes and current concentrations to deduce the absolute concentration changes

    """
    indoor_var_list: List[str]
    outdoor_var_list: List[str]

    def __init__(self, all_var_list):
        self.indoor_var_list, self.outdoor_var_list = self.get_trans_vars(all_var_list)

    def concentration_changes(self, flux: Fluxes,
                              delta_time: float,
                              room_1_concentrations: pd.Series,
                              room_2_concentrations: pd.Series,
                              room_1_volume: float,
                              room_2_volume: float) -> Tuple[pd.Series, pd.Series]:
        '''
        Deduce the absolute changes in concentrations, caused by the flux arising from an aperture between 2 rooms

        inputs:
            flux = The flux through the aperture, calculated in aperture_calculations
            delta_time = The interval of time being considered
            room_1_concentrations = the starting concentration of room 1
            room_2_concentrations = the starting concentration of room 2
            room_1_volume = the volume of room 1
            room_2_volume = the volume of room 2

        returns:
            results = concentration_change_in_room_1, concentration_change_in_room_2
        '''
        # deduce the absolute airflow over the time interval
        flow_from_1_to_2 = flux.from_1_to_2*delta_time
        flow_from_2_to_1 = flux.from_2_to_1*delta_time

        # The absolute quantity moved in this interval
        quantities_moved_from_1_to_2 = flow_from_1_to_2 * room_1_concentrations.loc[self.indoor_var_list]
        quantities_moved_from_2_to_1 = flow_from_2_to_1 * room_2_concentrations.loc[self.indoor_var_list]

        # the concentration change, coming from the absolute entry, absolute exit, and volume
        concentration_change_in_room_1 = (quantities_moved_from_2_to_1-quantities_moved_from_1_to_2)/room_1_volume
        concentration_change_in_room_2 = (quantities_moved_from_1_to_2-quantities_moved_from_2_to_1)/room_2_volume

        return concentration_change_in_room_1, concentration_change_in_room_2

    def outdoor_concentration_changes(self, flux: Fluxes,
                                      delta_time: float,
                                      room_1_concentrations: pd.Series,
                                      room_1_volume: float) -> pd.Series:
        '''
        Deduce the absolute changes in concentrations,
        caused by the flux arising from an aperture from a room to its outside

        inputs:
            flux = The flux through the aperture, calculated in aperture_calculations
            delta_time = The interval of time being considered
            room_1_concentrations = the starting concentration of room 1
            room_1_volume = the volume of room 1

        returns:
            results = concentration_change_in_room_1
        '''

        # deduce the absolute airflow over the time interval
        flow_from_1_to_2 = flux.from_1_to_2*delta_time
        flow_from_2_to_1 = flux.from_2_to_1*delta_time

        # The absolute quantity exiting in this interval
        quantities_moved_from_1_to_2 = flow_from_1_to_2 * room_1_concentrations.loc[self.indoor_var_list]

        # The species to consider coming from the outside - restrict species to those defined outside this room
        outdoor_concentrations = pd.Series()
        for outdoor_var in self.outdoor_var_list:
            var_without_OUT = outdoor_var[:-3]
            if (var_without_OUT in room_1_concentrations.keys()):
                outdoor_concentrations.loc[var_without_OUT] = room_1_concentrations.loc[outdoor_var]

        # The absolute quantity entering in this interval
        quantities_moved_from_2_to_1 = flow_from_2_to_1 * outdoor_concentrations

        # fill any blanks with 0s so summing the 2 sets doesn't give any nans
        common_index = quantities_moved_from_1_to_2.index.union(quantities_moved_from_2_to_1.index)
        q1to2_filled = quantities_moved_from_1_to_2.reindex(common_index, fill_value=0)
        q2to1_filled = quantities_moved_from_2_to_1.reindex(common_index, fill_value=0)

        # the concentration change, coming from the absolute entry, absolute exit, and volume
        concentration_change_in_room_1 = (q2to1_filled-q1to2_filled)/room_1_volume

        return concentration_change_in_room_1

    @staticmethod
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
            re.compile(r'^YIELD.+'),  # yields from materials
            re.compile(r'^AV.+'),    # surface/volume ratios
            re.compile(r'^vd.+'),    # deposition velocities
            re.compile(r'^r\d+')     # reaction rates
        ]

        # outdoor variables
        out_pattern = re.compile(r'.*OUT$')

        # constants, rate coefficients, and other variables
        reserved_list = ['ACRate', 'cosx', 'secx', 'M', 'temp', 'H2O', 'PI', 'AV', 'adults', 'children', 'O2', 'N2', 'H2', 'saero',
                         'OH_reactivity', 'OH_production', 'KDI', 'K8I', 'FC9', 'NC13', 'NCD', 'FC12', 'KMT14', 'CNO3', 'KMT05',
                         'F17', 'K140', 'KFPAN', 'KPPNI', 'K20', 'KMT06', 'KCH3O2', 'K7I', 'NC14', 'NCPPN', 'F3', 'K10I', 'KRD',
                         'KR10', 'NC1', 'K3I', 'NC17', 'K12I', 'NC4', 'K14I', 'K150', 'K200', 'F20', 'KMT16', 'K160', 'F19', 'KR7',
                         'FC2', 'F16', 'N19', 'KR3', 'KMT20', 'KHOCL', 'F13', 'KC0', 'KMT04', 'KRPPN', 'F9', 'K130', 'KMT10', 'KR19',
                         'KMT02', 'K4I', 'KMT01', 'FC14', 'KR14', 'NC7', 'K170', 'KBPPN', 'K190', 'NC3', 'K15I', 'KR15', 'KCI', 'FCPPN',
                         'F15', 'FC4', 'KR12', 'KMT17', 'KR13', 'K298CH3O2', 'K80', 'KMT19', 'FC15', 'K90', 'K17I', 'NC', 'K20I', 'F4',
                         'K4', 'N20', 'KNO3AL', 'KROSEC', 'KNO3', 'CCLNO3', 'K70', 'F8', 'KRO2HO2', 'FC20', 'K14ISOM1', 'KMT09', 'FC16',
                         'FPPN', 'KROPRIM', 'F12', 'K19I', 'NC8', 'FCD', 'KRO2NO3', 'KMT18', 'NC12', 'KMT07', 'FC3', 'KRC', 'F1', 'FCC',
                         'KR16', 'CCLHO', 'KMT13', 'F10', 'K100', 'K40', 'KCLNO3', 'FC7', 'F7', 'FC', 'NC10', 'KR2', 'FC17', 'CN2O5', 'KR4',
                         'FC8', 'KMT11', 'KMT15', 'KAPNO', 'K1I', 'KBPAN', 'NC9', 'FC19', 'KMT03', 'K3', 'K16I', 'KR20', 'KPPN0', 'F2',
                         'K10', 'FC1', 'KR1', 'KMT08', 'KAPHO2', 'KMT12', 'F14', 'KR17', 'FC13', 'KR8', 'K2I', 'K2', 'FC10', 'KDEC', 'KD0',
                         'NC16', 'K13I', 'KR9', 'KN2O5', 'K30', 'K1', 'K9I', 'KRO2NO', 'K120', 'FD', 'NC2', 'NC15']

        # create list of indoor and a list of outdoor variables that can be transported
        outdoor_var_list = []
        indoor_var_list = []
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
