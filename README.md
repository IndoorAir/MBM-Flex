```
_  _ ___  _  _    ____ _    ____ _  _
|\/| |__] |\/| __ |___ |    |___  \/
|  | |__] |  |    |    |___ |___ _/\_
```

[![license](https://img.shields.io/github/license/IndoorAir/MBM-Flex?color=green)](https://github.com/IndoorAir/MBM-Flex/blob/master/LICENSE) [![release](https://img.shields.io/github/v/release/IndoorAir/MBM-Flex?color=orange&include_prereleases)](https://github.com/IndoorAir/MBM-Flex/releases)

# MBM-Flex

MultiBox-Flexible Model (MBM-Flex) is an indoor air quality model. It was developed as part of the **IAQ-EMS** project, a component of the [UK Clean Air Programme](https://www.ukcleanair.org/). The aim of MBM-Flex is to provide the community with a flexible tool to simulate and investigate indoor air quality and its health impacts.

MBM-Flex is a Python-based multi-room box-model for indoor air chemistry and transport. It integrates chemical mechanisms, configurable room layouts, and simulation runners (CLI and simple UI), and includes tools for extracting and analysing outputs.

## Model description

MBM-Flex is built upon the [INCHEM-Py](https://github.com/DrDaveShaw/INCHEM-Py/) indoor chemical box-model. INCHEM-Py is designed to simulate air quality inside a single room, while MBM-Flex is designed to simulate air quality inside a number of interconnected rooms or an entire building.

To do so, MBM-Flex runs separate instances of INCHEM-Py for each per-room chemistry in piecewise time intervals. Between intervals it both adjusts the properties of a room which would otherwise be fixed; and interconnects the instances with an implementation of inter-room transport.

## Quick Start

**Prerequisites:** Python 3.8+ and pip.

**Install dependencies:**
+ numpy
+ numba
+ pandas
+ tqdm
+ scipy
+ threadpoolctl
+ matplotlib
+ multiprocess
+ json5

**Acquire inchempy**

Initially the `inchempy/` folder is empty. A complete version of [INCHEM-Py](https://github.com/DrDaveShaw/INCHEM-Py/) needs to be downloaded and copied into this folder.

As of January 26, the only commit of INCHEM-Py guaranteed to work is [INCHEM-Py Commit 116cb71](https://github.com/DrDaveShaw/INCHEM-Py/tree/116cb71562b32baaa86c58f9c090d94491a4fa41) . The mainline of INCHEM-Py **does not work**.
This is due to its management of memory. We hope future versions of INCHEM-Py will become compatible.
You can download this precise version [here](https://github.com/DrDaveShaw/INCHEM-Py/archive/116cb71562b32baaa86c58f9c090d94491a4fa41.zip).

**Run a sample simulation:**

```bash
# Basic run (runs the building configuration defined in the config_rooms/ folder)
python run_mbm.py
```
This will run the example simulation defined in the `config_rooms/` folder.
It produces a pkl binary file with the results contained and dataframes for the different rooms.

**Extract results / post-process:**

```bash
python MBM_extractor.py
```
This will extract the pkl file you have generated into plots & csv files of subsets of the results.

**Optional - Run the simple UI:**

```bash
python run_mbm_ui.py
```
Here you can assemble the skeleton of a building and populate default configuration files.
You can also view results after running a simulation.

**Optional - Run test suite:**

```bash
pip install pytest
python -m pytest multiroom_model_tests
```

This suite runs many unit tests of the chemistry and could take many minutes.

## Main python scripts to act as Entry Points

- **`run_mbm.py`**: Primary CLI runner for simulations.
- **`MBM_extractor.py`**: Tools to extract and summarise simulation outputs.
- **`model_tools/`**: R scripts and plotting utilities for downstream analysis.
- **`run_mbm_ui.py`**: Starts the simple UI front-end (see `UI/`).

## Configuring the simulation

All settings are defined or referenced in `run_mbm.py`.
You can edit this file to change global settings.
You can select a different building configuration by changing the line
`input_data = BuildingJSONParser.from_json_file("config_rooms/building.json")`
.

Alternatively you can change the building configuration **in place** by editing the JSON files in `config_rooms/`.

- [config_rooms/building.json](config_rooms/building.json)
- [config_rooms/room_1.json](config_rooms/room_1.json)

You can get assistance to generate and edit json configuration files using the [UI](#layout-design-graphical-interface).

The configuration files reference initial concentrations from files such as [config_chem/initial_concentrations.txt](config_chem/initial_concentrations.txt).

**Overview of `config_rooms` JSON files**

The `config_rooms/` folder contains two JSON schemes: a building-level file that references room files, and per-room files with physical and schedule parameters. Times are given in seconds from simulation start.

- Building-level (`config_rooms/building.json`):
	- `rooms`: mapping of room name → room JSON path (e.g., "room 1": "config_rooms/room_1.json").
	- `wind`: object with `values` (array of `{time, speed, direction}`) and an `in_radians` boolean.
	- `apertures`: list of aperture descriptors `{origin, destination, area}` that connect rooms or external faces.
	- `initial_conditions`: mapping of room name → initial concentrations file path.
	- Example: [config_rooms/building.json](config_rooms/building.json)

- Room-level (`config_rooms/room_*.json`) common fields:
	- `volume_in_m3`: room air volume.
	- `surf_area_in_m2`: total surface area for deposition/uptake calculations.
	- `light_type`, `glass_type`: descriptive strings controlling photolysis/lighting settings.
	- `composition`: object listing surface-material percentages (e.g., `paint`, `wood`, `metal`, ...) that sum to ~100.
	- `temp_in_kelvin`, `rh_in_percent`, `airchange_in_per_second`: each uses an array of `[time, value]` pairs describing piecewise schedules.
	- `light_switch`: schedule of on/off values as  `[time, value]` pairs.
	- `emissions`: mapping species → emission schedule. Each species entry contains a `values` array; values may be bracketed segments: `{start, end, value}` describing emission bursts.
	- `n_adults`, `n_children`: occupancy schedules in `[time, value]` arrays.

For a description of any of the parameters local to a single room see the [INCHEM-Py](https://github.com/DrDaveShaw/INCHEM-Py/) documentation.

**Chemical Mechanism `fac` files**

Chemical mechanism files (FAC format) live in `chem_mech/`; one is selected in the global settings of `run_mbm.py`.
Example files:

- [chem_mech/mcm_v331.fac](chem_mech/mcm_v331.fac)

These are used by the chemistry modules  of inchempy for building reaction systems.
For details about `fac` files see the [INCHEM-Py](https://github.com/DrDaveShaw/INCHEM-Py/) documentation.


## Layout design graphical interface


The layout editor allows you to visually design a multi-room building system by creating rooms, defining apertures between them, and reviewing how air transport flows through your layout.

When you first open the editor, you'll see a blank canvas on the left and a toolbar at the top. The interface allows you to create rooms, connect them, and then request the backend to compute transport paths through your design.

#### Creating Rooms

To add a new room to your layout, click the "Add Room" button in the toolbar. A new room will appear on the canvas with a default name like "Room 1". You can drag the room anywhere on the canvas to position it, and resize it by dragging the corner. Double clicking on the name allows the name to be changed

Each room has editable properties displayed in the JSON editor panel on the right side of the screen. Click on a room to select it and see its JSON data. You can modify the room's properties directly in the JSON editor, such as changing its name or adding custom properties.

#### Creating Apertures

Apertures represent openings between rooms or between a room and the outside. To create an aperture, click the "Link Mode" button in the toolbar to enter linking mode. The interface will show a banner indicating that you're ready to create connections.

In link mode, you can create connections in two ways:

1. **Between two rooms**: Select two rooms by clicking on them. An aperture will automatically be created between the selected rooms.

2. **Between a room and the outside**: Select a single room and then click on one of the four directional buttons (Front, Back, Left, Right) to create an opening on that side of the room.

Each aperture can be edited to set its area. Click on an aperture to select it and modify its properties in the JSON editor.

#### Viewing Transport Paths

Once you've created your room layout with apertures, you can request the backend to calculate transport paths through your system. Click the "Transport Paths" button to analyse how air flows through the connections you've defined.


#### Saving and Loading Your Layouts

Your work can be saved for later use. Click the "Save Layout" button to export your design. The system will save individual JSON files for each room as well as a master layout file containing the overall structure and aperture connections.
The saved json files can act as the start of your configuration for running.

To restore a previous design, click the "Load Layout" button and select your saved layout file. The editor will reconstruct your entire room configuration, apertures, and positioning, allowing you to continue editing where you left off.

#### Viewing Simulation Results

After running simulations in the backend, you can visualize the results directly in the layout editor. Click the "View Results" button to load a results file (pickle file) from a completed simulation.

Once loaded, you can select which chemical species to display and choose a specific time point from your simulation. The rooms in your layout will be coloured according to the concentration levels of the selected species at that time, providing an instant visual representation of how pollutants or other chemicals distribute through your building over time. You can switch between different species and time points to explore various aspects of your simulation results.




## Project Structure

- **`multiroom_model/`**: Core model classes and simulation engine (room definitions, transport, evolvers).
- **`chem_mech/`**: Chemical mechanism files (FAC format) used by the chemistry engine.
- **`inchempy/`**: This is an empty folder; choose a (compatible) version of inchempy and paste it here before running.
- **`config_rooms/`**: Building and room JSON configurations (`building.json`, `room_*.json`).
- **`config_chem /`**: Initial concentation files (`initial_concentrations.txt`).
- **`model_tools/`**: R scripts and plotting utilities for downstream analysis.


## License

MBM-Flex is available under the open source license **GPL v3**, which can be found in the `LICENSE` file.

This project includes a `LICENSE` file at the repository root. See [LICENSE](LICENSE) for terms.


## Overview of Key Classes and workings in `multiroom_model`

Below is a brief map of the principal classes you will encounter in `multiroom_model` and what they do. Refer to the source files for fuller docstrings and method details.

- `Simulation`: Coordinates the overall simulation (time loop, per-timestep updates, I/O) and advances species states across rooms and apertures.
- `GlobalSettings`: Stores simulation-wide defaults and global parameters used by the simulation and JSON builders.
- `RoomChemistry`: Holds chemistry-related options for a single room (mechanism selection, photolysis configuration, emissions).
- `InChemPyInstance` / `RoomInchemPyEvolver`: Encapsulate settings and factory methods to build and run InChemPy simulations (parsing FAC files, setting time steps, generating chemistry results).
- `Aperture`: Represents a connection between two rooms and stores properties used for flow calculations.
- `ApertureCalculation`, `ApertureFlowCalculator`, `Fluxes`: Compute advection and exchange flows through apertures and translate those into concentration fluxes between rooms.
- `TransportPath`: Models composite routes through multiple apertures along which continuous wind can flow.
- `WindDefinition`: The speed and direction of the wind changing over time.
- JSON builder/parsers: `BuildingJSONParser`, `ApertureJSONBuilder`, `RoomChemistryJSONBuilder`, `WindJsonBuilder`, and `GlobalSettingsJSONBuilder` — these parse the JSON configuration files in `config_rooms/` and construct the corresponding model objects.

Use these classes as starting points when extending or instrumenting the model; most heavy lifting is done in `simulation.py`, the evolver classes, and the aperture/flow calculators.
