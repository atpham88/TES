# About
Thermal Energy Storage Model for space heating coupled with heat pumps in residential buildings

# Model Overview
The TES model is an optimization-based model that minimizes the total heating electricity cost to meet buildings space heating load using a system of thermal energy storage coupled with heat pump.

The TES model can be run for a single building of choice or all 400 representative buildings in any of the 16 major US cities included in the study.

# Available city options to run up to date
Detroit

LA

NYC

Orlando

Minneapolis

Atlanta

Seattle

Phoenix

# Cities to add
Boston

Denver

Chicago

Boise

Omaha

Philly

Dallas

Salt Lake City

# Running Model
Run model from dashboard.py.
| Option | Description |
| --- | --- |
| `city` | Options: *Atlanta, Detroit, Los Angeles, Minneapolis, New York, Orlando, Phoenix, Seattle* |
| `single_building` | `True` if run only **one** single building, specify building number next |
| `building_no ` | Specify building number to run. Options: 1-400 |

# Model Outputs
Hourly operations of TES (charging, discharging, SOC) and heat pump (output to TES, output to serve load).

Hourly purchase of electricity from utilities

Total system cost.
