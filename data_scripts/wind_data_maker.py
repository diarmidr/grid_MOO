"""This script can be used to change raw NG generation data from 5min to hourly resolution, then normalise it based on
installed capacity. The latter means it can then be used as input for future scenario simulation where generation
capacity is a variable"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import datetime as dt

from generator_data_functions import gridwatch_data_pull, BM_reports_1620_API_pull, BM_reports_1630_API_pull

start_date = dt.datetime(2022, 1, 1)
end_date = dt.datetime(2022, 12, 31)

# Option on how to generate the nuclear profile
#nuclear_profile = "Historic"
nuclear_profile = "Idealised"

# This is data on installed capacity per generator class, and will be used to normalise historic output
capacity_data = pd.read_csv("data/historic_capacity.csv")
#wind_data_BM_1610 = BM_reports_1630_API_pull(start_date, end_date)
wind_data = BM_reports_1630_API_pull(start_date, end_date)
wind_data.to_csv("B1630_data.csv")
# for idx, row in wind_data.iterrows():
#     # Determine quarter of year to find installed capacity
#     q = math.ceil(idx.month / 3)
#     wind_data.loc[idx, 'offshore_wind_norm'] = row.Offshore_wind / capacity_data.loc[(capacity_data['year'] == idx.year) &
#                                                                     (capacity_data['quarter'] == q)]['offshore_wind'].values[0]
#     wind_data.loc[idx, 'onshore_wind_norm'] = row.Onshore_wind / capacity_data.loc[(capacity_data['year'] == idx.year) &
#                                                                     (capacity_data['quarter'] == q)]['onshore_HH_metered'].values[0]
# plt.stackplot(wind_data.index, wind_data['onshore_wind_norm'], wind_data['offshore_wind_norm'],
#               baseline="zero", labels=["Onshore wind", "Offshore wind"], colors=["blue", "cyan"])
# # plt.plot(wind_data['onshore_wind_norm'], label="cap_normalised_onshore_wind")
# # plt.plot(wind_data['offshore_wind_norm'], label="cap_normalised_offshore_wind")
# plt.legend()
# plt.show()
# # This data is nuclear and pv, which is taken from gridwatch.templar.co.uk, who take PV from Sheffield portal
# nuc_pv_demand_data = gridwatch_data_pull("data/gridwatch_2014-2023.csv", start_date, end_date)
# # Now we normalise both data sets against the installed capacity in each year and quarter
# for idx, row in nuc_pv_demand_data.iterrows():
#     # Determine quarter of year
#     q = math.ceil(idx.month / 3)
#     nuc_pv_demand_data.loc[idx, 'PV_norm'] = row.solar / capacity_data.loc[(capacity_data['year'] == idx.year) &
#                                                                     (capacity_data['quarter'] == q)]['PV'].values[0]
#     if nuclear_profile == "Historic":
#         nuc_pv_demand_data.loc[idx, 'nuclear_norm'] = row.nuclear / capacity_data.loc[(capacity_data['year'] == idx.year) &
#                                                                         (capacity_data['quarter'] == q)]['nuclear'].values[0]
#
# if nuclear_profile == "Idealised":
#     # Make an idealised nuclear profile based on a 1 month in 24 maintenance schedule, but only in Apr to September
#     # 0.9 comes fromm https://www.eia.gov/todayinenergy/detail.php?id=51978
#     # 0.8 is approximation of historic UK load factor
#     for idx, row in nuc_pv_demand_data.iterrows():
#         if idx.month in [1, 2, 3, 10, 11, 12]:
#             nuc_pv_demand_data.loc[idx, 'nuclear_norm'] = 0.8+1/12
#         else:
#             nuc_pv_demand_data.loc[idx, 'nuclear_norm'] = 0.8-1/12
# # Clean NaNs and 0s out of nuclear series
# for t in range(len(nuc_pv_demand_data)):
#     if t >= 1:
#         last_good_value = nuc_pv_demand_data['nuclear_norm'][t-1]
#         if math.isnan(nuc_pv_demand_data['nuclear_norm'][t]):
#             print("found a NaN at row ", t)
#             nuc_pv_demand_data['nuclear_norm'][t] = last_good_value
#         if nuc_pv_demand_data['nuclear_norm'][t] == 0:
#             nuc_pv_demand_data['nuclear_norm'][t] = last_good_value
#
#
#
# # for idx, row in wind_data.iterrows():
# #     print (idx.year)
# #     wind_data.loc[idx, 'onshore_wind_norm'] = row.onshore_wind / capacity_data.loc[idx.year]['onshore Wind']
# #     wind_data.loc[idx, 'offshore_wind_norm'] = row.offshore_wind / capacity_data.loc[idx.year]['offshore Wind']
# print('normalisation_finished_@', dt.datetime.now())
# #plt.plot(nuc_pv_demand_data['PV_norm'], label="cap_normalised_PV")
# #plt.plot(nuc_pv_demand_data['nuclear_norm'], label="cap_normalised_nuclear")
#
# all_data = nuc_pv_demand_data.join(wind_data)
# all_data.to_csv('nuc_pv_demand_profiles.csv')
# Below bit needs fixing, just reports cap factor for each tech per year
# cap_factor_dict = {"wind": [],
#                    "PV": [],
#                    "nuclear": []}
#
# for i in range(2017, 2023):
#     PV_mean = nuc_pv_demand_data[nuc_pv_demand_data.index.year == i].PV_norm.mean()
#     nuclear_mean = nuc_pv_demand_data[nuc_pv_demand_data.index.year == i].nuclear_norm.mean()
#     cap_factor_dict["PV"] += [PV_mean]
#     cap_factor_dict["nuclear"] += [nuclear_mean]
# print(cap_factor_dict)



