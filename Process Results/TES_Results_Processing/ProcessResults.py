
import glob
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import matplotlib as mpl
from shapely.geometry import Point
import plotly_express as px
import matplotlib.image as mpimg
import numpy as np

# Results folder:
ResultsFolder = "C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\TES\Results\\Detroit\\All\\"
salt_type = 'MgSO4'

# Combine results for all buildings into one place:
all_files_no_TES = glob.glob(ResultsFolder + "*False*.xlsx")
all_files_w_TES = glob.glob(ResultsFolder + "*MgSO4*.xlsx")

# Total costs:
sheetname = 'total cost'
li = []
li2 = []
for filename in all_files_no_TES:
    df = pd.read_excel(filename, sheet_name=sheetname)
    li.append(df)
for filename in all_files_w_TES:
    df = pd.read_excel(filename, sheet_name=sheetname)
    li2.append(df)

cost_noTES = pd.concat(li, axis=0)
cost_wTES = pd.concat(li2, axis=0)

cost_noTES.to_excel('C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\TES\Results\\Detroit\\Compiled\\' + 'total cost all building - no TES.xlsx')
cost_wTES.to_excel('C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\TES\Results\\Detroit\\Compiled\\' + 'total cost all building'
                   +'-' + salt_type +'.xlsx')