
import pandas as pd
import numpy as np
import zipfile

#parquetfile = pd.read_parquet("C:\\Users\\atpha\\Desktop\\Temp Files\\105114-0.parquet")

def load_data(super_comp, model_dir, load_folder, T, hour, starting_hour, building_id):

    # Read resstock results summary folder:
    resstock_results = pd.read_csv(model_dir + load_folder + 'results.csv')
    resstock_building_id = building_id + 1

    folder_id = resstock_results.loc[resstock_results['build_existing_model.building_id'] == resstock_building_id, '_id']
    folder_id = folder_id.reset_index()
    folder_id = folder_id.drop(['index'], axis=1)
    folder_id = folder_id.iloc[0,0]

    if super_comp == 0:
        archive = zipfile.ZipFile(model_dir + load_folder + folder_id + '\\' + 'data_point.zip')
    elif super_comp == 1:
        archive = zipfile.ZipFile(model_dir + load_folder + folder_id + '/' + 'data_point.zip')

    load_data_path = archive.extract('enduse_timeseries.csv', model_dir + load_folder + folder_id + '\\')
    load_data_raw = pd.read_csv(load_data_path)
    archive.close()

    # Hourly load
    load_data_annual = load_data_raw['electricity_heating_kwh']
    load_data_annual = load_data_annual.iloc[starting_hour:starting_hour+hour]
    load_data_annual = load_data_annual.reset_index()
    load_data_annual = load_data_annual.drop(['index'], axis=1)
    load_data_annual = load_data_annual.rename(columns={'electricity_heating_kwh':0})

    d_heating_temp = {(r, c): load_data_annual.at[r, c] for r in T for c in list(range(1))}
    d_heating = dict.fromkeys((range(hour)))
    for t in T:
        d_heating[t] = d_heating_temp[t,0]

    # Electricity price:
    p_W = 0.12                      # $/kWh

    return d_heating, p_W