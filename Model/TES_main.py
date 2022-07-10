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
def main_params(year, mon_to_run, include_TES, super_comp, used_cop, cop_type,
                e_T, p_T, ef_T, f_d, k_T, k_H, ir, single_building, city_to_run, building_no, building_id):

    if mon_to_run == 'Year':
        day = 365                                   # Equivalent days
        starting_day = 0
    else:
        day = monthrange(year, mon_to_run)[1]       # number of days in specified month
        starting_day = (date(year, mon_to_run, 1) - date(year, 1, 1)).days

    hour = day * 24
    starting_hour = starting_day * 24

    # TES parameters:
    f_c = ef_T/f_d                                  # Charging efficiency
    return (super_comp, ir, p_T, ef_T, f_d, f_c, hour, k_T, e_T, k_H, include_TES, starting_hour,
            mon_to_run, cop_type, used_cop, single_building, city_to_run, building_no, building_id)


def main_function(year, mon_to_run, include_TES, super_comp, used_cop, cop_type,
                  e_T, p_T, ef_T, f_d, k_T, k_H, ir, single_building, city_to_run, building_no, building_id):
    (super_comp, ir, p_T, ef_T, f_d, f_c, hour, k_T, e_T, k_H, include_TES, starting_hour,
     mon_to_run, cop_type, used_cop, single_building,
     city_to_run, building_no, building_id) = main_params(year, mon_to_run, include_TES, super_comp, used_cop,
                                                          cop_type, e_T, p_T, ef_T, f_d, k_T, k_H, ir, single_building,
                                                          city_to_run, building_no, building_id)
    (model_dir, load_folder, results_folder) = working_directory(super_comp, single_building, city_to_run)
    T = main_sets(hour)
    model_solve(model_dir, load_folder, results_folder, super_comp, ir, p_T, ef_T, k_H, f_d, f_c,
                hour, T, k_T, e_T, include_TES, starting_hour, mon_to_run, cop_type, used_cop,
                single_building, city_to_run, building_no, building_id)

# %% Set working directory:
def working_directory(super_comp, single_building, city_to_run):
    if super_comp == 1:
        model_dir = '/home/anph/projects/Thermal Storage/Data/'
        load_folder = '400 Buildings - EB/' + city_to_run + '/'
        if single_building:
            results_folder = '/home/anph/projects/Thermal Storage/Results/' + city_to_run + '/Single/'
        else:
            results_folder = '/home/anph/projects/Thermal Storage/Results/' + city_to_run + '/All/'
    else:
        model_dir = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Thermal Storage\\Data\\'
        load_folder = '400 Buildings - EB\\' + city_to_run + '\\'
        if single_building:
            results_folder = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Thermal Storage\\Results\\' + city_to_run + '\\Single\\'
        else:
            results_folder = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Thermal Storage\\Results\\' + city_to_run + '\\All\\'
    return model_dir, load_folder, results_folder

# %% Define set:
def main_sets(hour):
    T = list(range(hour))  # Set of hours to run                                 # Set of hours to run
    return T

# %% Solving HDV model:
def model_solve(model_dir, load_folder, results_folder, super_comp, ir, p_T, ef_T, k_H, f_d, f_c,
                hour, T, k_T, e_T, include_TES, starting_hour, mon_to_run, cop_type, used_cop,
                single_building, city_to_run, building_no, building_id):

    # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, p_W = load_data(super_comp, model_dir, load_folder, T, hour, starting_hour, building_id)
    cop = est_COP(model_dir, T, hour, starting_hour, cop_type, used_cop)

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
        model.x_T = Var(T, within=NonNegativeReals)                 # TES state of charge
        model.vT = Var(T, within=Binary)                            # binary variable: == 1 when TES discharges
    # Heat pump being on or off:
    model.vH = Var(T, within=Binary)                                # binary variable: == 1 when HP charges TES

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # TES constraints:
    if include_TES:
        # Heat pump's output to charge TES:
        def ub_d_TES(model, t):
            return model.g_HT[t] <= k_T * model.vH[t]
        model.ub_d_T = Constraint(T, rule=ub_d_TES)

        def ub_g_TES(model, t):
            return model.g_T[t] <= k_T * model.vT[t]
        model.ub_g_T = Constraint(T, rule=ub_g_TES)

        def ub_g_x_TES(model, t):
            return model.g_T[t] <= model.x_T[t]
        model.ub_g_x_T = Constraint(T, rule=ub_g_x_TES)

        def ub_x_e_TES(model, t):
            return model.x_T[t] <= e_T
        model.ub_x_e_T = Constraint(T, rule=ub_x_e_TES)

        def x_TES(model, t):
            return model.x_T[t] == model.x_T[model.T.prevw(t)] + f_c * model.g_HT[t] - 1/f_d * model.g_T[t]
        model.x_t = Constraint(model.T, rule=x_TES)

    # Heat pump's total load:
    def hp_load_tot(model, t):
        return model.g[t] <= k_H
    model.hp_load_tot_const = Constraint(T, rule=hp_load_tot)

    if include_TES:
        def hp_load(model, t):
            return model.g_HL[t] + model.g_HT[t] == model.g[t]
        model.hp_load_const = Constraint(T, rule=hp_load)
    else:
        def hp_load(model, t):
            return model.g_HL[t] == model.g[t]
        model.hp_load_const = Constraint(T, rule=hp_load)

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

    # Solve TES model:
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
    print('Total Cost:', total_cost)

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

    results_book = xw.Workbook(update_results_folder + 'Results_' + '_includeTES_' + str(include_TES)
                               + '_month_' + str(mon_to_run) + '_' + cop_type + 'Building_id_' + str(building_id+1) + '.xlsx')

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

print("--- %s seconds ---" % (time.time() - start_time))
