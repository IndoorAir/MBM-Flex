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


class GlobalSettings:
    """
         @brief Stores data needed for inchempy which does not differ between the rooms
    """
    def __init__(
        self,
        filename: str = 'chem_mech/mcm_subset.fac',
        INCHEM_additional: bool = False,
        particles: bool = False,
        constrained_file: str = None,
        output_folder: str = None,
        dt: float = 0.002,
        H2O2_dep: bool = False,
        O3_dep: bool = False,
        custom: bool = False,
        custom_filename: str = None,
        diurnal: bool = False,
        city: str = 'London_urban',
        date: str = '21-06-2020',
        lat: float = 45.4,
        path: str = None,
        reactions_output: bool = False,
        building_direction_in_radians: float = 0.0,
        air_density: float = 0.0,
        upwind_pressure_coefficient: float = 0.3,
        downwind_pressure_coefficient: float = -0.2
    ):
        """
        @param filename: Input FACSIMILE format filename.
        @param particles: Boolean flag to include particle modeling.
        @param INCHEM_additional: Include additional INCHEM reactions not in the MCM download.
        @param custom: Include custom reactions.
        @param custom_filename: Filename for custom reaction input.
        @param diurnal: Enable diurnal variation of outdoor concentrations.
        @param city: City for outdoor concentration profiles.
        @param date: Simulation date in format "DD-MM-YYYY".
        @param lat: Latitude of the simulation location.
        @param H2O2_dep: Enable surface deposition for H2O2.
        @param O3_dep: Enable surface deposition for O3.
        @param constrained_file: CSV file to constrain species or rates over time.
        @param dt: Time step for integration (seconds).
        @param reactions_output: Save detailed reaction rates and constants.
        @param building_direction_in_radians: Orientation of the building to determine wind components.
        @param air_density: Density of the air for advection flow calculations.
        @param upwind_pressure_coefficient: for advection flow calculations.
        @param downwind_pressure_coefficient: for advection flow calculations.
    """
        self.filename = filename
        self.INCHEM_additional = INCHEM_additional
        self.particles = particles
        self.constrained_file = constrained_file
        self.output_folder = output_folder
        self.dt = dt
        self.H2O2_dep = H2O2_dep
        self.O3_dep = O3_dep
        self.custom = custom
        self.custom_filename = custom_filename
        self.diurnal = diurnal
        self.city = city
        self.date = date
        self.lat = lat
        self.path = path
        self.reactions_output = reactions_output
        self.building_direction_in_radians = building_direction_in_radians
        self.air_density = air_density
        self.upwind_pressure_coefficient = upwind_pressure_coefficient
        self.downwind_pressure_coefficient = downwind_pressure_coefficient
