

import pandas as pd
import numpy as np
from get_load_data import load_data

def est_fan_load(super_comp, model_dir, load_folder, T, hour, starting_hour, cop_type, used_cop, city, building_id, pricing, curb_H):

    fan_load_raw = pd.read_csv(model_dir  + 'heating_load_cleaned.csv')
    heating_load, p_W, peakLoad, load_weight = load_data(super_comp, model_dir, load_folder, T, hour, city, starting_hour, building_id, pricing, curb_H)
    fan_load_ratio = pd.DataFrame(np.zeros((len(heating_load), 1)))

    for i in list(range(len(heating_load))):
        fan_load_raw['diff'] = abs(heating_load[i] - fan_load_raw['heatingload'])
        min_id = fan_load_raw['diff'].idxmin(axis=0)

        fan_load_ratio[0][i] = fan_load_raw['fanratio'][min_id]
        #print(i)

    fan_load_ratio = fan_load_ratio[0].iloc[starting_hour:starting_hour+hour]
    fan_load_ratio = fan_load_ratio.reset_index()
    fan_load_ratio = fan_load_ratio.drop(['index'],axis=1)
    fan_load_ratio = fan_load_ratio.squeeze()
    fan_load_ratio = fan_load_ratio.to_dict()

    return fan_load_ratio