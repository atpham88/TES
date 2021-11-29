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
    alpha = 3600                                    # Conversion from khW to kJ

    mass_W = 2000000                                # size of the water tank (g)
    mass_A = 2000                                   # mass of air in building 9g)
    c_W = 4.184                                     # Specific heat capacity of water (J/g C)
    c_A = 1.012                                     # Specific heat capacity of air (J/g C)

    app = 'Water'                                   # 'Water' == water boiling, 'Air' Building Heating/Coaling
    if app == 'Water':
        m = mass_W
        c = c_W
    elif app == 'Air':
        m = mass_A
        c = c_A

    # TES parameters:
    capex_T = 1455000                               # CAPEX ($/MW)
    life_T = 15                                     # Storage life time (years)
    fixed_OM_T = 36370                              # Fixed TES OM cost ($/MW-year)
    p_T_fixed = 0                                   # TES energy cost ($/kWh/h)
    p_T = 0                                         # TES operating cost ($/MWh)
    ef_T = 0.85                                     # Round trip efficiency
    f_d  = 0.90                                     # Discharging efficiency
    f_c = ef_T/f_d                                  # Charging efficiency
    k_T = 5                                         # Capacity of storage (MV)

    # Heat pump parameters:
    capex_H = 1455000                               # CAPEX ($/MW)
    life_H = 15                                     # Storage life time (years)
    fixed_OM_H = 36370                              # Fixed TES OM cost ($/MW-year)
    p_H_fixed = 0                                   # TES energy cost ($/kWh/h)
    p_H = 0                                         # TES operating cost ($/MWh)
    eta_x = 0.95                                    # Factor deviating from Carnot efficiency
    temp_L = 13
    temp_H = 70
    eta_C = eta_x*(temp_H/(temp_H-temp_L))          # Coefficient of performance (COP)

    # Model's scope:
    hour = 24

    return (super_comp,ir,alpha,m,c,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,ef_T,f_d,f_c,k_T,capex_H,life_H,fixed_OM_H,p_H_fixed,p_H,eta_x,temp_L,temp_H,eta_C,hour,app)


def main_function():
    (super_comp,ir,alpha,m,c,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,ef_T,f_d,f_c,k_T,capex_H,life_H,fixed_OM_H,p_H_fixed,p_H,eta_x,temp_L,temp_H,eta_C,hour,app) = main_params()

    (model_dir, load_folder, results_folder) = working_directory(super_comp)

    T = main_sets(hour)

    model_solve(model_dir,load_folder,results_folder,super_comp,ir,alpha,m,c,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,
                ef_T,f_d,f_c,k_T,capex_H,life_H,fixed_OM_H,p_H_fixed,p_H,eta_x,temp_L,temp_H,eta_C,hour,app,T)


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
def model_solve(model_dir,load_folder,results_folder,super_comp,ir,alpha,m,c,capex_T,life_T,fixed_OM_T,p_T_fixed,p_T,
                ef_T,f_d,f_c,k_T,capex_H,life_H,fixed_OM_H,p_H_fixed,p_H,eta_x,temp_L,temp_H,eta_C,hour,app,T):

        # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, temp_orig, temp_desire, p_W = load_data(model_dir, load_folder, app, T, hour)

    # Storage:
    (p_TK, p_TC) = storage_data(ir, life_T, capex_T, fixed_OM_T, p_T_fixed)

    # Heat pump:
    p_HK = heatpump_data(ir, life_H, capex_H, fixed_OM_H, p_H_fixed)


    # %% Define variables and ordered set:
    model.T = Set(initialize=T, ordered=True)

    # Power rating by technology:
    model.k_H = Var(within=NonNegativeReals)  # Heat pump capacity

    # Energy capacity by technology:
    model.e_T = Var(within=NonNegativeReals)  # TES energy capacity

    # Generation by technology:
    model.g_T = Var(T, within=NonNegativeReals)  # TES discharge
    model.i_T = Var(T, within=NonNegativeReals)  # Heat pump output discharge = TES inflow
    model.d_T = Var(T, within=NonNegativeReals)  # purchased electricity

    # TES states of charges:
    model.x_T = Var(T, within=NonNegativeReals)  # Battery state of charge

    # Whole number variables:
    model.u_T = Var(within=NonNegativeIntegers)  # Number of TES units built

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # TES constraints:
    def ub_d_TES(model, t):
        return model.i_T[t] <= k_T*model.u_T
    model.ub_d_T = Constraint(T, rule=ub_d_TES)

    def ub_g_TES(model, t):
        return model.g_T[t] <= k_T*model.u_T
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

    # Heat pump output to TES inflow:
    def i_TES(model, t):
        return model.i_T[t] == eta_C *1/alpha * model.d_T[t]
    model.inflow_const = Constraint(T, rule=i_TES)

    # Market clearing condition:
    def market_clearing(model, t):
        return model.g_T[t] >= 1/1000*m*c*(temp_desire-temp_orig)
    model.mc_const = Constraint(T, rule=market_clearing)

    # Objective function:
    def obj_function(model):
        return sum(p_TK * model.u_T* k_T + p_TC * model.e_T + sum(p_T * model.g_T[t] for t in T)) \
               + sum(p_HK* model.k_H + p_H*model.i_T[t] for t in T) \
               + sum(p_W * model.g_W[t] for t in T)

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

    k_H_star = np.zeros(1)
    u_T_star = np.zeros(1)
    e_T_star = np.zeros(1)

    g_T_star = np.zeros(hour)
    i_T_star = np.zeros(hour)
    d_T_star = np.zeros(hour)
    x_T_star = np.zeros(hour)


    k_H_star = value(model.k_H)
    e_T_star = value(model.e_T)
    u_T_star = value(model.u_T)

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
    result_sheet_wg = results_book.add_worksheet('purchased electrcity')
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
    result_sheet_pr.write("A1", "number of TES unit built")
    result_sheet_pr.write("B1", "TES energy capacity (kJ)")
    result_sheet_pr.write("C1", "Heat pump capacity (kJ)")

    result_sheet_pr.write(1, 1, u_T_star)
    result_sheet_pr.write(1, 2, e_T_star)
    result_sheet_pr.write(1, 3, k_H_star)

    # write TES discharge results:
    result_sheet_bg.write("A1", "TES discharge")

    for item in T:
        result_sheet_bg.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_bg.write(1, item_2 + 1, g_T_star[item_2])

    # write purchased gen results:
    result_sheet_wg.write("A1", "Purchased electricity")

    for item in T:
        result_sheet_wg.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_wg.write(1, item_2 + 1, d_T_star[item_2])

    # TES inflow results:
    result_sheet_bi.write("A1", "TES indlow")

    for item in T:
        result_sheet_bi.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_bi.write(1, item_2 + 1, i_T_star[item_2])

    # TES SOC results:
    result_sheet_bs.write("A1", "TES SOC")

    for item in T:
        result_sheet_bs.write(0, item + 1, hour_number[item])

    for item_2 in T:
        result_sheet_bs.write(1, item_2 + 1, x_T_star[item_2])


    results_book.close()

main_function()

print("--- %s seconds ---" % (time.time() - start_time))
