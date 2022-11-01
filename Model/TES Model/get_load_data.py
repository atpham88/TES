
import pandas as pd
import numpy as np
import zipfile
from datetime import datetime

#parquetfile = pd.read_parquet("C:\\Users\\atpha\\Desktop\\Temp Files\\105114-0.parquet")

def load_data(super_comp, model_dir, load_folder, T, hour, starting_hour, building_id, pricing, curb_H):

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

    peakLoad = float(load_data_annual.max())

    load_weight = pd.DataFrame(np.zeros((len(load_data_annual), 1)))

    for t in T:
        if load_data_annual[0][t] > peakLoad * 0.7:
            load_weight[0][t] = 9999999

    load_weight_temp = {(r, c): load_weight.at[r, c] for r in T for c in list(range(1))}
    load_weight = dict.fromkeys((range(hour)))

    d_heating_temp = {(r, c): load_data_annual.at[r, c] for r in T for c in list(range(1))}
    d_heating = dict.fromkeys((range(hour)))
    for t in T:
        d_heating[t] = d_heating_temp[t,0]
        load_weight[t] = load_weight_temp[t,0]

    # Electricity price:
    date_str = '1/1/2019'
    start = pd.to_datetime(date_str) - pd.Timedelta(days=365)
    hourly_periods = 8760
    drange = pd.date_range(start, periods=hourly_periods, freq='H')
    data = list(range(len(drange)))

    # create data frame with drange index
    p_W_temp = pd.DataFrame(data, index=drange)
    p_W_temp = p_W_temp.reset_index()
    p_W_temp = p_W_temp.rename(columns={"index": "timestamp"})
    p_W_temp = p_W_temp.rename(columns={0: "dt"})
    p_W_temp['hour'] = 0
    p_W_temp['day of week'] = 0
    p_W_temp['month'] = 0
    p_W_temp['rate'] = 0.183

    if pricing == 'ToD':
        p_W_temp['rate'] = 0.12
        for t in data:
            p_W_temp['dt'][t] = datetime.strptime(str(p_W_temp['timestamp'][t]), '%Y-%m-%d %H:%M:%S')
            p_W_temp['hour'][t] = p_W_temp['dt'][t].strftime('%H')
            p_W_temp['day of week'][t] = p_W_temp['dt'][t].strftime('%A')
            p_W_temp['month'][t] = p_W_temp['dt'][t].strftime('%m')
            if int(p_W_temp['month'][t]) <=5 and int(p_W_temp['month'][t]) >= 10:
                if int(p_W_temp['hour'][t]) >=11 and int(p_W_temp['hour'][t]) <=19:
                    p_W_temp['rate'][t] = 0.2
            else:
                if int(p_W_temp['hour'][t]) >=11 and int(p_W_temp['hour'][t]) <=19:
                    p_W_temp['rate'][t] = 0.23

    p_W_temp2 = p_W_temp['rate']
    p_W_temp2 = p_W_temp2.to_frame()
    p_W_temp2 = p_W_temp2.rename(columns={'rate':0})
    p_W_temp3 = {(r, c): p_W_temp2.at[r, c] for r in T for c in list(range(1))}
    p_W = dict.fromkeys((range(hour)))
    for t in T:
        p_W[t] = p_W_temp3[t, 0]


    return d_heating, p_W, peakLoad, load_weight