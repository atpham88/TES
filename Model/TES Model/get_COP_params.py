
import pandas as pd

def est_COP(model_dir, T, hour, starting_hour, cop_type, used_cop, city):

    if city == 'Los Angeles':
        city = 'LA'
    elif city == 'New York':
        city = 'NY'

    if used_cop == "Waite_Modi":
        load_cop50_raw = pd.read_excel(model_dir  + 'cop_temp.xlsx', sheet_name='cop NEEP50')
        load_cop90_raw = pd.read_excel(model_dir + 'cop_temp.xlsx', sheet_name='cop NEEP90')
        load_copDOE_raw = pd.read_excel(model_dir + 'cop_temp.xlsx', sheet_name='cop DOE')

        ext_temp = pd.read_excel(model_dir + 'weather/' + 'ext_temp_' + city + '.xlsx')
        ext_temp['COP NEEP 50'] = 0.0000
        ext_temp['COP NEEP 90'] = 0.0000
        ext_temp['COP DOE'] = 0.0000

        for i in list(range(len(ext_temp))):
            load_cop50_raw['temp_diff'] = abs(ext_temp['temp'][i] - load_cop50_raw['temp C'])
            load_cop90_raw['temp_diff'] = abs(ext_temp['temp'][i] - load_cop90_raw['temp C'])
            load_copDOE_raw['temp_diff'] = abs(ext_temp['temp'][i] - load_copDOE_raw['temp C'])

            min_id50 = load_cop50_raw['temp_diff'].idxmin(axis=0)
            min_id90 = load_cop90_raw['temp_diff'].idxmin(axis=0)
            min_idDOE = load_copDOE_raw['temp_diff'].idxmin(axis=0)

            ext_temp['COP NEEP 50'][i] = load_cop50_raw['COP NEEP50'][min_id50]
            ext_temp['COP NEEP 90'][i] = load_cop90_raw['COP NEEP90'][min_id90]
            ext_temp['COP DOE'][i] = load_copDOE_raw['COP DOE'][min_idDOE]
            #print(i)

        if cop_type == 'DOE':
            cop = ext_temp['COP DOE']
        elif cop_type == 'NEEP90':
            cop = ext_temp['COP NEEP 90']
        elif cop_type == 'NEEP50':
            cop = ext_temp['COP NEEP 50']

    elif used_cop == "Resstock":
        load_cop_RS_raw = pd.read_excel(model_dir + 'cop_resstock.xlsx', header=None)
        cop = load_cop_RS_raw.squeeze()

    cop = cop.iloc[starting_hour:starting_hour+hour]
    cop = cop.reset_index()
    cop = cop.drop(['index'],axis=1)
    cop = cop.squeeze()
    cop = cop.to_dict()

    return cop