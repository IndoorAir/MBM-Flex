```
_  _ ___  _  _    ____ _    ____ _  _
|\/| |__] |\/| __ |___ |    |___  \/
|  | |__] |  |    |    |___ |___ _/\_
```

[![license](https://img.shields.io/github/license/IndoorAir/MBM-Flex?color=green)](https://github.com/IndoorAir/MBM-Flex/blob/master/LICENSE) [![release](https://img.shields.io/github/v/release/IndoorAir/MBM-Flex?color=orange)](https://github.com/IndoorAir/MBM-Flex/releases)

MBM-Flex (MultiBox-Flexible Model) is an indoor air quality model. It was developed as part of the [Clean Air Programme]{https://www.ukcleanair.org/} with the aim to provide a flexible tool to simulate and study indoor air quality and its health impacts.

MBM-Flex is available under the open source license **GPL v3**, which can be found in the `LICENSE` file.

## Model description

MBM-Flex is built upon the [INCHEM-Py](https://github.com/DrDaveShaw/INCHEM-Py) indoor chemical box-model, with a few modifications. described below. Version 1.2 of INCHEM-Py [Shaw et al., Geosci. Model Dev., 2023](https://doi.org/10.5194/gmd-16-7411-2023).

- MCM subsets and other chemical mechanisms

- HONO parametrization

- multiple rooms

## Model installation and configuration

Most of the parameters and variables are the same as INCHEM-Py: details can be found in its manual, a copy of which is in the `docs/` directory (`INCHEMPY_v1_2_manual.pdf`)

- settings_init.py

- room configuration in config_rooms directory

## Model output and analysis

The model can be run in serial or in parallel mode

The results are stored in a directory and can be extracted with the MBM_extractor.py script

Plotting scripts and other scripts to estimate human exposure are in model_tools
