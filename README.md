```
_  _ ___  _  _    ____ _    ____ _  _
|\/| |__] |\/| __ |___ |    |___  \/
|  | |__] |  |    |    |___ |___ _/\_
```

[![license](https://img.shields.io/github/license/IndoorAir/MBM-Flex?color=green)](https://github.com/IndoorAir/MBM-Flex/blob/master/LICENSE) [![release](https://img.shields.io/github/v/release/IndoorAir/MBM-Flex?color=orange)](https://github.com/IndoorAir/MBM-Flex/releases)

**MBM-Flex** (MultiBox-Flexible Model) is an indoor air quality model. It was developed as part of the **IAQ-EMS** project, a component of the [UK Clean Air Programme](https://www.ukcleanair.org/). The aim of MBM-Flex is to provide the community with a flexible tool to simulate and investigate indoor air quality and its health impacts.

MBM-Flex is available under the open source license **GPL v3**, which can be found in the `LICENSE` file.

## Model description

MBM-Flex is built upon the [INCHEM-Py](https://github.com/DrDaveShaw/INCHEM-Py/) indoor chemical box-model. INCHEM-Py is designed to simulate air quality inside a single room, while MBM-Flex is designed to simulate air quality inside a number of interconnected rooms or an entire building. To do so, MBM-Flex runs a separate instance of a modified version of INCHEM-Py for each room, and connects each instance with an *ad-hoc* implementation of inter-room transport.

**INCHEM-Py v1.2**, described in [Shaw et al., Geosci. Model Dev., 2023](https://doi.org/10.5194/gmd-16-7411-2023), is the basis of MBM-Flex. The main differences between the original INCHEM-Py codebase and the version used in MBM-Flex are:

- Chemical mechanisms of different complexity. The chemical mechanism used by INCHEM-Py is the full [MCM v3.3.1](https://mcm.york.ac.uk/MCM/), which includes the gas-phase oxidation of methane and 142 non-methane hydrocarbons. MBM-Flex allows the user to choose any subset of the full MCM, as well as the two reduced chemical mechanisms developed for the IAQ-EMS project (`rcs_2023.fac` and `escs_v1.fac`). The chemical mechanism filess (in `.fac` format) are stored in the `chem_mech/` directory.

- Humidity-dependent parametrization of HONO formation via reaction of NO2 on surfaces based on [Mendez et al., Indoor Air, 2016](https://doi.org/10.1111/ina.12320).

- Time-variable relative humidity, number and body surface area of adults and children (defined as less than 10 years old), ambient wind speed and direction. Number density of air calculated from pressure and temperature. These parameters are constant in the original INCHEM-Py.

- Surface materials provided as a percentage of the total room surface (instead of square metres).

- Outdoor-indoor exchange rate (`ACRate`) redefined to account for multiple rooms and for the implementation of inter-room convective transport.

## Model installation, configuration, and execution

MBM-Flex has the same requirements as INCHEM-Py (see `inchem_docs/README.md`). To install MBM-Flex, download the latest release of the model at https://github.com/IndoorAir/MBM-Flex/releases and unpack the archive file in a directory of choice. The model can be configured and run using the **Spyder IDE** (part of the [Anaconda](https://www.anaconda.com/) platform). Alternatively, a text editor and a Python installation with all the required packages (listed in `inchem_docs/README.md`) can be used.

Most of the parameters that the user needs to set in order to run the MBM-Flex model are the same as for INCHEM-Py, and are described in the INCHEM-Py manual (`inchem_docs/INCHEMPY_v1_2_manual.pdf`). However, the user-set variables are defined in the initialization file `settings_init.py` (instead of `settings.py` used in INCHEM-Py). The `settings_init.py` file is self-documented: it includes detailed description of each parameter, together with information on the possible values it can have and the corresponding measurement unit.

Additionally, MBM-Flex requires a description of the building's location and rooms, as well as their connections to each other and to the outdoor. This information must be provided by the user via the `.csv` files stored in the `config_rooms/` directory:

- `mr_tcon_room_params.csv`: room number, volume (m3), total surface area (m2), light and glass type (see INCHEM-Py manual for details), surface materials (%). One room for each line of the file.

- `mr_tcon_building.csv`: openings bween each room and the other rooms, and with the outdoor. The rooms are identified by a number, and the area of each opening is in m2. It must be specified on which side of the building (relative to the *facade* or front side) are the openings between a room and the outdoor.

- `mr_room_emis_params_*.csv`: hourly emission rates of chemical species (molecule cm-3 s-1). One chemical species for each line of the file; one file for each room, identified by the room number.

- `mr_tvar_room_params_*.csv`: hourly temperature (K), relative humidity (%), indoor-outdoor exchange (s-1), light_switch (on/off). One file for each room, identified by the room number.

- `mr_tvar_expos_params_*.csv`: hourly occupancy, i.e. number of adults and of children. One file for each room, identified by the room number.

- `mr_tvar_wind_params.csv`: hourly wind speed (m/s) and direction (deg N).

The format of the `.csv` files can be inferred by the example files stored in the `config_rooms/` directory. After these files have been created and the `settings_init.py` file has been modified, the model is ready to be run.

MBM-Flex can be executed in serial or parallel mode, via the corresponding script: `run_mbm_serial.py` or `run_mbm_parallel.py`. The choice between the two modes depends on the user's preferences and available computing resources. There is no difference in the model results, only in the time needed to complete the model run.

MBM-Flex can also be run on high performance computing systems (HPC): these usually require a submission script which is different depending on the type of job scheduler used on the HPC. Submission scripts for the [UoB BlueBEAR](https://www.birmingham.ac.uk/research/arc/bear/) supercomputer, which uses the **Slurm** workload manager, are provided in the `hpc_scripts/` directory. For other HPC systems the user should refer to the local documentation.

## Model output and analysis

The results of the model run are stored in the main output directory, which is automatically created by MBM-Flex at runtime with the following name: `yyyymmdd_hhmmss_<custom_name>`, where `custom_name` is a variable set by the user in the `settings_init.py` file. This directory contains a number of subdirectories (one for each room for each model timestep) which contain the model output as a `.pickle` file (see INCHEM-Py manual for more information on the output files).

In order to obtain the results of the whole model run, the individual subdirectory must be collated, which is done via the `MBM_extractor.py` script. The user must edit the script to specify the main output directory (`yyyymmdd_hhmmss_<custom_name>`), the duration of the model run, and the list of desired model variables. The script generates a number of `.csv` files in the `extracted_outputs/` subdirectory, within the main output directory: one `.csv` file for each room, plus one `.csv` file for the outdoor.

The directory `model_tools/` contains basic scripts for plotting and analyzing the model results. The scripts are written in R, and require the `ggplot2` and `scales` R packages.

- `MBM_plots.R`: a plotting script for a quick overview of the model results.

- `MBM_metrics.R`: a script to calculate exposure metrics from the model results (e.g. mean/maximum concentrations, exceedance of the [WHO air quality guidelines](https://www.who.int/publications/i/item/9789240034228), etc...).


It is suggested to import the extracted `.csv` files into a data analysis software for further analysis and visualization of the model results.
