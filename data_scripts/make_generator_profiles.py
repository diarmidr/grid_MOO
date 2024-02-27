"""The following code generates load profiles for use in grid_moo."""
import matplotlib.pyplot as plt
import pandas as pd
import math
# Wind and PV
"""Wind and PV profiles are generated from historical UK level data. Output data from www.gridwatch.templar.co.uk
are normalised to the capacity of the generation type that was installed in that time period (to nearest quarter where
 possible). This allows an aggregated hourly capacity factor that can be scaled up as desired."""
# Import grid level generation and demand data
data = pd.read_csv("_data/gridwatch_generator_data_2017-nov2023.csv", parse_dates=[' timestamp'], index_col=" timestamp")
# For each column of interest+0, take data and reduce to hourly resolution
data_hourly = data.resample('H').mean()
print(data_hourly)
# Now we normalise wind output to historic capacity. Have moved to quarterly resolution,as updating capacity annually
# leads to an artifact where wind production looks low in spring as capacity hadn't actually been installed yet!
# To preserve information,value in capacity_history is sum of onshore,offshore-seabed and offshore-floating respectively
# (source Energy Trends 6.1 by BEIS, https://www.gov.uk/government/statistics/energy-trends-section-6-renewables)

wind_capacity_history = {"2014-Q1": 7668+3764+0, "2014-Q2": 7998+4085+0, "2014-Q3": 8281+4426+0, "2014-Q4": 8573+4501+0,
                    "2015-Q1": 8689+4739+0, "2015-Q2": 8792+5014+0, "2015-Q3": 9003+5094+0, "2015-Q4": 9212+5094+0,
                    "2016-Q1": 9392+5087+0, "2016-Q2": 9546+5087+0, "2016-Q3": 10183+5087+0, "2016-Q4": 10833+5293+0,
                    "2017-Q1": 11965+5448+0, "2017-Q2": 12314+5646+0, "2017-Q3": 12567+6958+0, "2017-Q4": 12597+6958+30,
                    "2018-Q1": 13045+7610+30, "2018-Q2": 13142+7764+30, "2018-Q3": 13288+7980+30, "2018-Q4": 13425+8151+30,
                    "2019-Q1": 13664+8447+32, "2019-Q2": 13873+9124+32, "2019-Q3": 13960+9670+32, "2019-Q4": 13998+9856+32,
                    "2020-Q1": 13974+10082+32, "2020-Q2": 13976+10351+32, "2020-Q3": 13978+10351+32, "2020-Q4": 14075+10351+32,
                    "2021-Q1": 14115+10360+32, "2021-Q2": 14211+10625+40, "2021-Q3": 14346+11025+42, "2021-Q4": 14492+11025+80,
                    "2022-Q1": 14648+12654+80, "2022-Q2": 14648+13116+80, "2022-Q3": 14686+13768+80, "2022-Q4": 14835+13848+80,
                    "2023-Q1": 15359+14093+80, "2023-Q2": 15441+14350+80, "2023-Q3": 15469+14666+80
                    }
for index, row in data_hourly.iterrows():
    if index.month in [1, 2, 3]:
        quarter = "Q1"
    elif index.month in [4, 5, 6]:
        quarter = "Q2"
    elif index.month in [7, 8, 9]:
        quarter = "Q3"
    elif index.month in [10, 11, 12]:
        quarter = "Q2"
    data_hourly.loc[index, 'normalised_MW'] = row[' wind'] / wind_capacity_history[str(index.year)+"-" + quarter]

plt.plot(data_hourly['normalised_MW'])
plt.show()
#data_hourly.to_csv("capacity_normalised_wind_history.csv")