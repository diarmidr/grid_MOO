import pandas as pd
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt

def gridwatch_data_pull(file, start_date, end_date, col):
    """This function pulls 5 min generation output data from the as-downloaded CSV from gridwatch.templar.co.uk
    then converts it to hourly timestep."""
    print('started PV and nuclear data pull from gridwatch.templar.co.uk_@', dt.datetime.now())
    # Import CSV to DataFrame, discarding all but listed columns
    data = pd.read_csv(file, index_col=1, parse_dates=True)
    # remove erroneous space at start of col names
    data.rename(columns={' solar': 'solar',
                         ' demand': 'demand'}, inplace=True)
    # data['timestamp'] = data.apply(
    #     lambda row: dt.datetime(int(row.timestamp[1:5]), int(row.timestamp[6:8]), int(row.timestamp[9:11]),
    #                             int(row.timestamp[12:14]), int(row.timestamp[15:17])), axis=1)
    downsampled = data.resample("H").mean()[col]
    # Downsampling automatically makes timestamp the index
    #filtered = downsampled[start_date:end_date]

    return downsampled

def BM_reports_1610_API_pull(start_date, end_date):
    """Due to uncertainty around embedded generation, I've made this function to aggregate known HH metered wind farms
    in order to get a representative load profile for the ensemble. Goes like this:
    1) Obtain data for a balancing mechanism unit (or several units belonging to one site)
    2) Clean any outages.
    3) Divided output by capacity of installation to get load factor."""
    # This dictionary details the capacity of an installation (MW), and the BM sub-units it comprises (for API query).
    offshore_installations = {"LARYO": [630, ["-1", "-2", "-3", "-4"], "London Array"]}
    offshore_installations = {"HOWAO": [1200, ["-1", "-2", "-3"], "Hornsea A"]}
    offshore_installations = {"HOWBO": [1386, ["-1", "-2", "-3"], "Hornsea B"]}
    offshore_installations = {"SGRWO": [1140, ["-1", "-2", "-3", "-4", "-5", "-6"], "Seagreen"]}
    offshore_installations = {"MOWEO": [950, ["-1", "-2", "-3"], "Moray East"]}
    offshore_installations = {"TKNEW": [857.25/2, ["-1"], "Triton Knoll East"],
                              "TKNWW": [857.25/2, ["-1"], "Triton Knoll West"]}
    offshore_installations = {"EAAO": [714, ["-1", "-2"], "East Anglia"]}
    offshore_installations = {"WALNYO": [660, ["-3", "-4"], "Walney Extension"]}
    offshore_installations = {"WALNYO": [660, ["-3", "-4"], "Walney Extension"]}  # No data...
    offshore_installations = {"WALNYO": [660, ["-1", "-2"], "Walney Extension?"],
                              "WALNYW": [660, ["-1", "-2"], "Walney"]}  # No data
    offshore_installations = {"LARYO": [630, ["-1", "-2", "-3", "-4"], "London Array"]}
    offshore_installations = {"BEATO": [588, ["-1", "-2", "-3", "-4"], "Beatrice"]}

    offshore_installations = {"RCBKO": [588, ["-1", "-2"], "Race Bank"]}
    offshore_installations = {"GRGBW": [504, ["-1", "-2", "-3"], "Greater Gabbard"]}
    offshore_installations = {"GANW": [353, ["-11", "-13", "-22", "-24"], "Galloper"],
                              "RMPNO": [400, ["-1", "-2"], "Rampion"],
                              "DDGNO": [395, ["-1", "-2", "-3", "-4"], "Dudgeon"]}
    offshore_installations = {"SHRHW": [317, ["-1", "-2"], "Sheringham Shoal"],
                              "THNTO": [300, ["-1", "-2"], "Thanet"]}  # Can't seem to get data for these.
    offshore_installations = {"BURBO": [317, [""], "Burbo Bank"],
                              "BRBEO": [200, ["-1"], "Burbo bank extension"]}  # Can't find start of data
    offshore_installations = {"HMGTO": [219, ["-1", "-2"], "Humber Gateway"],
                              "WTMSO": [200, ["-1"], "Westermost Rough"]}  # Can't find start of data
    offshore_installations = {"GYMRW": [500, ["-1", "-2"], "Gwynt y Mor 1 and 2"],
                              "GYMR": [500, ["-26", "-28"], "Gwynt y Mor West"],
                              "GYMR": [500, ["-15", "-16"], "Gwynt y Mor East"]}
    offshore_installations = {"WDNSO": [500, ["-1", "-2"], "WDNSW"],
                              "WDNSW": [500, ["-1", "-2"], "WDNSO"],
                              "SHBA": [1000, ["-1", "-2"], "SHBA"]}
    offshore_installations = {"GANW": [353, ["-11", "-13", "-22", "-24"], "Galloper"]}
    offshore_installations = {"THNTO": [300, ["-1", "-2"], "Thanet"]}  # F all data
    date = start_date
    #############################
    # Parse dates to API format #
    #############################
    # Need to set up dictionary structure first so data can be added by iteration
    offshore_dict_multi_day = {"Timestamp": []}
    for key in offshore_installations:
        for sub_unit in offshore_installations[key][1]:
            new_key = key+sub_unit
            offshore_dict_multi_day[new_key] = []
    while date <= end_date:
        print(date)
        if date.month < 10:
            month = '0' + str(date.month)
        else:
            month = str(date.month)
        if date.day < 10:
            day = '0' + str(date.day)
        else:
            day = str(date.day)
        date_string = str(date.year) + '-' + month + '-' + day
        #######################################
        # Query API per day, per installation #
        #######################################
        offshore_dict_24h = {"Timestamp": []}
        for i in range(48):
            if i % 2 == 0:
                minutes = 0
            else:
                minutes = 30
            ts = dt.datetime(date.year, date.month,
                             date.day, int(i / 2), minutes)
            offshore_dict_24h["Timestamp"] += [ts]
        for oi in offshore_installations:  # Gather data from sub units of the installation
            installation_dict = {}
            for bm_unit_suffix in offshore_installations[oi][1]:
                bm_unit_id = oi+bm_unit_suffix
                print(bm_unit_id)
                query_string = "https://api.bmreports.com/BMRS/B1610/V2?APIKey=9du8tosrd1t3pka&SettlementDate=" +\
                    date_string + "&Period=*&NGCBMUnitID="+bm_unit_id+"&ServiceType=CSV"
                try:
                    api_grab = pd.read_csv(query_string, skiprows=1, engine='python')
                    api_mw, api_sp = api_grab["Quantity (MW)"].to_list(), api_grab["SP"].to_list()
                    # Move api data to list, coercing to 48 HH periods by adding NaNs for missing rows
                    clean_list = [np.NaN for i in range(48)]
                    for i in range(48):
                        if i+1 in api_sp:
                            idx = api_sp.index(i+1)  # Settlement periods are back to front in order
                            clean_list[i] = api_mw[idx]
                        else:
                            clean_list[i] = np.NaN
                    # if len(mw) > 48:  # When clocks go back, just ignore the extra hour
                    #     mw = mw.iloc[:48,:]
                    # elif len(mw) < 48:  # When clocks go forward just, duplicate last hour to get 24h
                    #     mw = mw.append[mw.iloc[44:,:]]

                    ##############################################################
                    # This is the best place to del with NaN in data if required #
                    ##############################################################
                    installation_dict[bm_unit_id] = clean_list
                except:
                    print("No data for this date")
                    # # Just duplicate the previous 48 periods of data!
                    # installation_dict[bm_unit_id] = offshore_dict_multi_day[bm_unit_id][-48:]
                    # Just fill with NaN
                    installation_dict[bm_unit_id] = [np.NaN for i in range(48)]
            ####################
            # Add installation to the 24h table
            offshore_dict_24h = {**offshore_dict_24h, **installation_dict}
        date = date+dt.timedelta(1)
        for key in offshore_dict_multi_day:
            offshore_dict_multi_day[key] += offshore_dict_24h[key]
    df = pd.DataFrame(offshore_dict_multi_day)
    df = df.set_index('Timestamp')

    df.to_csv("processed_offshore_wind_data.csv")
    df.plot()
    plt.show()
    plt.show()

def onshore_wind_BM_reports_1630_API_pull(start_date, end_date):
    """This pulls HH data on the half-hourly metered onshore wind (as opposed to embedded wind)."""
    print("Started Wind data pull from BMReports API B1630")
    # This first bit makes repeated API calls, but only keeps the generators we are interested in
    generator_data = {'Timestamp': [],
                      'Onshore_wind': []
                      }
    date = start_date
    while date <= end_date:
        print(date)
        if date.month < 10:
            month = '0' + str(date.month)
        else:
            month = str(date.month)
        if date.day < 10:
            day = '0' + str(date.day)
        else:
            day = str(date.day)
        date_string = str(date.year) + '-' + month + '-' + day
        raw = pd.read_csv("https://api.bmreports.com/BMRS/B1630/V1?APIKey=9du8tosrd1t3pka&SettlementDate=" +
                          date_string + "&Period=*&ServiceType=CSV", skiprows=4, skipfooter=1, engine='python')\
              [['Settlement Date', 'Settlement Period', 'Power System Resource  Type', 'Quantity ']]
        # Discard all but generators we are interested in
        filtered = raw[raw['Power System Resource  Type'].isin(["Wind Onshore"])]
        #Need to rename the date cols to have no spaces so that lambda func below works
        filtered = filtered.rename(columns={"Settlement Date":"Date",
                            'Settlement Period':"Period",
                            'Power System Resource  Type':"Class",  'Quantity ': "Quantity"})
        # Next we construct a timestamp using date and settlement period. On day where clocks go back, periods 49 and 50 get parsed
        # as 48 to avoid datetime error.
        filtered['timestamp'] = filtered.apply(
            lambda row: dt.datetime(int(row.Date[0:4]),int(row.Date[5:7]),
                                    int(row.Date[8:10]),int((row.Period-1)/2)) if row.Period <=48
                                    else dt.datetime(int(row.Date[0:4]),int(row.Date[5:7]),
                                                     int(row.Date[8:10]),23),axis=1)

        for i in range(int(len(raw))):
            toggle = False
            if raw['Power System Resource  Type'][i] == "Wind Onshore":
                generator_data['Onshore_wind'] += [raw['Quantity '][i]]

                if raw["Settlement Period"][i] <= 48:
                    hour = int((raw["Settlement Period"][i] - 1) / 2)
                else:
                    hour = 23
                generator_data["Timestamp"] += [dt.datetime(int(raw["Settlement Date"][i][0:4]),
                                                            int(raw["Settlement Date"][i][5:7]),
                                                            int(raw["Settlement Date"][i][8:10]),
                                                            hour)]
                toggle = True
        date += dt.timedelta(days=1)
    generator_data = pd.DataFrame(generator_data)
    # this step takes rolling averages on the wind data to smooth out the frequent spikes and dropouts in the data
    # generator_data["rolling_onshore_wind"] = generator_data["Onshore_wind"].rolling(6).mean()
    # generator_data["rolling_offshore_wind"] = generator_data["Offshore_wind"].rolling(6).mean()
    # this step converts the HH data to hourly
    generator_data = generator_data.resample("H", on="Timestamp").mean()
    return generator_data

def BM_reports_1620_API_pull(start_date, end_date):
    print("Started Wind data pull from BMReports API B1620")
    # This first bit makes repeated API calls, but only keeps the generators we are interested in
    generator_data = {'Timestamp': [],
                      'Onshore_wind': [],
                      'Offshore_wind': []
                      }
    date = start_date
    while date <= end_date:
        print(date)
        if date.month < 10:
            month = '0' + str(date.month)
        else:
            month = str(date.month)
        if date.day < 10:
            day = '0' + str(date.day)
        else:
            day = str(date.day)
        date_string = str(date.year) + '-' + month + '-' + day
        raw = pd.read_csv("https://api.bmreports.com/BMRS/B1620/V1?APIKey=9du8tosrd1t3pka&SettlementDate=" +
                          date_string + "&Period=*&ServiceType=CSV", skiprows=4, skipfooter=1, engine='python')\
            [['Settlement Date', 'Settlement Period', 'Power System Resource  Type', 'Quantity']]
        # Discard all but generators we are interested in
        filtered = raw[raw['Power System Resource  Type'].isin(["Wind Offshore", "Wind Onshore"])]
        #Need to rename the date cols to have no spaces so that lambda func below works
        filtered = filtered.rename(columns={"Settlement Date":"Date",
                            'Settlement Period':"Period",
                            'Power System Resource  Type':"Class"})
        # Next we construct a timestamp using date and settlement period. On day where clocks go back, periods 49 and 50 get parsed
        # as 48 to avoid datetime error.
        filtered['timestamp'] = filtered.apply(
            lambda row: dt.datetime(int(row.Date[0:4]),int(row.Date[5:7]),
                                    int(row.Date[8:10]),int((row.Period-1)/2)) if row.Period <=48
                                    else dt.datetime(int(row.Date[0:4]),int(row.Date[5:7]),
                                                     int(row.Date[8:10]),23),axis=1)

        for i in range(int(len(raw))):
            toggle = False
            if raw['Power System Resource  Type'][i] == "Wind Onshore":
                generator_data['Onshore_wind'] += [raw['Quantity'][i]]

                if raw["Settlement Period"][i] <= 48:
                    hour = int((raw["Settlement Period"][i] - 1) / 2)
                else:
                    hour = 23
                generator_data["Timestamp"] += [dt.datetime(int(raw["Settlement Date"][i][0:4]),
                                                            int(raw["Settlement Date"][i][5:7]),
                                                            int(raw["Settlement Date"][i][8:10]),
                                                            hour)]
                toggle = True
            if raw['Power System Resource  Type'][i] == "Wind Offshore":
                generator_data['Offshore_wind'] += [raw['Quantity'][i]]
                if toggle:
                    generator_data["Timestamp"] += [dt.datetime(int(raw["Settlement Date"][i][0:4]),
                                                                int(raw["Settlement Date"][i][5:7]),
                                                                int(raw["Settlement Date"][i][8:10]),
                                                                int((raw["Settlement Period"][i] - 1) / 2))]



        date += dt.timedelta(days=1)
    generator_data = pd.DataFrame(generator_data)
    # this step takes rolling averages on the wind data to smooth out the frequent spikes and dropouts in the data
    generator_data["rolling_onshore_wind"] = generator_data["Onshore_wind"].rolling(6).mean()
    generator_data["rolling_offshore_wind"] = generator_data["Offshore_wind"].rolling(6).mean()
    # this step converts the HH data to hourly
    generator_data = generator_data.resample("H", on="Timestamp").mean()
    return generator_data


