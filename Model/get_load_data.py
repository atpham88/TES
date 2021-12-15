
import pandas as pd
import numpy as np

def load_data(model_dir, load_folder, app, T, hour):

    # Hourly load
    load_data_raw = pd.read_excel(model_dir + load_folder + 'load_data.xlsx', sheet_name=app, header=None)
    load_data_annual = pd.DataFrame(np.tile(load_data_raw, 1))
    d_heating_temp = {(r, c): load_data_annual.at[r, c] for r in list(range(1)) for c in T}

    d_heating = dict.fromkeys((range(hour)))
    for t in T:
        d_heating[t] = d_heating_temp[0,t]

    # Electricity price:
    p_W = 0.12                      # $/kWh

    return d_heating, p_W