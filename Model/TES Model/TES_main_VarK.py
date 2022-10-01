"""
An Pham
Updated 11/27/2021
TES Model for Building and Water Heating
Original approach -- No temperature considered
No CAPEX
Power rating as a function of SOC
"""

import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
import time
import glob
import os
import xlsxwriter as xw
import math

from get_load_data import load_data
from get_COP_params import est_COP

from calendar import monthrange
from datetime import date

start_time = time.time()

# %% Main parameters:
def main_params(year, mon_to_run, include_TES, tes_material, replace_TES_w_Battery, include_bigM, super_comp, used_cop, cop_type,
                p_T, ef_T, f_d, k_H, ir, single_building, city_to_run, building_no, building_id):

    if mon_to_run == 'Year':
        day = 365                                   # Equivalent days
        starting_day = 0
    else:
        day = monthrange(year, mon_to_run)[1]       # number of days in specified month
        starting_day = (date(year, mon_to_run, 1) - date(year, 1, 1)).days

    hour = day * 24
    starting_hour = starting_day * 24

    bigM = 99999999

    # TES parameters:
    f_c = ef_T/f_d                                  # Charging efficiency

    # Piecewise linear function of power rating vs SOC:
    if not replace_TES_w_Battery:
        if tes_material == 'MgSO4':
            xData = [0, 0.152453, 1]
            yData = [57.25852/1000, 127.132/1000, 281.2521/1000]
            c_salt = 0.75
        elif tes_material == 'MgCl2':
            xData = [0, 0.110406, 1]
            yData = [14.82347/1000, 34.39765/1000, 84.89351/1000]
            c_salt = 0.1933333333
        elif tes_material == 'K2CO3':
            xData = [0, 0.0463205477241624, 1]
            yData = [547.047924901186/1000, 814.766768168298/1000, 1636.06071295454/1000]
            c_salt = 0.1847222222
        elif tes_material == 'SrBr2':
            xData = [0, 0.925, 1]
            yData = [1.035853/1000, 16.64624/1000, 127.6629/1000]
            c_salt = 0.3027777778
    elif replace_TES_w_Battery:
        xData = [0, 0.637072888, 1]
        yData = [0/1000, 627.021051/1000, 2803.504518/1000]
        c_salt = 0

    if not include_TES:
        xData = []
        yData = []
        c_salt = 0
    return (super_comp, ir, p_T, ef_T, f_d, f_c, hour, c_salt, k_H, tes_material,
            include_TES, starting_hour, mon_to_run, cop_type, used_cop, bigM, include_bigM,
            xData, yData, single_building, city_to_run, building_no, building_id)

def main_function_VarK(year, mon_to_run, include_TES, tes_material,  replace_TES_w_Battery, include_bigM, super_comp, used_cop,
                       cop_type, p_T, ef_T, f_d, k_H , ir, single_building, city_to_run, building_no, building_id, zeroIntialSOC):
    (super_comp, ir, p_T, ef_T, f_d, f_c, hour, c_salt, k_H, tes_material,
     include_TES, starting_hour, mon_to_run, cop_type, used_cop, bigM, include_bigM,
     xData, yData, single_building, city_to_run,
     building_no, building_id) = main_params(year, mon_to_run, include_TES, tes_material, replace_TES_w_Battery, include_bigM,
                                             super_comp, used_cop, cop_type, p_T, ef_T, f_d, k_H , ir,
                                             single_building, city_to_run, building_no, building_id)

    (model_dir, load_folder, results_folder) = working_directory(super_comp, single_building, city_to_run)
    T = main_sets(hour)
    model_solve(model_dir, load_folder, results_folder, super_comp, ir, p_T, ef_T, k_H, f_d, f_c, hour, T,
                c_salt, include_TES, tes_material, starting_hour, mon_to_run, cop_type, used_cop,
                bigM, include_bigM, xData, yData, single_building, city_to_run, building_no, building_id, zeroIntialSOC)


# %% Set working directory:
def working_directory(super_comp, single_building, city_to_run):
    if super_comp == 1:
        model_dir = '/home/anph/projects/TES/Data/'
        load_folder ='400_Buildings_EB/' + city_to_run + '/'
        if single_building:
            results_folder = '/home/anph/projects/TES/Results/' + city_to_run + '/Single/'
        else:
            results_folder = '/home/anph/projects/TES/Results/' + city_to_run + '/All/'
    else:
        model_dir = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\TES\\Data\\'
        load_folder = '400 Buildings - EB\\' + city_to_run + '\\'
        if single_building:
            results_folder = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\TES\\Results\\' + city_to_run + '\\Single\\'
        else:
            results_folder = 'C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\TES\\Results\\' + city_to_run + '\\All\\'
    return model_dir, load_folder, results_folder

# %% Define set:
def main_sets(hour):
    T = list(range(hour))                                   # Set of hours to run
    return T

# %% Solving HDV model:
def model_solve(model_dir, load_folder, results_folder, super_comp, ir, p_T, ef_T, k_H, f_d, f_c,  hour, T,
                c_salt, include_TES, tes_material, starting_hour, mon_to_run, cop_type, used_cop,
                bigM, include_bigM, xData, yData, single_building, city_to_run, building_no, building_id, zeroInitialSOC):

    # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, p_W, peakLoad = load_data(super_comp, model_dir, load_folder, T, hour, starting_hour, building_id)
    cop = est_COP(model_dir, T, hour, starting_hour, cop_type, used_cop)

    # Size of TES:
    e_T = math.ceil(peakLoad)

    if include_TES:
        v_salt = max(e_T/c_salt, e_T/max(yData))
        if tes_material == 'MgSO4' or tes_material == 'K2CO3':
            v_salt = int(math.ceil(v_salt / 25.0)) * 25
        elif tes_material == 'MgCl2' or tes_material == 'SrBr2':
            v_salt = int(math.ceil(v_salt / 100.0)) * 100

        e_T = v_salt * c_salt

        for item in list((range(len(yData)))):
            yData[item] = v_salt * yData[item]

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
        model.k_T = Var(T, bounds=(0, max(yData)))                  # TES power rating
        model.x_T = Var(T, within=NonNegativeReals)                 # TES state of charge
        model.xpt_T = Var(T, bounds=(0, 1))                         # SOC in percentage
        model.v = Var(T, within=Binary)                             # binary variable: == 1 when TES charges

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # TES constraints:
    if include_TES:
        # Heat pump's output to charge TES:
        def ub_d_TES(model, t):
            return model.g_HT[t] <= model.k_T[t]
        model.ub_d_T = Constraint(T, rule=ub_d_TES)

        def ub_g_TES(model, t):
            return model.g_T[t] <= model.k_T[t]
        model.ub_g_T = Constraint(T, rule=ub_g_TES)

        def ub_g_x_TES(model, t):
            return model.g_T[t] <= model.x_T[t]
        model.ub_g_x_T = Constraint(T, rule=ub_g_x_TES)

        def ub_x_e_TES(model, t):
            return model.x_T[t] <= e_T
        model.ub_x_e_T = Constraint(T, rule=ub_x_e_TES)

        if not zeroInitialSOC:
            def x_TES(model, t):
                return model.x_T[t] == model.x_T[model.T.prevw(t)] + f_c * model.g_HT[t] - 1/f_d * model.g_T[t]
            model.x_t = Constraint(model.T, rule=x_TES)
        else:
            def x_TES(model, t):
                if t == 0:
                    return model.x_T[t] == 0
                return model.x_T[t] == model.x_T[t-1] + f_c * model.g_HT[t] - 1/f_d * model.g_T[t]
            model.x_t = Constraint(T, rule=x_TES)

        def x_pt(model, t):
            return model.xpt_T[t] == model.x_T[t]/e_T
        model.x_pt_t = Constraint(T, rule=x_pt)

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

    # Piece-wise linear power rating vs SOC constraints:
    if include_TES:
        model.piecewise = Piecewise(T, model.k_T, model.xpt_T, pw_pts=xData, pw_constr_type='EQ', f_rule=yData, pw_repn='SOS2')

    # Big M constraints:
    if include_bigM:
        if include_TES:
            def big_M_1(model, t):
                return model.g_HT[t] <= bigM*model.v[t]
            model.bigM_const1 = Constraint(T, rule=big_M_1)

            def big_M_2(model, t):
                return model.v[t] <= bigM*model.g_HT[t]
            model.bigM_const2 = Constraint(T, rule=big_M_2)

            def big_M_3(model, t):
                return model.g_T[t] <= bigM*(1-model.v[t])
            model.bigM_const3 = Constraint(T, rule=big_M_3)

            def big_M_4(model, t):
                return (1-model.v[t]) <= bigM*model.g_T[t]
            model.bigM_const4 = Constraint(T, rule=big_M_4)

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
    #solver.options['mipgap'] = 0.005
    solver.options['mipgap'] = 0.027
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

    update_results_folder = results_folder   #+ fixed_time_for_results
    if not os.path.exists(update_results_folder):
        os.makedirs(update_results_folder)

    results_book = xw.Workbook(update_results_folder + 'Results_' + '_includeTES_' + str(include_TES) + '_' + tes_material
                               + '_month_' + str(mon_to_run) + '_' + cop_type + '_Building_id_' + str(building_id+1) + '.xlsx')

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
