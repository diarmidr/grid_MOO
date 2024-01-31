import pandas as pd
import datetime as dt
from matplotlib import pyplot as plt

def gridwatch_data_pull(file, start_date, end_date):
    """This function pulls 5 min generation output data from the as-downloaded CSV from gridwatch.templar.co.uk
    then converts it to hourly timestep."""
    print('started PV and nuclear data pull from gridwatch.templar.co.uk_@', dt.datetime.now())
    # Import CSV to DataFrame, discarding all but listed columns
    data = pd.read_csv(file)[[' timestamp', ' solar', ' demand', ' nuclear']]
    # remove erroneous space at start of col names
    data.rename(columns={' timestamp': 'timestamp',
                         ' solar': 'solar',
                         ' demand': 'demand',
                         ' nuclear': 'nuclear'}, inplace=True)
    data['timestamp'] = data.apply(
        lambda row: dt.datetime(int(row.timestamp[1:5]), int(row.timestamp[6:8]), int(row.timestamp[9:11]),
                                int(row.timestamp[12:14]), int(row.timestamp[15:17])), axis=1)
    # raw_data = raw_data.assign(wind_normalised=lambda row: row.timestamp.year)
    downsampled = data.resample("H", on="timestamp").mean()
    # Downsampling automatically makes timestamp the index
    filtered = downsampled[start_date:end_date]
    print('resampling_finished_@', dt.datetime.now())
    return filtered

def BM_reports_1630_API_pull(start_date, end_date):
    """Due to uncertainty around embedded generation, I've made this function to aggregate known HH metered wind farms
    in order to get a representative load profile for the ensemble. Goes like this:
    1) Obtain data for a balancing mechanism unit (or several units belonging to one site)
    2) Clean any outages.
    3) Divided output by capacity of installation to get load factor."""
    # This dictionary details the capacity of an installation, and the BM sub-units it comprises (for API query).
    offshore_installations = {"LARYO": [630, ["-1", "-2", "-3", "-4"]]}

    BMUnitID = "LARYO-1"
    #############################
    # Parse dates to API format #
    #############################
    date = start_date
    while date <= end_date:
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
        offshore_df = pd.DataFrame()
        for oi in offshore_installations:
            installation_df = pd.DataFrame()
            for bm_unit_suffix in offshore_installations[oi][1]:
                bm_unit_id = oi+bm_unit_suffix
                print(bm_unit_id)
                query_string = "https://api.bmreports.com/BMRS/B1610/V2?APIKey=9du8tosrd1t3pka&SettlementDate=" +\
                    date_string + "&Period=*&NGCBMUnitID="+bm_unit_id+"&ServiceType=CSV"
                mw = pd.read_csv(query_string, skiprows=1, engine='python')["Quantity (MW)"]
                installation_df = pd.concat([installation_df, mw], axis=1)
            # Sum teh output from sub-units and normalise by capacity
            installation_df[oi] = installation_df.sum(axis=1)/offshore_installations[oi][0]
            offshore_df = pd.concat([offshore_df, installation_df[oi]], axis=1)
            print(installation_df)
            print(offshore_df)
            # Now pass installation output and timestamp index to
        # extracted['timestamp'] = extracted.apply(
        #     lambda row: dt.datetime(int(row.Date[0:4]),int(row.Date[5:7]),
        #                             int(row.Date[8:10]),int((row.Period-1)/2)) if row.Period <=48
        #                             else dt.datetime(int(row.Date[0:4]),int(row.Date[5:7]),
        #                                              int(row.Date[8:10]),23),axis=1)
        # # Next we go through the
        # print(raw)
        # raw.to_csv("output_from_BM1610.csv")
        date += dt.timedelta(days=1)

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
    generator_data = generator_data.resample("H", on="Timestamp").mean()
    return generator_data
