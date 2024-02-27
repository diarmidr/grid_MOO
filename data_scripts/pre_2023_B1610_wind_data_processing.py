import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime

row = 0
farms = ["WBURB_HH_data", "GYMRO_HH_data", "SHBA_HH_data", "WDNSW_HH_data", "WDNSO_HH_data"]
#Notes on list below: can't find 2nd unit for Humber
farms = {"HOWBO_HH_data": [1386], "HOWAO_HH_data": [1200], "SGRWO_HH_data": [1140], "MOWEO_HH_data": [950],
         "Triton_Knoll_HH_data": [857], "East_Anglia_HH_data": [714], "Walney_ext_HH_data": [660],
         "LARYO_HH_data": [630], "BEATO_HH_data": [588], "GYMRO_HH_data": [576], "RCBKO_HH_data": [573],
         "GRGBW_HH_data": [504], "Rampion_HH_data": [400], "Dudgeon_HH_data": [395], "WDNSO_HH_data": [389],
         "Walney_HH_data": [367], "GAOFO_HH_data": [353], "SHRSO_HH_data": [317], "THNTO_HH_data": [300],
         "LNCSO_HH_data": [270], "BRBEO_HH_data": [259], "WTMSO_HH_data": [210], "Humber_HH_data": [110]}
fig, ax = plt.subplots(ncols=1, nrows=len(farms))
start_date = datetime(2017, 1, 1)
end_date = datetime(2024, 1, 1)
total_cap = 0
total_output = 0
collection_for_export = {}
for key in farms:
    raw_data = pd.read_csv("data/raw_data/historic_HH_bm1610_unit_data/" + key+".csv", index_col=0, parse_dates=True, dayfirst=True)
    print(raw_data)
    #raw_data["Timestamp"] = pd.to_datetime(raw_data["Timestamp"], format='%d/%m/%Y %H:%M')
    #raw_data = raw_data.set_index(raw_data["Timestamp"])
    #raw_data = raw_data.drop("Timestamp", axis=1)
    selected_data = raw_data.loc[(raw_data.index >= start_date) &
                                 (raw_data.index <= end_date)]
    selected_data["Total"] = selected_data.sum(axis=1, numeric_only=True)
    selected_data["Normalised"] =selected_data["Total"]/farms[key][0]
    output_MWh = selected_data["Total"].sum()/2
    print(selected_data)
    print(output_MWh)
    ax[row].plot(selected_data.index, selected_data["Normalised"])
    row += 1
    # Add cap factor to farms dictionary
    print(len(selected_data))
    print(farms[key][0])
    cap_factor = output_MWh/(farms[key][0]*len(selected_data)/2)
    farms[key] += [cap_factor]
    total_cap += farms[key][0]
    total_output += output_MWh
    collection_for_export[key] = selected_data["Total"]
print(farms)
plt.show()
collection_for_export = pd.DataFrame(collection_for_export) # Convert to hourly data
collection_for_export = collection_for_export.resample("H").mean()
collection_for_export.to_csv("selected_B1610_output_hourly.csv")
