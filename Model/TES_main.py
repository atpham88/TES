"""
An Pham
Updated 11/27/2021
TES Model for Building and Water Heating
Original approach -- No temperature considered
No CAPEX
"""

import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
import time
import glob
import os
import xlsxwriter as xw

from get_load_data import load_data
from get_COP_params import est_COP

from calendar import monthrange
from datetime import date

start_time = time.time()

# %% Main parameters:
def main_params():

    year = 2017
    mon_to_run = 1

    if mon_to_run == 'Year':
        day = 365                                   # Equivalent days
        starting_day = 0
    else:
        day = monthrange(year, mon_to_run)[1]       # number of days in specified month
        starting_day = (date(year, mon_to_run, 1) - date(year, 1, 1)).days

    hour = day * 24
    starting_hour = starting_day * 24

    # Define Switches:
    super_comp = 0                                  # ==1: run on super computer, ==0: run on local laptop

    # Model main parameters:
    ir = 0.03                                       # interest rate
    alpha = 3600                                    # Conversion from kWh to kJ
    beta = 1.055                                    # Conversion from BTU to kJ
    gamma = beta/alpha                              # Conversion from BTU to kWh

    app = 'Water'                                   # 'Water' == water boiling, 'Air' Building Heating/Coaling
    include_TES = True                              # Using coupled TES and heat pump, == False: Using heat pump only
    cop_type = 'DOE'                             # Type of COP used NEEP, NEEP50, DOE

    # TES parameters:
    p_T = 0                                         # TES operating cost ($/kW)
    ef_T = 0.85                                     # Round trip efficiency
    f_d  = 0.98                                     # Discharging efficiency
    f_c = ef_T/f_d                                  # Charging efficiency
    h_TES = 4                                       # Storage period (hours)
    k_T = 0.004                                     # Power rating (MW)
    e_T = k_T*h_TES                                 # Energy capacity (MWh)

    # Heat pump parameters:
    k_H = 27000                                      # Heat pump capacity (BTU)
    #eta_CT = 3.1                                   # Coefficient of performance (COP) when HP is charging TES
    #eta_CL = 3.1                                   # Coefficient of performance (COP) when HP is serving load
    ramp_h = 0.7                                    # percentage of capacity heat pump can ramp down to

    return (super_comp, ir, alpha, beta, gamma, p_T, ef_T, f_d, f_c, k_H, hour, app, h_TES, k_T, e_T,
            include_TES, ramp_h, starting_hour, mon_to_run, cop_type)


def main_function():
    (super_comp, ir, alpha, beta, gamma, p_T, ef_T, f_d, f_c, k_H, hour, app, h_TES, k_T, e_T,
     include_TES, ramp_h, starting_hour, mon_to_run, cop_type) = main_params()

    (model_dir, load_folder, results_folder) = working_directory(super_comp)

    T = main_sets(hour)

    model_solve(model_dir, load_folder, results_folder, super_comp, ir, alpha, beta, gamma,p_T, ef_T, f_d, f_c,
                k_H, hour, app, T, h_TES, k_T, e_T, include_TES, ramp_h, starting_hour, mon_to_run, cop_type)


# %% Set working directory:
def working_directory(super_comp):
    if super_comp == 1:
        model_dir = '/home/anph/projects/Thermal Storage/Data/'
        load_folder = 'load/'
        results_folder = '/home/anph/projects/Thermal Storage/Results/'
    else:
        model_dir = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Thermal Storage\\Data\\'
        load_folder = 'load\\'
        results_folder = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Thermal Storage\\Results\\'
    return model_dir, load_folder, results_folder

# %% Define set:
def main_sets(hour):
    T = list(range(hour))                                   # Set of hours to run
    return T

# %% Solving HDV model:
def model_solve(model_dir, load_folder, results_folder, super_comp, ir, alpha, beta, gamma, p_T, ef_T, f_d, f_c,
                k_H, hour, app, T, h_TES, k_T, e_T, include_TES, ramp_h, starting_hour, mon_to_run, cop_type):

        # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, p_W = load_data(model_dir, load_folder, app, T, hour, starting_hour)
    cop = est_COP(model_dir, app, T, hour, starting_hour, cop_type)

    # %% Define variables and ordered set:
    model.T = Set(initialize=T, ordered=True)

    # Generation by technology:
    if include_TES:
        model.g_T = Var(T, within=NonNegativeReals)                 # TES discharge to serve thermal load
        model.g_HT = Var(T, within=NonNegativeReals)                # Heat pump output to charge TES

    model.g = Var(T, within=NonNegativeReals)                       # Total output from heat pump (kWh)
    model.g_HL = Var(T, within=NonNegativeReals)                    # Heat pump output to serve load
    model.d_T = Var(T, within=NonNegativeReals)                     # purchased electricity (kWh)

    # TES states of charges:
    if include_TES:
        model.x_T = Var(T, within=NonNegativeReals)                 # Battery state of charge
        model.vT = Var(T, within=Binary)                            # binary variable: == 1 when TES discharges
    # Heat pump being on or off:
    model.vH = Var(T, within=Binary)                                # binary variable: == 1 when HP charges TES

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # TES constraints:
    if include_TES:
        # Heat pump's output to charge TES:
        def ub_d_TES(model, t):
            return model.g_HT[t] <= k_T * 1000 * model.vH[t]
        model.ub_d_T = Constraint(T, rule=ub_d_TES)

        def ub_g_TES(model, t):
            return model.g_T[t] <= k_T * 1000 * model.vT[t]
        model.ub_g_T = Constraint(T, rule=ub_g_TES)

        def ub_g_x_TES(model, t):
            return model.g_T[t] <= model.x_T[t]
        model.ub_g_x_T = Constraint(T, rule=ub_g_x_TES)

        def ub_x_e_TES(model, t):
            return model.x_T[t] <= e_T * 1000
        model.ub_x_e_T = Constraint(T, rule=ub_x_e_TES)

        def x_TES(model, t):
            return model.x_T[t] == model.x_T[model.T.prevw(t)] + f_c * model.g_HT[t] - 1/f_d * model.g_T[t]
        model.x_t = Constraint(model.T, rule=x_TES)

    # Heat pump's electricity demand:
    #def d_heat_pump(model, t):
    #    return model.d_T[t] == k_H * gamma * model.v[t]
    #model.heat_pump_d = Constraint(T, rule=d_heat_pump)

    # If TES flow is 0, no need to purchase electricity:
    #def big_M(model, t):
    #    return model.i_T[t] <=bigM * model.v[t]
    #model.bigM_const = Constraint(T,rule=big_M)

    #def vbound(model, t):
    #    return model.v[t] <= model.i_T[t]
    #model.vbound_const = Constraint(T,rule=vbound)

    # Heat pump's total load:
    def hp_load_tot(model, t):
        return model.g[t] <= k_H * gamma
    model.hp_load_tot_const = Constraint(T, rule=hp_load_tot)

    if include_TES:
        def hp_load(model, t):
            return model.g_HL[t] + model.g_HT[t] == model.g[t]
        model.hp_load_const = Constraint(T, rule=hp_load)
    else:
        def hp_load(model, t):
            return model.g_HL[t] == model.g[t]
        model.hp_load_const = Constraint(T, rule=hp_load)

    #def i_load_lower(model, t):
    #    return model.g_HL[t] >= k_H * gamma * eta_CL[t] * model.vL[t] * (1-ramp_h)
    #model.h_load_lower_const = Constraint(T, rule=i_load_lower)

    # TES cannot charge and discharge at the same time:
    if include_TES:
        def TES_balance(model, t):
            return model.vT[t] + model.vH[t] <= 1
        model.TES_balance_const = Constraint(T, rule=TES_balance)

    # Electricity purchased needs to be enough to power heat pump
    def i_TES(model, t):
        return model.d_T[t] >= model.g[t]/cop[t]
    model.inflow_const = Constraint(T, rule=i_TES)

    # Market clearing condition:
    if include_TES:
        def market_clearing(model, t):
            return model.g_HL[t] + model.g_T[t] >= d_heating[t]
        model.mc_const = Constraint(T, rule=market_clearing)
    else:
        def market_clearing(model, t):
            return model.g_HL[t] >= d_heating[t]
        model.mc_const = Constraint(T, rule=market_clearing)

    # Objective function:
    if include_TES:
        def obj_function(model):
            return sum(p_T * model.g_T[t] for t in T) + sum(p_W * model.d_T[t]  for t in T)
        model.obj_func = Objective(rule=obj_function)
    else:
        def obj_function(model):
            return sum(p_W * model.d_T[t] for t in T)
        model.obj_func = Objective(rule=obj_function)

    # Solve HDV model:
    # model.dual = Suffix(direction=Suffix.IMPORT_EXPORT)
    solver = SolverFactory('cplex')
    results = solver.solve(model, tee=True)
    # model.pprint()
    #model.display()
    #model.k_B.display()
    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        print('Solution is feasible')
    elif results.solver.termination_condition == TerminationCondition.infeasible:
        print('Solution is infeasible')
    else:
        # Something else is wrong
        print('Solver Status: ', results.solver.status)

    # Print variable outputs:
    total_cost = value(model.obj_func)

    g_T_star = np.zeros(hour)
    g_star = np.zeros(hour)
    g_HT_star = np.zeros(hour)
    g_HL_star = np.zeros(hour)
    x_T_star = np.zeros(hour)
    d_T_star = np.zeros(hour)

    for t in T:
        if include_TES:
            g_T_star[t] = value(model.g_T[t])
            g_HT_star[t] = value(model.g_HT[t])
            x_T_star[t] = value(model.x_T[t])
        d_T_star[t] = value(model.d_T[t])
        g_HL_star[t] = value(model.g_HL[t])
        g_star[t] = value(model.g[t])

    update_results_folder = results_folder  + '\\' #+ fixed_time_for_results
    if not os.path.exists(update_results_folder):
        os.makedirs(update_results_folder)

    results_book = xw.Workbook(update_results_folder + 'Model_results' + '_includeTES_' + str(include_TES) + '_month_' + str(mon_to_run) +'.xlsx')

    result_sheet_ob = results_book.add_worksheet('total cost')
    result_sheet_d = results_book.add_worksheet('load')
    result_sheet_wg = results_book.add_worksheet('purchased electricity')
    result_sheet_bi = results_book.add_worksheet('HP output')
    result_sheet_bg = results_book.add_worksheet('TES')

    hour_number = [''] * hour

    for t in T:
        hour_number[t] = "hour " + str(T[t] + 1)

    # Write total cost result:
    result_sheet_ob.write("A1", "total cost ($)")
    result_sheet_ob.write("A2", total_cost)

    # write TES discharge results:
    if include_TES:
        result_sheet_bg.write("B1", "TES discharge (kWh)")
        result_sheet_bg.write("C1", "TES SOC (kWh)")

        for item in T:
            result_sheet_bg.write(item + 1, 0, hour_number[item])

        for item_2 in T:
            result_sheet_bg.write(item_2 + 1, 1, g_T_star[item_2])
            result_sheet_bg.write(item_2 + 1, 2, x_T_star[item_2])

    # write purchased gen results:
    result_sheet_wg.write("A1", "Purchased electricity (kWh)")

    for item in T:
        result_sheet_wg.write(item + 1, 0, hour_number[item])

    for item_2 in T:
        result_sheet_wg.write(item_2 + 1, 1, d_T_star[item_2])

    # write load:
    result_sheet_d.write("B1", "Load (kWh)")

    for item in T:
        result_sheet_d.write(item + 1, 0, hour_number[item])

    for item_2 in T:
        result_sheet_d.write(item_2 + 1, 1, d_heating[item_2])

    # TES inflow results:
    if include_TES:
        result_sheet_bi.write("B1", "HP output to TES (kWh)")

        for item in T:
            result_sheet_bi.write(item + 1, 0, hour_number[item])

        for item_2 in T:
            result_sheet_bi.write(item_2 + 1, 1, g_HT_star[item_2])

    result_sheet_bi.write("C1", "HP output to load (kWh)")
    result_sheet_bi.write("D1", "HP output total (kWh)")

    for item_2 in T:
        result_sheet_bi.write(item_2 + 1, 2, g_HL_star[item_2])
        result_sheet_bi.write(item_2 + 1, 3, g_star[item_2])

    results_book.close()

main_function()

print("--- %s seconds ---" % (time.time() - start_time))
