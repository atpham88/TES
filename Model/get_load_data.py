
import pandas as pd
import numpy as np

#parquetfile = pd.read_parquet("C:\\Users\\atpha\\Desktop\\Temp Files\\105114-0.parquet")

def load_data(model_dir, load_folder, app, T, hour, starting_hour):

    # Hourly load
    load_data_raw = pd.read_excel(model_dir + load_folder + 'load_data.xlsx', sheet_name='1 hour', header=None)

    load_data_annual = pd.DataFrame(np.tile(load_data_raw, 1))
    load_data_annual = load_data_annual.iloc[starting_hour:hour]
    d_heating_temp = {(r, c): load_data_annual.at[r, c] for r in T for c in list(range(1))}

    d_heating = dict.fromkeys((range(hour)))

    for t in T:
        d_heating[t] = d_heating_temp[t,0]

    # Electricity price:
    p_W = 0.12                      # $/kWh

    return d_heating, p_W