"""
An Pham
Updated 03/08/2023
TES Model for Space Heating
Power rating as a function of SOC
"""

import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
import time
import os
import xlsxwriter as xw
import math

from get_load_data import load_data
from get_COP_params import est_COP

from calendar import monthrange
from datetime import date

start_time = time.time()

# %% Main parameters:
def main_params(year, mon_to_run, include_TES, tes_material, tes_sizing, include_bigM, super_comp,
                used_cop, cop_type, p_T, ef_T, f_d, k_H, ir, single_building, city_to_run, building_no,
                building_id, const_pr, power_rating):

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
    if include_TES:
        if not const_pr:
            if tes_material == 'MgSO4':
                # xData = [0, 0.268018305, 1]
                # yData = [2.816408928/1000, 83.20127263/1000, 281.2673055/1000]
                # xData_charge = [0, 1-0.268018305, 1]
                # yData_charge = [281.2673055/1000, 83.20127263/1000, 2.816408928/1000]
                xData = [0, 1]
                yData = [2.816408928/1000, 281.2673055/1000]
                xData_charge = [0, 1]
                yData_charge = [281.2673055/1000, 2.816408928/1000]
                c_salt = 0.75
            elif tes_material == 'MgCl2':
                # xData = [0, 0.213856511, 1]
                # yData = [0.930935172 / 1000, 20.35515839 / 1000, 84.76789215 / 1000]
                # xData_charge = [0, 1 - 0.213856511, 1]
                # yData_charge = [84.76789215 / 1000, 20.35515839 / 1000, 0.930935172 / 1000]

                xData = [0, 1]
                yData = [0.930935172/1000, 84.76789215/1000]
                xData_charge = [0, 1]
                yData_charge = [84.76789215/1000, 0.930935172/1000]
                c_salt = 0.193056
            elif tes_material == 'K2CO3':
                xData = [0, 0.129554216, 1]
                yData = [81.60749345/1000, 444.7337936/1000, 1646.738256/1000]
                xData_charge = [0, 1-0.129554216, 1]
                yData_charge = [1646.738256/1000, 444.7337936/1000, 81.60749345/1000]
                c_salt = 0.18611
            elif tes_material == 'SrBr2':
                # xData = [0, 0.449284033, 1]
                # yData = [9.844630229 / 1000, 402.2793362 / 1000, 811.2535806 / 1000]
                # xData_charge = [0, 1 - 0.449284033, 1]
                # yData_charge = [811.2535806 / 1000, 402.2793362 / 1000, 9.844630229 / 1000]

                xData = [0, 1]
                yData = [9.844630229/1000, 811.2535806/1000]
                xData_charge = [0, 1]
                yData_charge = [811.2535806/1000, 9.844630229/1000 ]
                c_salt = 0.3556
            yData_ref = yData
        else:
            yData_ref = [2.816408928 / 1000, 281.2673055 / 1000]
            if power_rating == 'Peak':
                xData = [0, 1]
                yData = [281.2673055/1000, 281.2673055/1000]
                xData_charge = [0, 1]
                yData_charge = [281.2673055/1000, 281.2673055/1000]
            elif power_rating == 'Average':
                xData = [0, 1]
                yData = [100/1000, 100/1000]
                xData_charge = [0, 1]
                yData_charge = [100/1000, 100/1000]
            elif power_rating == 'Low':
                xData = [0, 1]
                yData = [10/1000, 10/1000]
                xData_charge = [0, 1]
                yData_charge = [10/1000, 10/1000]
            c_salt = 0.75
    elif not include_TES:
        xData = []
        yData = []
        xData_charge = []
        yData_charge = []
        c_salt = 0
        yData_ref =[]

    return (super_comp, ir, p_T, ef_T, f_d, f_c, hour, c_salt, k_H, tes_material, tes_sizing, include_TES, starting_hour,
            mon_to_run, cop_type, used_cop, bigM, include_bigM, xData, yData, xData_charge, yData_charge, yData_ref,
            single_building, city_to_run, building_no, building_id)

def main_function_VarK(year, mon_to_run, include_TES, tes_material, tes_sizing, include_bigM, super_comp, used_cop,
                       cop_type, p_T, ef_T, f_d, k_H, ir, single_building, city_to_run, building_no, building_id, zeroIntialSOC, pricing,
                       curb_H, city, const_pr, power_rating):
    (super_comp, ir, p_T, ef_T, f_d, f_c, hour, c_salt, k_H, tes_material, tes_sizing,
     include_TES, starting_hour, mon_to_run, cop_type, used_cop, bigM, include_bigM,
     xData, yData, xData_charge, yData_charge, yData_ref, single_building, city_to_run,
     building_no, building_id) = main_params(year, mon_to_run, include_TES, tes_material, tes_sizing,
                                             include_bigM, super_comp, used_cop, cop_type, p_T, ef_T, f_d, k_H, ir,
                                             single_building, city_to_run, building_no, building_id, const_pr, power_rating)

    (model_dir, load_folder, results_folder) = working_directory(super_comp, single_building, city_to_run, city)
    T = main_sets(hour)

    # Read total system cost under no TES:
    if include_TES:
        if curb_H:
            if super_comp:
                totcost_noTES = pd.read_excel('/nfs/turbo/seas-mtcraig/anph/TES/Results/Detroit/Compiled/costs_noTES_Fixed_Rate.xlsx')
            elif not super_comp:
                totcost_noTES = pd.read_excel('C:/Users/atpha/Documents/Postdocs/Projects/TES/Results/Detroit/Compiled/costs_noTES_Fixed_Rate.xlsx')
            totcost_noTES = float(totcost_noTES.loc[totcost_noTES['Unnamed: 0'] == building_no, 'total cost ($)'])
        else: totcost_noTES = 0
    else:
        totcost_noTES = 0

    model_solve(model_dir, load_folder, results_folder, super_comp, ir, p_T, ef_T, k_H, f_d, f_c, hour, T, pricing,
                c_salt, include_TES, tes_material, tes_sizing, starting_hour, mon_to_run, cop_type, used_cop, curb_H, totcost_noTES,
                bigM, include_bigM, xData, yData, xData_charge, yData_charge, yData_ref, single_building, city_to_run, building_no,
                building_id, zeroIntialSOC, city,  const_pr, power_rating)


# %% Set working directory:
def working_directory(super_comp, single_building, city_to_run, city):
    if city == 'Los Angeles':
        city = 'LA'
    elif city == 'New York':
        city = 'NY'
    if super_comp:
        model_dir = '/nfs/turbo/seas-mtcraig/anph/TES/Data/'
        load_folder = '400_Buildings_EB/' + city_to_run + '/'
        if single_building:
            results_folder = '/nfs/turbo/seas-mtcraig/anph/TES/Results/' + city + '/Single/'
        else:
            results_folder = '/nfs/turbo/seas-mtcraig/anph/TES/Results/' + city + '/All/'
    else:
        model_dir = '/Users/apham/Documents/GitHub/TES/Data'
        load_folder = '400_Buildings_EB/' + city_to_run + '/'
        if single_building:
            results_folder = '/Users/apham/Documents/GitHub/TES/Results/' + city + '\\Single\\'
        else:
            results_folder = '/Users/apham/Documents/GitHub/TES/Results/' + city + '\\All\\'
    return model_dir, load_folder, results_folder

# %% Define set:
def main_sets(hour):
    T = list(range(hour))                                   # Set of hours to run
    return T

# %% Solving HDV model:
def model_solve(model_dir, load_folder, results_folder, super_comp, ir, p_T, ef_T, k_H, f_d, f_c, hour, T, pricing,
                c_salt, include_TES, tes_material, tes_sizing, starting_hour, mon_to_run, cop_type, used_cop, curb_H, totcost_noTES,
                bigM, include_bigM, xData, yData, xData_charge, yData_charge, yData_ref, single_building, city_to_run,
                building_no, building_id, zeroInitialSOC, city,  const_pr, power_rating):

    # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, p_W, peakLoad, load_weight = load_data(super_comp, model_dir, load_folder, T, hour, city, starting_hour, building_id, pricing, curb_H)
    cop = est_COP(model_dir, T, hour, starting_hour, cop_type, used_cop, city)

    # Size of TES:
    e_T_temp = math.ceil(peakLoad)

    if include_TES:
        if tes_sizing == 'Varied':
            v_salt = max(e_T_temp/c_salt, e_T_temp/max(yData_ref))
        elif tes_sizing == 'Incremental':
            v_salt = max(e_T_temp / c_salt, e_T_temp / max(yData_ref))
            v_salt = int(math.ceil(v_salt / 25.0)) * 25
        elif tes_sizing == 'Fixed':
            v_salt = 150

        e_T = v_salt * c_salt

        for item in list((range(len(yData)))):
            yData[item] = v_salt * yData[item]
        for item in list((range(len(yData_charge)))):
            yData_charge[item] = v_salt * yData_charge[item]

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
        model.k_T = Var(T, bounds=(0, max(yData)))                  # TES power rating for discharging
        model.k_Tc = Var(T, bounds=(0, max(yData_charge)))          # TES power rating for charging
        model.x_T = Var(T, within=NonNegativeReals)                 # TES state of charge
        model.xpt_T = Var(T, bounds=(0, 1))                         # SOC in percentage
        if bigM:
            model.v = Var(T, within=Binary)                             # binary variable: == 1 when TES charges
        if curb_H:
            model.hp_cap_red = Var(bounds=(0, 1))                    # Percentage of peak load reduction

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # TES constraints:
    if include_TES:
        # Heat pump's output to charge TES:
        def ub_d_TES(model, t):
            return model.g_HT[t] <= model.k_Tc[t]
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

        if curb_H:
            def hp_max(model, t):
                return model.g[t] <= e_T_temp*model.hp_cap_red
            model.hp_max_const = Constraint(T, rule=hp_max)

            def obj_func_buffer(model):
                return sum(p_T * model.g_T[t] for t in T) + sum(p_W[t] * model.d_T[t] for t in T) <= totcost_noTES
            model.obj_func_buffer_const = Constraint(rule=obj_func_buffer)

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
        model.piecewise_charge = Piecewise(T, model.k_Tc, model.xpt_T, pw_pts=xData_charge, pw_constr_type='EQ',
                                           f_rule=yData_charge, pw_repn='CC')

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
            if curb_H:
                return model.hp_cap_red
            else:
                return sum(p_T * model.g_T[t] for t in T) + sum(p_W[t] * model.d_T[t] for t in T)
        model.obj_func = Objective(rule=obj_function)
    else:
        def obj_function(model):
            return sum(p_W[t] * model.d_T[t] for t in T)
        model.obj_func = Objective(rule=obj_function)

    # Solve TES model:
    # model.dual = Suffix(direction=Suffix.IMPORT_EXPORT)
    solver = SolverFactory('cplex')
    # solver.options['mipgap'] = 0.005
    # solver.options['mipgap'] = 0.027
    results = solver.solve(model, tee=True)
    # model.pprint()
    # model.display()
    # model.k_B.display()
    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        print('Solution is feasible')
    elif results.solver.termination_condition == TerminationCondition.infeasible:
        print('Solution is infeasible')
    else:
        # Something else is wrong
        print('Solver Status: ', results.solver.status)

    # Print variable outputs:
    fval = value(model.obj_func)
    print('Objective function:', fval)

    g_T_star = np.zeros(hour)
    g_star = np.zeros(hour)
    g_HT_star = np.zeros(hour)
    g_HL_star = np.zeros(hour)
    x_T_star = np.zeros(hour)
    d_T_star = np.zeros(hour)
    cost_T = np.zeros(hour)

    for t in T:
        if include_TES:
            g_T_star[t] = value(model.g_T[t])
            g_HT_star[t] = value(model.g_HT[t])
            x_T_star[t] = value(model.x_T[t])
        d_T_star[t] = value(model.d_T[t])
        g_HL_star[t] = value(model.g_HL[t])
        g_star[t] = value(model.g[t])
        cost_T[t] = d_T_star[t]*p_W[t]

    total_cost = cost_T.sum()

    update_results_folder = results_folder                   # + fixed_time_for_results
    if not os.path.exists(update_results_folder):
        os.makedirs(update_results_folder)

    if not curb_H:
        results_book = xw.Workbook(update_results_folder + 'Results_' + 'includeTES_' + str(include_TES) + '_' + tes_material
                                   + '_month_' + str(mon_to_run) + '_' + cop_type + '_' + pricing + '_Building_id_'
                                   + 'Size_' + tes_sizing + '_' + str(building_id+1) + '.xlsx')
        if const_pr:
            results_book = xw.Workbook(update_results_folder + 'Results_' + 'includeTES_' + str(include_TES) + '_'
                                       + power_rating + '_' + pricing + '_Building_id_'
                                       + 'Size_' + tes_sizing + '_' + str(building_id + 1) + '.xlsx')

    elif curb_H:
        results_book = xw.Workbook(update_results_folder + 'Results_' + 'curbH_includeTES_' + str(include_TES) + '_' + tes_material
                                   + '_month_' + str(mon_to_run) + '_' + cop_type + '_' + pricing + '_Building_id_'
                                   + 'Size_' + tes_sizing + '_' + str(building_id + 1) + '.xlsx')

    result_sheet_ob = results_book.add_worksheet('total cost')
    result_sheet_d = results_book.add_worksheet('load')
    result_sheet_wg = results_book.add_worksheet('purchased electricity')
    result_sheet_bi = results_book.add_worksheet('HP output')
    result_sheet_bg = results_book.add_worksheet('TES')
    if curb_H:
        result_sheet_rl = results_book.add_worksheet('reduced peak load')

    hour_number = [''] * hour

    for t in T:
        hour_number[t] = "hour " + str(T[t] + 1)

    # Write total cost result:
    result_sheet_ob.write("A1", "total cost ($)")
    result_sheet_ob.write("A2", total_cost)

    # Reduced peak load:
    if curb_H:
        result_sheet_rl.write("A1", "Reduced peak load (fraction)")
        result_sheet_rl.write("A2", fval)

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
