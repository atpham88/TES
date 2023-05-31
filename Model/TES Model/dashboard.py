
from TES_main_VarK import *
from get_Opt_k_e import *

def main():
    # Define Switches:
    super_comp =  False                     # = True: run on super computer, = False: run on local laptop
    city = 'Detroit'                         # Name of city to running building/s located in
    single_building = True                  # = True: run only one single building in a city
                                            # = False: run all buildings in that city or a range of building
    building_range = False                  # = True: run building within range specified
    # If running single building (single_building = True), pick building ID to run (from 1 to 400):
    building_no = 5                         # = ID of building to run (if running single building
    # if running multiple buildings can also specify building range:
    if building_range:
        first_building, last_building = 176, 177

    # Utility rate options:
    pricing = 'Fixed'                         # =Fixed, ToD=Time of day, DP=Dynamic peak

    # Coupled TES with heat pump to shift load or not:
    include_TES = True                      # Using coupled TES and heat pump, == False: Using heat pump only
    tes_sizing = 'Varied'                   # TES sizing methods:
                                            # = Varied: Varying based on peak load
                                            # = Incremental: based on peak load + round up to 25 kg
                                            # = Fixed: fixed size at 150 kg regardless of salt

    # If include_TES = True, these options can be chosen:
    include_bigM = False                    # Include bigM constraints for TES
    used_cop = "Waite_Modi"                 # = Resstock: use estimated resstock COP, = Waite_Modi: use Waite and Modi paper's calculation of COPs
    cop_type = 'NEEP50'                     # Type of COP used if used_cop = Waite_Modi: NEEP90, NEEP50, DOE
    tes_material = 'MgSO4'                  # Type of TES material, choosing from:
                                            # MgSO4, K2CO3, MgCl2, SrBr2
    const_pr = True                         # = True: use constant rating (no Ragone plot regardless of salt types)
    if const_pr:
        power_rating = 'Peak'               # Constant power rating, = Peak: at peak load, = Average: at 100 W per kg, = Low: at 10 W per kg
    else:
        power_rating = 'None'

    # Instead of minimizing cost, maximizing total peak load reduction:
    curb_H = False                          # Curb heat pump output when with TES to reduce peak load
    zeroIntialSOC = True                    # If True, set first period SOC = 0, otherwise first period SOC depends on last

    if not include_TES:
        tes_material = ''

    if city == 'Detroit':
        city_to_run = 'Detroit'
    elif city == 'Los Angeles' or city == 'New York' or city == 'Orlando' or city == 'Seattle' \
            or city == 'Atlanta' or city == 'Minneapolis' or city == 'Phoenix':
        city_to_run = 'LA_NYC_ORL_SEA_ATL_MIN_PHX'
    elif city == 'Boston' or city == 'Boulder' or city == 'Chicago' or city == 'Dallas':
        city_to_run = 'BOS_CHI_DAL_BOU'

    p_T = 0                                 # TES operating cost ($/kWh)
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
        if building_range:
            B = list(range(first_building, last_building+1))
        else:
            B = list(range(400))

    for b in B:
        building_id = b

        if single_building:
            building_id = building_no-1

        k_H_star = main_function_Opt_k_e(year, mon_to_run, super_comp, used_cop, cop_type, curb_H, pricing,
                                         p_T, ef_T, f_d, ir, single_building, city_to_run, building_no, building_id, city)

        # Heat pump parameters:
        k_H = k_H_star                           # Heat pump capacity (kWh)

        main_function_VarK(year, mon_to_run, include_TES, tes_material, tes_sizing, include_bigM, super_comp, used_cop, cop_type,
                           p_T, ef_T, f_d, k_H, ir, single_building, city_to_run, building_no, building_id, zeroIntialSOC, pricing,
                           curb_H, city, const_pr, power_rating)

main()
