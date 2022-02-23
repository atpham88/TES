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

start_time = time.time()

# %% Main parameters:
def main_params():
    # Define Switches:
    super_comp = 0                                  # ==1: run on super computer, ==0: run on local laptop

    # Model main parameters:
    ir = 0.03                                       # interest rate
    alpha = 3600                                    # Conversion from kWh to kJ
    beta = 1.055                                    # Conversion from BTU to kJ
    gamma = beta/alpha                              # Conversion from BTU to kWh

    app = 'Water'                                   # 'Water' == water boiling, 'Air' Building Heating/Coaling
    include_TES = True                              # Using coupled TES and heat pump, == False: Using heat pump only

    # TES parameters:
    p_T = 0                                         # TES operating cost ($/kW)
    ef_T = 0.85                                     # Round trip efficiency
    f_d  = 0.98                                     # Discharging efficiency
    f_c = ef_T/f_d                                  # Charging efficiency
    h_TES = 6                                       # Storage period (hours)
    k_T = 0.004                                     # Power rating (MW)
    e_T = k_T*h_TES                                 # Energy capacity (MWh)

    # Heat pump parameters:
    k_H = 9000                                      # Heat pump capacity (BTU)
    eta_C = 4                                     # Coefficient of performance (COP)
    ramp_h = 0                                    # percentage of capacity heat pump can ramp down to

    # Model's scope:
    hour = 8670

    # Big M number:
    bigM = 1000

    return (super_comp,ir,alpha,beta,gamma,p_T,ef_T,f_d,f_c,k_H,eta_C,hour,app,bigM,h_TES,k_T,e_T,include_TES,ramp_h)


def main_function():
    (super_comp,ir,alpha,beta,gamma,p_T,ef_T,f_d,f_c,k_H,eta_C,hour,app,bigM,h_TES,k_T,e_T,include_TES,ramp_h) = main_params()

    (model_dir, load_folder, results_folder) = working_directory(super_comp)

    T = main_sets(hour)

    model_solve(model_dir,load_folder,results_folder,super_comp,ir,alpha,beta,gamma,p_T,
                ef_T,f_d,f_c,k_H,eta_C,hour,app,T,bigM,h_TES,k_T,e_T,include_TES,ramp_h)


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
def model_solve(model_dir,load_folder,results_folder,super_comp,ir,alpha,beta,gamma,p_T,
                ef_T,f_d,f_c,k_H,eta_C,hour,app,T,bigM,h_TES,k_T,e_T,include_TES,ramp_h):

        # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, p_W = load_data(model_dir, load_folder, app, T, hour)

    # %% Define variables and ordered set:
    model.T = Set(initialize=T, ordered=True)

    # Generation by technology:
    if include_TES:
        model.g_T = Var(T, within=NonNegativeReals)  # TES discharge

    model.i_T = Var(T, within=NonNegativeReals)  # Heat pump output discharge = TES inflow (kWh)
    model.d_T = Var(T, within=NonNegativeReals)  # purchased electricity (kWh)

    # TES states of charges:
    if include_TES:
        model.x_T = Var(T, within=NonNegativeReals)  # Battery state of charge

    # Heat pump being on or off:
    model.v = Var(T, within=Binary)  # binary variable, indicating whether the heat pump is on or off in a given hour

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # TES constraints:
    if include_TES:
        def ub_d_TES(model, t):
            return model.i_T[t] <= k_T*1000
        model.ub_d_T = Constraint(T, rule=ub_d_TES)

        def ub_g_TES(model, t):
            return model.g_T[t] <= k_T*1000
        model.ub_g_T = Constraint(T, rule=ub_g_TES)

        def ub_g_x_TES(model, t):
            return model.g_T[t] <= model.x_T[t]
        model.ub_g_x_T = Constraint(T, rule=ub_g_x_TES)

        def ub_x_e_TES(model, t):
            return model.x_T[t] <= e_T*1000
        model.ub_x_e_T = Constraint(T, rule=ub_x_e_TES)

        def x_TES(model, t):
            return model.x_T[t] == model.x_T[model.T.prevw(t)] + f_c * model.i_T[t] - f_d * model.g_T[t]
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

    # Heat pump's output to TES inflow:
    def i_TES_upper(model, t):
        return model.i_T[t] <= k_H * gamma * eta_C * model.v[t]
    model.h_output_upper_const = Constraint(T, rule=i_TES_upper)

    #def i_TES_lower(model, t):
    #    return model.i_T[t] >= k_H * gamma *eta_C * model.v[t] * (1-ramp_h)
    #model.h_output_lower_const = Constraint(T, rule=i_TES_lower)

    def i_TES(model, t):
        return model.d_T[t] >= k_H *gamma *model.v[t]
    model.inflow_const = Constraint(T, rule=i_TES)

    # Market clearing condition:
    if include_TES:
        def market_clearing(model, t):
            return model.g_T[t] >= d_heating[t]
        model.mc_const = Constraint(T, rule=market_clearing)
    else:
        def market_clearing(model, t):
            return model.i_T[t] >= d_heating[t]
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
    i_T_star = np.zeros(hour)
    x_T_star = np.zeros(hour)
    v_T_star = np.zeros(hour)
    d_T_star = np.zeros(hour)

    for t in T:
        if include_TES:
            g_T_star[t] = value(model.g_T[t])
            i_T_star[t] = value(model.i_T[t])
            x_T_star[t] = value(model.x_T[t])
        v_T_star[t] = value(model.v[t])
        d_T_star[t] = value(model.d_T[t])

    update_results_folder = results_folder  + '\\' #+ fixed_time_for_results
    if not os.path.exists(update_results_folder):
        os.makedirs(update_results_folder)

    results_book = xw.Workbook(update_results_folder + 'Model_results' + '_includeTES_' + str(include_TES) +'.xlsx')
    result_sheet_pr = results_book.add_worksheet('power rating')
    result_sheet_bg = results_book.add_worksheet('TES discharge')
    result_sheet_wg = results_book.add_worksheet('purchased electricity')
    result_sheet_ob = results_book.add_worksheet('total cost')
    result_sheet_bi = results_book.add_worksheet('TES inflow')
    result_sheet_bs = results_book.add_worksheet('TES SOC')
    result_sheet_ho = results_book.add_worksheet('Heat pump on off')

    hour_number = [''] * hour

    for t in T:
        hour_number[t] = "hour " + str(T[t] + 1)

    # Write total cost result:
    result_sheet_ob.write("A1", "total cost (million $)")
    result_sheet_ob.write("A2", total_cost / 1000000)

    # write TES discharge results:
    if include_TES:
        result_sheet_bg.write("A1", "TES discharge (kJ)")

        for item in T:
            result_sheet_bg.write(0, item + 1, hour_number[item])

        for item_2 in T:
            result_sheet_bg.write(1, item_2 + 1, g_T_star[item_2])

    # write purchased gen results:
    result_sheet_wg.write("A1", "Purchased electricity (kWh)")

    for item in T:
        result_sheet_wg.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_wg.write(1, item_2 + 1, d_T_star[item_2])

    # TES inflow results:
    if include_TES:
        result_sheet_bi.write("A1", "TES inflow (kJ)")

        for item in T:
            result_sheet_bi.write(0, item + 1, hour_number[item])

        for item_2 in T:
            result_sheet_bi.write(1, item_2 + 1, i_T_star[item_2])

    # TES SOC results:
    if include_TES:
        result_sheet_bs.write("A1", "TES SOC (kJ)")

        for item in T:
            result_sheet_bs.write(0, item + 1, hour_number[item])

        for item_2 in T:
            result_sheet_bs.write(1, item_2 + 1, x_T_star[item_2])

    # Heat pumo on-off results:
    result_sheet_ho.write("A1", "Heat Pump on - off")

    for item in T:
        result_sheet_ho.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_ho.write(1, item_2 + 1, v_T_star[item_2])

    results_book.close()

main_function()

print("--- %s seconds ---" % (time.time() - start_time))
