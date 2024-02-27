"""This script takes hourly generator output data at UK level and normalises it to installed capacity. Diarmid Roberts
2024-02-12"""
import matplotlib.pyplot as plt
import pandas as pd
import math

# This is data on installed capacity per generator class, and will be used to normalise historic output
capacity_data = pd.read_csv("data/historic_capacity_data.csv")
###############################################################################################################
# These are the four things that should be changed to move between PV, offshore wind,onshore wind and nuclear #
###############################################################################################################
# Source data should have a timestamp col that can be converted to a datetime object index
source = pd.read_csv("data/hourly_data_for_normalisation/onshore_wind_hourly_2017-2023_B1630.csv",
                                index_col=0, parse_dates=True, dayfirst=True)  # Change csv string, if BM data pass dayfirst=True
source_col = "Onshore_wind"  # The column in the source CSV that contains data we want.
capacity_col = "onshore_HH_corr."  # This is the appropriate column in the capacity history file
output_file_name = "normalised_onhore_wind_profile_2017-2023.csv"


norm_data = pd.DataFrame()
for idx, row in source.iterrows():
    # Determine quarter of year to find installed capacity
    q = math.ceil(idx.month / 3)
    norm_data.loc[idx, 'output_as_frac_of_cap'] = row[source_col] / capacity_data.loc[(capacity_data['year'] == idx.year) &
                                                                    (capacity_data['quarter'] == q)][capacity_col].values[0]

norm_data.to_csv(output_file_name)


