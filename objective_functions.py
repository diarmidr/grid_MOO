from matplotlib import axes
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math

def annualised_capex(X, cost_dict, *args, **kwargs):
    # Reminder of X format: P_nuc, P_PV, P_wind_offshore, P_ESS_1, P_ESS_2, P_ESS_3, dur_ESS_1, dur_ESS_2, dur_ESS_3, P_OCGT
    # 1000 just converts from £/kW(kWh) to £/GW(GWh) which are the units used in the demand met function
    annualised_capex = (X[0] * cost_dict["Nuclear"][0]
                        + X[1] * cost_dict["PV"][0]
                        + X[2] * cost_dict["Offshore_wind"][0]

                        + X[3] * cost_dict["LIB_type"][0]
                        + X[4] * cost_dict["PHS_type"][0]
                        + X[5] * cost_dict["CAES_type"][0]
                        + X[6] * cost_dict["HES_type"][0]
                        + X[3] * X[7] * cost_dict["LIB_type"][1]
                        + X[4] * X[8] * cost_dict["PHS_type"][1]
                        + X[5] * X[9] * cost_dict["CAES_type"][1]
                        + X[6] * X[10] * cost_dict["HES_type"][1]
                        + X[11] * cost_dict["OCGT"][0]
                        ) * 1000000\

    #print("annualised_capex=", annualised_capex)
    return annualised_capex

def dispatch_v2(t_data, X, ESS_array, ocgt_params, graph, metric):
    timestep = 1  # Hours
    # This loop just corrects any 0 values from the input so that we don't get div by 0 errors
    for i in range(len(X)):
        if X[i] == 0:
            X[i] = 0.000001
    # Reminder of X format: P_nuc, P_PV, P_wind_offshore, P_ESS_1, P_ESS_2, P_ESS_3, dur_ESS_1, dur_ESS_2, dur_ESS_3,
    # Calculate balance of power that storage and OCGT must respond to (demand is converted from MW to GW)
    power_balance_hourly = t_data["nuclear_norm"] * X[0] \
                            + t_data["PV_norm"] * X[1] \
                            + t_data["offshore_wind_norm"] * X[2] \
                            - t_data["demand"]/1000
    simulation_years = len(power_balance_hourly)/8760
    #power_balance_hourly = power_balance_hourly.loc[0:7700]
    t = 1  # Timestep in h
    #print(power_balance_hourly.iloc[:,0])
    P_ESS_log = [[] for i in range(len(ESS_array))]  # Log individual ESS outputs
    SOC_ESS_log = [[] for i in range((len(ESS_array)))]  # Log individual ESS SOC
    P_ESS_tot_log = []  # Log combined EES output
    p_ocgt_log = []  # Log of OCGT hours for fuel cost and CO2 emission calculations
    deficit_log = []  # Log of unmet power deficit for use in % demand met calc
    for p in power_balance_hourly:
        p_ess_tot = 0  # Combined ESS output counter
        if p > 0:
            p_surp = p
            for i in range(len(ESS_array)):  # For each ESS in the mix
                """Attempt to store surplus by charging ESS"""
                E_ESS = X[i+3] * X[i+7]  # P * duration gives energy capacity
                SOC_ESS = ESS_array[i][2]
                RT_ESS = ESS_array[i][1]
                p_soc_lim = E_ESS * (1 - SOC_ESS) / (math.sqrt(RT_ESS) * t)  # Charge power limit imposed by SOC remaining
                p_ess = min(p_surp, p_soc_lim, X[i+3])
                p_surp = p_surp - p_ess  # Update surplus after each storage is dispatched
                P_ESS_log[i] += [p_ess]
                p_ess_tot += p_ess
                ESS_array[i][2] += p_ess * math.sqrt(RT_ESS) * t * 1/E_ESS
                SOC_ESS_log[i] += [ESS_array[i][2]]
            deficit_log += [0]
            P_ESS_tot_log += [p_ess_tot]
            p_ocgt_log += [0]

            # param_dict = SOC_ESS and Eff_ESS
        elif p == 0:
            print("P=0 case")
            for i in range(len(ESS_array)):  # For each ESS in the mix
                # print('balanced')
                P_ESS_log[i] += [0]
                SOC_ESS_log[i] += [ESS_array[i][2]]
            P_ESS_tot_log += [0]
            deficit_log += [0]
            p_ocgt_log += [0]

        elif p < 0:
            #print('Energy deficit on grid')
            p_def = p
            for i in range(len(ESS_array)):  # For each ESS in the mix (first 3 vars are gen)
                """Attempt to meet deficit by discharging ESS"""
                E_ESS = X[i + 3] * X[i + 7]  # P * duration gives energy capacity
                SOC_ESS = ESS_array[i][2]
                RT_ESS = ESS_array[i][1]
                p_soc_lim = E_ESS * SOC_ESS * math.sqrt(RT_ESS) / t  # Discharge power limit imposed by SOC remaining
                p_ess = max(p_def, -p_soc_lim, -X[i + 3])  # Yields -ve value as convention for discharge
                p_def = p_def - p_ess  # Update surplus after each storage is dispatched
                P_ESS_log[i] += [p_ess]
                p_ess_tot += p_ess
                ESS_array[i][2] += p_ess * t * 1 / (E_ESS * math.sqrt(RT_ESS))
                SOC_ESS_log[i] += [ESS_array[i][2]]
            # Dispatch of fossil fuel plant
            if p_def < 0:
                p_ocgt = min(-p_def, X[11])  # Whichever is lesser of OCGT capacity and deficit
                p_def = p_def + p_ocgt
                p_ocgt_log += [p_ocgt]
            else:
                p_ocgt_log += [0]
            deficit_log += [p_def]
            P_ESS_tot_log += [p_ess_tot]

    if graph:
        year_idx = [2017 + i / 8670 for i in range(len(power_balance_hourly))]
        fig_surp_def, axs1 = plt.subplots(1, 1, figsize=(6,2), sharex=True)
        surp_def = [power_balance_hourly[i] - P_ESS_tot_log[i] + p_ocgt_log[i] for i in range(len(power_balance_hourly))]
        surplus = []
        deficit = []
        for i in surp_def:
            if i > 0:
                surplus += [i]
                deficit += [0]
            elif i < 0:
                surplus += [0]
                deficit += [i]
            else:
                surplus += [i]
                deficit += [i]
        axs1.stackplot(year_idx, surplus, deficit, colors =['b', 'r'])
        axs1.set_ylabel('Power surplus (GW)')

        fig_soc, axs2 = plt.subplots(1, 1, figsize=(6,2), sharex=True)
        for i in range(len(ESS_array)):
            # Only plot SOC of storage that has been allocated a non-zero capacity
            if X[i+3] * X[i+7] > 1:
                axs2.plot(year_idx, [100*i for i in SOC_ESS_log[i]], label=ESS_array[i][0])
        axs2.set_ylabel('Storage level (%)')
        axs2.set_xlabel('Year')
        axs2.legend(ncol=2, loc='right')
        axs2.legend(ncol=2, loc='right')

        # Second figure, placeholder for now
        # fig2, axs2 = plt.subplots(2, 1, sharex=True)
        # axs2[0].plot(year_idx, power_balance_hourly, label="power_balance_hourly")
        # axs2[0].plot(year_idx, P_ESS_tot_log, label="P_to_ESS")
        # axs2[0].plot(year_idx, p_ocgt_log, label='P_OCGT')
        # axs2[0].legend(ncol=2, loc='right')
        # Stitch together an output table for external processing
        # for i in range(len(ESS_array)):
        #     t_data = t_data.join(pd.DataFrame({"P_ESS_" + str(i): P_ESS_log[i]}))
        # for i in range(len(ESS_array)):
        #     t_data = t_data.join(pd.DataFrame({"SOC_ESS_" + str(i): SOC_ESS_log[i]}))
        # t_data = t_data.join(pd.DataFrame({"P_deficit_": deficit_log}))
        # t_data = t_data.join(pd.DataFrame({"Power_balance_exc_ESS": power_balance_hourly}))
        # t_data = t_data.join(pd.DataFrame({"P-OCGT": p_ocgt_log}))
        # t_data.to_csv('verbose_output.csv')
    """Percentage of historic electrical demand that could have been met by the portfolio"""
    demand_met = (t_data["demand"].iloc[1:].sum()/1000 + sum(deficit_log) * timestep)  # GWh
    percentage_demand_met = 100 * demand_met / (t_data["demand"].iloc[1:].sum()/1000)
    #print(p_ocgt_log)
    #ocgt_log = pd.DataFrame({"p_ocgt": p_ocgt_log}).to_csv("ocgt_log.csv")
    #print("sum ocgt log", sum(p_ocgt_log))
    """Fuel cost of running OCGT (£/year, so must divide by years in modelled period)"""
    fuel_cost = sum(p_ocgt_log) * timestep * 1000 * ocgt_params["£_ng_per_MWh"]  # £
    """Emissions from OCGT spread over all demand met"""
    co2_emissions = (sum(p_ocgt_log) * 1000 * timestep * ocgt_params["kg_CO2_per_MWh"]) /\
                    (t_data["demand"].iloc[1:].sum() + sum(deficit_log))  # kgCO2/MWh = gCO2/kWh
    if metric == "demand_met":
        return percentage_demand_met
    elif metric == "CO2_emissions":
        return co2_emissions
    elif metric == "fuel_cost":
        return fuel_cost