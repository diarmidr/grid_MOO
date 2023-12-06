"""The following code generates load profiles for use in grid_moo."""
import matplotlib.pyplot as plt
import pandas as pd
import math
# Wind and PV
"""Wind and PV profiles are generated from historical UK level data. Output data from www.gridwatch.templar.co.uk
are normalised to the capacity of the generation type that was installed in that time period (to nearest quarter where
 possible). This allows an aggregated hourly capacity factor that can be scaled up as desired."""
# Import grid level generation and demand data
data = pd.read_csv("gridwatch_2017-2023.csv", parse_dates=[' timestamp'], index_col=" timestamp")
# For each column of interest, take data and reduce to hourly resolution
data_hourly = data.resample('H').mean()
#print(data_hourly)

capacity_history = {"2015": 13602,
                    "2016": 16218,
                    "2017": 19387,
                    "2018": 21700,
                    "2019": 23950,
                    "2020": 24485,
                    "2021": 25730,
                    "2022": 25730
                    }
for index, row in data_hourly.iterrows():
    data_hourly.loc[index, 'normalised_MW'] = row[' wind']/ capacity_history[str(index.year)]

plt.plot(data_hourly['normalised_MW'])
plt.show()
#data_hourly.to_csv("capacity_normalised_wind_history.csv")