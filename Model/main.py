"""
An Pham
Updated 11/27/2021
TES Model for Building and Water Heating
"""
import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
import time
import glob
import os
import xlsxwriter as xw

from get_storage_data import storage_data
from get_heat_pump_data import heatpump_data
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

    # TES parameters:
    capex_T_kW = 1455                               # CAPEX ($/kW)
    capex_T = capex_T_kW/alpha
    life_T = 15                                     # Storage life time (years)
    fixed_OM_T_kW = 36.37                           # Fixed TES OM cost ($/kW-year)
    fixed_OM_T = fixed_OM_T_kW/alpha
    p_T_fixed = 0                                   # TES energy cost ($/kJ/h)
    p_T = 0                                         # TES operating cost ($/kJ)
    ef_T = 0.85                                     # Round trip efficiency
    f_d  = 0.98                                     # Discharging efficiency
    f_c = ef_T/f_d                                  # Charging efficiency

    # Heat pump parameters:
    k_H = 9000                                      # Heat pump capacity (BTU)
    p_H = 729                                       # Heat pump cost
    eta_C = 3.1                                     # Coefficient of performance (COP)

    # Model's scope:
    hour = 8670

    return (super_comp,ir,alpha,beta,gamma,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,ef_T,f_d,f_c,k_H,p_H,eta_C,hour,app)


def main_function():
    (super_comp,ir,alpha,beta,gamma,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,ef_T,f_d,f_c,k_H,p_H,eta_C,hour,app) = main_params()

    (model_dir, load_folder, results_folder) = working_directory(super_comp)

    T = main_sets(hour)

    model_solve(model_dir,load_folder,results_folder,super_comp,ir,alpha,beta,gamma,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,
                ef_T,f_d,f_c,k_H,p_H,eta_C,hour,app,T)


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
def model_solve(model_dir,load_folder,results_folder,super_comp,ir,alpha,beta,gamma,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,
                ef_T,f_d,f_c,k_H,p_H,eta_C,hour,app,T):

        # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, p_W = load_data(model_dir, load_folder, app, T, hour)

    # Storage:
    (p_TK, p_TC) = storage_data(ir, life_T, capex_T, fixed_OM_T, p_T_fixed)

    # Heat pump:

    # %% Define variables and ordered set:
    model.T = Set(initialize=T, ordered=True)

    # Power rating by technology:
    model.u_H = Var(within=NonNegativeIntegers)  # Heat pump capacity

    # Energy capacity by technology:
    model.k_T = Var(within=NonNegativeReals)  # Power rating of TES
    model.e_T = Var(within=NonNegativeReals)  # TES energy capacity

    # Generation by technology:
    model.g_T = Var(T, within=NonNegativeReals)  # TES discharge
    model.i_T = Var(T, within=NonNegativeReals)  # Heat pump output discharge = TES inflow
    model.d_T = Var(T, within=NonNegativeReals)  # purchased electricity

    # TES states of charges:
    model.x_T = Var(T, within=NonNegativeReals)  # Battery state of charge

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # TES constraints:
    def ub_d_TES(model, t):
        return model.i_T[t] <= model.k_T
    model.ub_d_T = Constraint(T, rule=ub_d_TES)

    def ub_g_TES(model, t):
        return model.g_T[t] <= model.k_T
    model.ub_g_T = Constraint(T, rule=ub_g_TES)

    def ub_g_x_TES(model, t):
        return model.g_T[t] <= model.x_T[t]
    model.ub_g_x_T = Constraint(T, rule=ub_g_x_TES)

    def ub_x_e_TES(model, t):
        return model.x_T[t] <= model.e_T
    model.ub_x_e_T = Constraint(T, rule=ub_x_e_TES)

    def x_TES(model, t):
        return model.x_T[t] == model.x_T[model.T.prevw(t)] + f_c * model.i_T[t] - f_d * model.g_T[t]
    model.x_t = Constraint(model.T, rule=x_TES)

    # Heat pump's electricity demand:
    def d_heat_pump(model, t):
        return k_H*model.u_H * gamma == model.d_T[t]
    model.heat_pump_d = Constraint(T, rule=d_heat_pump)

    # Heat pump's output to TES inflow:
    def i_TES(model, t):
        return model.i_T[t] <= eta_C * alpha * model.d_T[t]
    model.inflow_const = Constraint(T, rule=i_TES)

    # Market clearing condition:
    def market_clearing(model, t):
        return model.g_T[t] == alpha * d_heating[t]
    model.mc_const = Constraint(T, rule=market_clearing)

    # Objective function:
    def obj_function(model):
        return p_TK * model.k_T + p_TC * model.e_T + sum(p_T * model.g_T[t] for t in T) \
               + model.u_H* p_H + sum(p_W * model.d_T[t] for t in T)

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
    d_T_star = np.zeros(hour)
    x_T_star = np.zeros(hour)


    u_H_star = value(model.u_H)
    e_T_star = value(model.e_T)
    k_T_star = value(model.k_T)

    for t in T:
        g_T_star[t] = value(model.g_T[t])
        i_T_star[t] = value(model.i_T[t])
        d_T_star[t] = value(model.d_T[t])
        x_T_star[t] = value(model.x_T[t])


    update_results_folder = results_folder  + '\\' #+ fixed_time_for_results
    if not os.path.exists(update_results_folder):
        os.makedirs(update_results_folder)

    results_book = xw.Workbook(update_results_folder + 'TES_model_results.xlsx')
    result_sheet_pr = results_book.add_worksheet('power rating')
    result_sheet_bg = results_book.add_worksheet('TES discharge')
    result_sheet_wg = results_book.add_worksheet('purchased electricity')
    result_sheet_ob = results_book.add_worksheet('total cost')
    result_sheet_bi = results_book.add_worksheet('TES inflow')
    result_sheet_bs = results_book.add_worksheet('TES SOC')

    hour_number = [''] * hour

    for t in T:
        hour_number[t] = "hour " + str(T[t] + 1)

    # Write total cost result:
    result_sheet_ob.write("A1", "total cost (million $)")
    result_sheet_ob.write("A2", total_cost / 1000000)

    # Write power rating results:
    result_sheet_pr.write("A1", "TES power rating (kJ)")
    result_sheet_pr.write("B1", "TES energy capacity (kJ)")
    result_sheet_pr.write("C1", "Number of 9,000 BTU heat pumps")

    result_sheet_pr.write(1, 0, k_T_star)
    result_sheet_pr.write(1, 1, e_T_star)
    result_sheet_pr.write(1, 2, u_H_star)

    # write TES discharge results:
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
    result_sheet_bi.write("A1", "TES inflow (kJ)")

    for item in T:
        result_sheet_bi.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_bi.write(1, item_2 + 1, i_T_star[item_2])

    # TES SOC results:
    result_sheet_bs.write("A1", "TES SOC (kJ)")

    for item in T:
        result_sheet_bs.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_bs.write(1, item_2 + 1, x_T_star[item_2])


    results_book.close()

main_function()

print("--- %s seconds ---" % (time.time() - start_time))
