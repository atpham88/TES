
import pandas as pd
import numpy as np

def est_COP(model_dir, app, T, hour, starting_hour, cop_type):

    load_cop50_raw = pd.read_excel(model_dir  + 'cop_temp.xlsx', sheet_name='cop NEEP50')
    load_cop90_raw = pd.read_excel(model_dir + 'cop_temp.xlsx', sheet_name='cop NEEP90')
    load_copDOE_raw = pd.read_excel(model_dir + 'cop_temp.xlsx', sheet_name='cop DOE')

    ext_temp = pd.read_excel(model_dir + 'ext_temp.xlsx')
    ext_temp['COP NEEP 50'] = 0
    ext_temp['COP NEEP 90'] = 0
    ext_temp['COP DOE'] = 0

    for i in list(range(len(ext_temp))):
        load_cop50_raw['temp_diff'] = abs(ext_temp['MI C'][i] - load_cop50_raw['temp C'])
        load_cop90_raw['temp_diff'] = abs(ext_temp['MI C'][i] - load_cop90_raw['temp C'])
        load_copDOE_raw['temp_diff'] = abs(ext_temp['MI C'][i] - load_copDOE_raw['temp C'])

        min_id50 = load_cop50_raw['temp_diff'].idxmin(axis=1)
        min_id90 = load_cop90_raw['temp_diff'].idxmin(axis=1)
        min_idDOE = load_copDOE_raw['temp_diff'].idxmin(axis=1)

        ext_temp.iloc[i,1] = load_cop50_raw['COP NEEP50'][min_id50]
        ext_temp.iloc[i,2] = load_cop90_raw['COP NEEP90'][min_id90]
        ext_temp.iloc[i,3] = load_copDOE_raw['COP DOE'][min_idDOE]

    if cop_type == 'DOE':
        cop = ext_temp['COP DOE']
    elif cop_type == 'NEEP90':
        cop = ext_temp['COP NEEP90']
    elif cop_type == 'NEEP50':
        cop = ext_temp['COP NEEP50']

    cop = cop.iloc[starting_hour:hour]
    cop = cop.to_dict()

    return cop