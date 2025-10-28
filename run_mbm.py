import math
import pickle
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.simulation import Simulation
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file
)
from multiroom_model.aperture_factory import (
    build_apertures,
    build_apertures_from_double_definition,
    build_wind_definition
)

# Define some global settings which are true for the whole building
if __name__ == '__main__':

    ambient_press = 1013.0   # ambient pressure (mbar) is assumed to be constant, and is the same in all rooms
    ambient_temp = 293.0     # ambient temperature (K) is assumed to be constant
    # ambient air density (assuming dry air), in kg/m3
    rho = (100*ambient_press) / (287.050 * ambient_temp)


    global_settings = GlobalSettings(
        filename='chem_mech/mcm_subset.fac',
        INCHEM_additional=False,
        particles=True,
        constrained_file=None,
        output_folder=None,
        dt=1,
        H2O2_dep=False,
        O3_dep=False,
        custom=False,
        custom_filename=None,
        diurnal=True,
        city='London_urban',
        date='21-06-2020',
        lat=45.4,
        path=None,
        reactions_output=False,
        building_direction_in_radians=math.radians(180),
        air_density=rho,
        upwind_pressure_coefficient=0.3,
        downwind_pressure_coefficient=-0.2
    )

    # Construct the rooms
    # This is using the CSV file, but other methods could be employed

    rooms_dictionary = build_rooms("config_rooms/mr_tcon_room_params.csv")

    # Populate each of the rooms with additional information from supplementary csv files

    for i, room in rooms_dictionary.items():
        populate_room_with_emissions_file(room, f"config_rooms/mr_room_emis_params_{i}.csv")
        populate_room_with_tvar_file(room, f"config_rooms/mr_tvar_room_params_{i}.csv")
        populate_room_with_expos_file(room, f"config_rooms/mr_tvar_expos_params_{i}.csv")

    # Populate the apertures,
    # uses the "double definition" method because we expect each aperture will appear twice in the csv file.
    apertures = build_apertures_from_double_definition("config_rooms/mr_tcon_building.csv", rooms_dictionary)

    # Populate the definition of the wind
    wind_definition = build_wind_definition("config_rooms/mr_tvar_wind_params.csv", in_radians=False)

    # We dont need the keys of the rooms anymore now we have populated them
    rooms = list(rooms_dictionary.values())


    # Build the simulation class
    # This step will build jacobeans for each of the rooms in preparation for running later
    simulation = Simulation(
        global_settings=global_settings,
        rooms=rooms,
        apertures=apertures,
        wind_definition=wind_definition,
        processes=5)

    # Select an initial conditions text file for each room
    # This lines uses the same file for all the rooms, but this could be different for the different rooms
    initial_conditions = dict((r, 'initial_concentrations.txt') for r in rooms)

    # Run the simulation starting at t=0, for 25 seconds,
    # interrupt the inchempy solver to apply the effects of windows every 6 seconds
    result = simulation.run(
        t0=0,
        t_total=20,
        t_interval=6,
        init_conditions=initial_conditions
    )

    # Save to pickle file

    results_as_dictionary = dict((f"Room {i+1}", result[r]) for i, r in enumerate(rooms))

    pickle.dump(results_as_dictionary, open("./results.pkl", "wb"))

    # Make use of results here eg
    # plot tool

    # Demo: Print one of the many results to the output
    room_of_interest = rooms_dictionary[1]
    species_of_interest = "CO"
    time_of_interest = 9

    print(f"\n\nCO concentration in room 1 after 9 seconds = {result[room_of_interest][species_of_interest][time_of_interest]}")
