# About
Thermal Energy Storage Model for space heating coupled with air-source heat pumps in residential homes in U.S. Cities across different climates.

# Model overview
The TES model is an optimization-based model that minimizes the total space heating electricity cost to satisfy buildings space heating load using a system of thermal energy storage coupled with air-source heat pump.

The TES model can be run for a single building of choice, a range of buildings of choice, or all 400 representative buildings in any of the 12 major US cities across different climates included in the study (details below).

![image (1)](https://user-images.githubusercontent.com/56058936/223792219-ca237aac-603c-4dc8-abdb-2a7117e20d3d.png)

# Programming language
The TES model is programmed in Pyomo/Python and solved using CPLEX.

# Running model
Run model from dashboard.py. Main options to choose from:
| Option | Description |
| --- | --- |
| `super_comp` | `False` if run locally, `True` if run on supercomputer|
| `city` | Options: *Atlanta, Boston, Boulder, Chicago, Detroit, Dallas, Los Angeles, Minneapolis, New York, Orlando, Phoenix, Seattle* |
| `single_building` | `True` if run only **one** single building, specify building number next |
| `building_no` | Specify building number to run. Options:  `1` to  `400`. The 400 buildings represent over 90% heating load for a city. Each building has different heating load profile provided in Data folder. |
| `building_range` | `True` if run a **range** of individual buildings, specify building range next|
| `first_building`,`last_building`  | Specify building range to run. Options:  `1` to  `400`|
| `pricing` | `Fixed` to apply fixed utility rate, `ToD` to apply time-of-day rate|
| `include_TES` | `True` to couple TES with ASHP, `False` to exclude TES (only ASHP to provide load)|
| `tes_material` | Four different salt hydrates `MgSO4`, `MgCl2`, `K2CO3`, and `SrBr2`|
| `tes_sizing` | How TES is size, `Varied` if sized based on peak load, `Incremental` if sized based on peak load then round up to the next 25 kg ,`Fixed` if assumed one size (150 kg of salt) |
| `const_pr` | `False` if use Ragone plots, `True` if assumed constant power rating|
| `power_rating` | (only eligible if `const_pr`=`True`) `Peak` if setting constant power rating at peak load, `Average` if setting power rating at 100 W per kg, and `Low` if setting power rating at 10 W per kg|

# Model outputs for each building
* ASHP's capacity
* Hourly operations of TES (charging/output to shift load, discharging, SOC). 
* Hourly charging and discharging power ratings of TES.
* Hourly operation of ASHP (output to charge TES, output to serve load).
* Hourly purchase of electricity from utilities to power ASHP.
* TES sizes based on specified sizing methods and TES materials.
* Total system cost.
* TES break-even cost.
* Peak load reduction.
