
import pandas as pd
import numpy as np
import zipfile
from datetime import datetime

def load_data(super_comp, model_dir, load_folder, T, hour, city, starting_hour, building_id, pricing, curb_H):

    # Read resstock results summary folder:
    resstock_results = pd.read_csv(model_dir + load_folder + 'results.csv')
    resstock_results = resstock_results[resstock_results['building_characteristics_report.location_city'].str.contains(city) == True]
    resstock_results = resstock_results.sort_values(by='build_existing_model.building_id')
    resstock_results['build_existing_model.building_id'] = resstock_results['build_existing_model.building_id'] % 400
    resstock_results.loc[resstock_results['build_existing_model.building_id'] == 0, 'build_existing_model.building_id'] = 400
    resstock_results = resstock_results.reset_index()
    resstock_results = resstock_results.drop(['index'], axis=1)

    resstock_building_id = building_id + 1

    folder_id = resstock_results.loc[resstock_results['build_existing_model.building_id'] == resstock_building_id, '_id']
    folder_id = folder_id.reset_index()
    folder_id = folder_id.drop(['index'], axis=1)
    folder_id = folder_id.iloc[0,0]

    if not super_comp:
        archive = zipfile.ZipFile(model_dir + load_folder + folder_id + '/' + 'data_point.zip')
    elif super_comp:
        archive = zipfile.ZipFile(model_dir + load_folder + folder_id + '/' + 'data_point.zip')

    load_data_path = archive.extract('enduse_timeseries.csv', model_dir + load_folder + folder_id + '/')
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

    if city == 'Detroit':
        p_W_temp['rate'] = 0.183
    elif city == 'Los Angeles':
        p_W_temp['rate'] = 0.257
    elif city == 'New York':
        p_W_temp['rate'] = 0.249
    elif city == 'Orlando':
        p_W_temp['rate'] = 0.16
    elif  city == 'Seattle':
        p_W_temp['rate'] = 0.118
    elif city == 'Atlanta':
        p_W_temp['rate'] = 0.16
    elif city == 'Minneapolis':
        p_W_temp['rate'] = 0.17
    elif city == 'Phoenix':
        p_W_temp['rate'] = 0.14
    elif city == 'Boston':
        p_W_temp['rate'] = 0.291
    elif city == 'Dallas':
        p_W_temp['rate'] = 0.12
    elif city == 'Boulder':
        p_W_temp['rate'] = 0.15
    elif city == 'Chicago':
        p_W_temp['rate'] = 0.151

    if pricing == 'ToD':
        if city == 'Detroit':
            off_peak_rate = 0.1673
            on_peak_rate_winter = 0.1809
            on_peak_rate_summer = 0.2240
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 15
            on_peak_hr_end = 19
        elif city == 'Los Angeles':
            off_peak_rate = 0.16826
            on_peak_rate_winter = 0.21659
            on_peak_rate_summer = 0.21659
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 10
            on_peak_hr_end = 20
        elif city == 'New York':
            off_peak_rate = 0.0233
            on_peak_rate_winter = 0.1223
            on_peak_rate_summer = 0.3305
            winter_month_start = 11
            winter_month_end = 5
            on_peak_hr_start = 20
            on_peak_hr_end = 24
        elif city == 'Orlando':
            off_peak_rate = 0.06520
            on_peak_rate_winter = 0.08828
            on_peak_rate_summer = 0.08828
            winter_month_start = 11
            winter_month_end = 5
            on_peak_hr_start = 18
            on_peak_hr_end = 21
        elif city == 'Seattle':
            off_peak_rate = 0.08
            on_peak_rate_winter = 0.15
            on_peak_rate_summer = 0.15
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 6
            on_peak_hr_end = 24
        elif city == 'Atlanta':
            off_peak_rate = 0.012614
            on_peak_rate_winter = 0.117993
            on_peak_rate_summer = 0.117993
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 14
            on_peak_hr_end = 19
        elif city == 'Minneapolis':
            off_peak_rate = 0.05171
            on_peak_rate_winter = 0.21408
            on_peak_rate_summer = 0.25879
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 9
            on_peak_hr_end = 21
        elif city == 'Phoenix':
            off_peak_rate = 0.12345
            on_peak_rate_winter = 0.32543
            on_peak_rate_summer = 0.34396
            winter_month_start = 11
            winter_month_end = 4
            on_peak_hr_start = 16
            on_peak_hr_end = 19
        elif city == 'Boston':
            off_peak_rate = 0.13477
            on_peak_rate_winter = 0.28783
            on_peak_rate_summer = 0.28783
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 7
            on_peak_hr_end = 20
        elif city == 'Dallas':
            off_peak_rate = 0.077926
            on_peak_rate_winter = 0.245241
            on_peak_rate_summer = 0.245241
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 13
            on_peak_hr_end = 19
        elif city  == 'Boulder':
            off_peak_rate = 0.12
            on_peak_rate_winter = 0.19
            on_peak_rate_summer = 0.19
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 15
            on_peak_hr_end = 19
        elif city == 'Chicago':
            off_peak_rate = 0.12447
            on_peak_rate_winter = 0.16117
            on_peak_rate_summer = 0.16117
            winter_month_start = 10
            winter_month_end = 5
            on_peak_hr_start = 14
            on_peak_hr_end = 19

        p_W_temp['rate'] = off_peak_rate
        for t in data:
            p_W_temp['dt'][t] = datetime.strptime(str(p_W_temp['timestamp'][t]), '%Y-%m-%d %H:%M:%S')
            p_W_temp['hour'][t] = p_W_temp['dt'][t].strftime('%H')
            p_W_temp['day of week'][t] = p_W_temp['dt'][t].strftime('%A')
            p_W_temp['month'][t] = p_W_temp['dt'][t].strftime('%m')
            # If in the winter month:
            if int(p_W_temp['month'][t]) <=winter_month_end and int(p_W_temp['month'][t]) >= winter_month_start:
                # Rate within on-peak hours:
                if int(p_W_temp['hour'][t]) >=on_peak_hr_start and int(p_W_temp['hour'][t]) <=on_peak_hr_end:
                    p_W_temp['rate'][t] = on_peak_rate_winter
            else:
                if int(p_W_temp['hour'][t]) >=on_peak_hr_start and int(p_W_temp['hour'][t]) <=on_peak_hr_end:
                    p_W_temp['rate'][t] = on_peak_rate_summer

    p_W_temp2 = p_W_temp['rate']
    p_W_temp2 = p_W_temp2.to_frame()
    p_W_temp2 = p_W_temp2.rename(columns={'rate':0})
    p_W_temp3 = {(r, c): p_W_temp2.at[r, c] for r in T for c in list(range(1))}
    p_W = dict.fromkeys((range(hour)))
    for t in T:
        p_W[t] = p_W_temp3[t, 0]

    return d_heating, p_W, peakLoad, load_weight