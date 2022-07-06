
from TES_main_VarK import *
from TES_main import *

def main():
    # Define Switches:
    super_comp = 0                          # ==1: run on super computer, ==0: run on local laptop
    include_TES = True                     # Using coupled TES and heat pump, == False: Using heat pump only

    # Heat pump parameters:
    k_H = 12.1134986948048                  # Heat pump capacity (kWh)

    # If include_TES = True, these options can be chosen:
    include_pw_func = True                 # Include piecewise linear function for power rating vs energy capacity
    include_bigM = False                    # Include bigM constraints for TES
    used_cop = "TES"                        # == Resstock: use estimated resstock COP, == TES: use Modi paper calculated COPs
    cop_type = 'NEEP50'                     # Type of COP used if used_cop == TES: NEEP90, NEEP50, DOE
    e_T = 300                               # Energy capacity (kWh)
    k_T = 2                                 # TES constant power rating (kW) (if not using piecewise linear function)
    p_T = 0                                 # TES operating cost ($/kW)
    ef_T = 0.98                             # Round trip efficiency
    f_d = 0.98                              # Discharging efficiency
    c_salt = 0.56                           # Conversion from kWh to kg of salt = kWh/c_salt

    # Model time and resolution:
    year = 2018
    mon_to_run = 'Year'                     # == 'Year': run entire year, 1,2,...,12: run individual month.
    ir = 0.03                               # interest rate

    if include_pw_func:
        main_function_VarK(year, mon_to_run, include_TES, include_bigM, super_comp, used_cop, cop_type,
                           e_T, p_T, ef_T, f_d, c_salt, k_H, ir)
    else:
        main_function(year, mon_to_run, include_TES, super_comp, used_cop, cop_type, e_T, p_T, ef_T, f_d, k_T, k_H, ir)

main()
