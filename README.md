# About
Thermal Energy Storage Model for space heating coupled with heat pumps in residential buildings

# Model overview
The TES model is an optimization-based model that minimizes the total heating electricity cost to meet buildings space heating load using a system of thermal energy storage coupled with heat pump.

The TES model can be run for a single building of choice, a range of buildings of choice, or all 400 representative buildings in any of the 12 major US cities across different climates included in the study (detailed below).

# Running model
Run model from dashboard.py. Main options to choose from:
| Option | Description |
| --- | --- |
| `super_comp` | `0` if run locally, `1` if run on supercomputer|
| `city` | Options: *Atlanta, Detroit, Los Angeles, Minneapolis, New York, Orlando, Phoenix, Seattle* |
| `single_building` | `True` if run only **one** single building, specify building number next |
| `building_no` | Specify building number to run. Options:  `1` to  `400` |
| `building_range` | `True` if run a **range** of individual buildings, specify building range next|
| `first_building`,`last_building`  | Specify building range to run. Options:  `1` to  `400`|
| `pricing` | `Fixed` to apply fixed utility rate, `ToD` to apply time-of-day rate|
| `include_TES` | `True` to couple TES with ASHP, `False` to exclude TES (only ASHP to provide load)|
| `tes_material` | Four different salt hydrates `MgSO4`, `MgCl2`, `K2CO3`, and `SrBr2`|
| `tes_sizing` | How TES is size, `Varied` if sized based on peak load, `Fixed` if assumed one size (150 kg of salt) |

# Available city options to run up to date
* Detroit
* LA
* NYC
* Orlando
* Minneapolis
* Atlanta
* Seattle
* Phoenix

# Cities soon to be available
* Boston
* Denver
* Chicago
* Dallas

# Model outputs for each building
* Hourly operations of TES (charging/output to shift load, discharging, SOC). 
* Hourly charing and discharging power ratings of TES.
* Hourly operation of ASHP (output to TES, output to serve load).
* Hourly purchase of electricity from utilities to power ASHP.
* TES sizes based on specified sizing methods and TES materials.
* Total system cost.
