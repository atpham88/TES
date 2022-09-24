
from TES_main_VarK import *
from TES_main import *
from get_Opt_k_e import *

def main():
    # Define Switches:
    super_comp = 0                          # ==1: run on super computer, ==0: run on local laptop
    city_to_run = 'Detroit'                 # Name of city to running building/s located in
    single_building = True                  # == True: run only one single building in a city
                                            # == False: run all buildings in that city
    building_no = 305                        # == ID of building to run (if running single building)

    include_TES = False                      # Using coupled TES and heat pump, == False: Using heat pump only
    replace_TES_w_Battery = False           # Replace a TES system with battery

    # If include_TES = True, these options can be chosen:
    include_pw_func = True                  # Include piecewise linear function for power rating vs energy capacity
    include_bigM = False                    # Include bigM constraints for TES
    used_cop = "TES"                        # == Resstock: use estimated resstock COP, == TES: use Modi paper calculated COPs
    cop_type = 'NEEP50'                     # Type of COP used if used_cop == TES: NEEP90, NEEP50, DOE
    tes_material = 'MgSO4'                  # Type of TES material, choosing from:
                                            # MgSO4, K2CO3, MgCl2
    zeroIntialSOC = True                    # If True, set first period SOC = 0, otherwise first period SOC depends on last

    if not include_TES:
        tes_material = ''

    p_T = 0                                 # TES operating cost ($/kW)
    ef_T = 0.98                             # Round trip efficiency
    f_d = 0.98                              # Discharging efficiency

    # Model time and resolution:
    year = 2018
    mon_to_run = 'Year'                     # == 'Year': run entire year, 1,2,...,12: run individual month.
    ir = 0.03                               # interest rate

    if used_cop == 'Resstock':
        cop_type = 'ResstockCOP'

    if single_building:
        B = list(range(1))
    else:
        B = list(range(400))

    for b in B:
        building_id = b

        if single_building:
            building_id = building_no-1

        k_H_star = main_function_Opt_k_e(year, mon_to_run, super_comp, used_cop, cop_type,
                                         p_T, ef_T, f_d, ir, single_building, city_to_run, building_no, building_id)

        # Heat pump parameters:
        k_H = k_H_star                           # Heat pump capacity (kWh)

        if include_pw_func:
            main_function_VarK(year, mon_to_run, include_TES, tes_material, replace_TES_w_Battery, include_bigM, super_comp, used_cop, cop_type,
                               p_T, ef_T, f_d, k_H, ir, single_building, city_to_run, building_no, building_id, zeroIntialSOC)
        else:
            main_function(year, mon_to_run, include_TES, tes_material, replace_TES_w_Battery, super_comp, used_cop, cop_type,
                          p_T, ef_T, f_d, k_H, ir, single_building, city_to_run, building_no, building_id, zeroIntialSOC)

main()
