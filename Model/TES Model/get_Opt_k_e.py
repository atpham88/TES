"""
An Pham
Updated 07/10/2022
TES Model for Building and Water Heating
Get optimal TES storage capacity and heat pump capacity for specific building
Then using optimal sizings of TEs and heat pump in TES model
"""

from pyomo.environ import *
from pyomo.opt import SolverFactory
import time

from get_load_data import load_data
from get_COP_params import est_COP
from get_fan_load import est_fan_load

from calendar import monthrange
from datetime import date

start_time = time.time()

# %% Main parameters:
def main_params(year, mon_to_run, super_comp, used_cop, cop_type,
                p_T, ef_T, f_d, ir, single_building, city_to_run, building_no, building_id):

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
    return (super_comp, ir, p_T, ef_T, f_d, f_c, hour, starting_hour, mon_to_run, cop_type, used_cop,
            single_building, city_to_run, building_no, building_id)


def main_function_Opt_k_e(year, mon_to_run, super_comp, used_cop, cop_type, curb_H, pricing, p_T, ef_T, f_d, ir,
                          single_building, city_to_run, building_no, building_id, city):

    (super_comp, ir, p_T, ef_T, f_d, f_c, hour, starting_hour,
     mon_to_run, cop_type, used_cop, single_building,
     city_to_run, building_no, building_id) = main_params(year, mon_to_run, super_comp, used_cop, cop_type, p_T, ef_T, f_d,
                                                          ir, single_building, city_to_run, building_no, building_id)
    (model_dir, load_folder) = working_directory(super_comp, single_building, city_to_run)
    T = main_sets(hour)
    k_H_star = model_solve_Opt_k_e(model_dir, load_folder, super_comp, ir, p_T, ef_T, f_d, f_c, hour, T, starting_hour,
                                   mon_to_run, cop_type, used_cop, pricing, single_building, city_to_run, building_no, building_id, curb_H, city)
    return k_H_star

# %% Set working directory:
def working_directory(super_comp, single_building, city_to_run):
    if super_comp:
        model_dir = '/nfs/turbo/seas-mtcraig/anph/TES/Data/'
        load_folder = '400_Buildings_EB/' + city_to_run + '/'
    else:
        model_dir = 'C:/Users/atpha/Documents/Postdocs/Projects/TES/Data/'
        load_folder = '400_Buildings_EB/' + city_to_run + '/'
    return model_dir, load_folder

# %% Define set:
def main_sets(hour):
    T = list(range(hour))  # Set of hours to run                               # Set of hours to run
    return T

# %% Solving HDV model:
def model_solve_Opt_k_e(model_dir, load_folder, super_comp, ir, p_T, ef_T, f_d, f_c,
                        hour, T, starting_hour, mon_to_run, cop_type, used_cop, pricing,
                        single_building, city_to_run, building_no, building_id, curb_H, city):


    # %% Set model type - Concrete Model:
    model = ConcreteModel(name="TES_model")

    # Load data:
    d_heating, p_W, peakLoad, load_weight = load_data(super_comp, model_dir, load_folder, T, hour, city, starting_hour, building_id, pricing, curb_H)
    cop = est_COP(model_dir, T, hour, starting_hour, cop_type, used_cop, city)

    # Fan load as fraction of total heating load (for both ASHP and TES discharging):
    fan_load_ratio = est_fan_load(super_comp, model_dir, load_folder, T, hour, starting_hour, cop_type, used_cop, city, building_id, pricing, curb_H)

    # %% Define variables and ordered set:
    model.T = Set(initialize=T, ordered=True)

    # Generation by technology:
    model.k_H = Var(within=NonNegativeReals)
    model.g = Var(T, within=NonNegativeReals)                       # Total output from heat pump (kWh)
    model.d_T = Var(T, within=NonNegativeReals)                     # purchased electricity (kWh)

    # %% Formulate constraints and  objective functions:
    # Constraints:
    # Heat pump's total load:
    def hp_load_tot(model, t):
        return model.g[t] <= model.k_H
    model.hp_load_tot_const = Constraint(T, rule=hp_load_tot)
    # Electricity purchased needs to be enough to power heat pump
    def i_TES(model, t):
        return model.d_T[t] >= model.g[t]/cop[t]
    model.inflow_const = Constraint(T, rule=i_TES)

    def market_clearing(model, t):
        return model.g[t]*(1-fan_load_ratio[t]) >= d_heating[t]
    model.mc_const = Constraint(T, rule=market_clearing)

    # Objective function:
    def obj_function(model):
        return sum(p_W[t] * model.d_T[t] for t in T) + model.k_H*999
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

    k_H_star = value(model.k_H)

    return k_H_star


print("--- %s seconds ---" % (time.time() - start_time))
