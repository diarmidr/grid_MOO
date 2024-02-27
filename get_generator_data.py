"""This is just a short script where raw generator output data is obtained from various functions"""
from generator_data_functions import gridwatch_data_pull, BM_reports_1610_API_pull, \
    onshore_wind_BM_reports_1630_API_pull
import datetime as dt
start_date = dt.datetime(2023, 1, 3)
end_date = dt.datetime(2023, 1, 3)

# Use this one to get PV, demand or other series downloaded from gridwatch (not good for wind)
# col = "solar"  # Change col to "demand" if required
# data = gridwatch_data_pull("data/raw_data/demand+PV_from_gridwatch/gridwatch_2017-2023.csv", start_date, end_date, col)
# data.to_csv("PV_profile_2017-2023.csv")

# Use this one to get HH metered onshore wind from B1630 api
data = onshore_wind_BM_reports_1630_API_pull(start_date, end_date)
data.to_csv("onshore_wind_hourly_from_B1630.csv")
