from matplotlib import axes
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math

def dispatch_v2(t_data, x, capex_dict, ess_dict, ocgt_dict, beccs_dict, graph):
    timestep = 1  # Hours
    # This loop just corrects any 0 values from the input so that we don't get div by 0 errors
    for i in range(len(x)):
        if x[i] == 0:
            x[i] = 0.000001
    # Calculate annualised CAPEX in £/year, 1e6 just convert from /kWh(kwh) to /GW(GWh)
    annualised_capex = (x[0] * capex_dict["Nuclear"][0]
                        + x[1] * capex_dict["PV"][0]
                        + x[2] * capex_dict["Offshore_wind"][0]
                        + x[3] * capex_dict["BECCS"][0]
                        + x[4] * capex_dict["LIB_type"][0]
                        + x[5] * capex_dict["PHS_type"][0]
                        + x[6] * capex_dict["CAES_type"][0]
                        + x[7] * capex_dict["HES_type"][0]
                        + x[8] * capex_dict["OCGT"][0]
                        + x[3] * x[9] * capex_dict["LIB_type"][1]
                        + x[4] * x[10] * capex_dict["PHS_type"][1]
                        + x[5] * x[11] * capex_dict["CAES_type"][1]
                        + x[6] * x[12] * capex_dict["HES_type"][1]
                        ) * 1e6
    # Convert to total £ CAPEX over the modelled period
    capex = annualised_capex * len(t_data) * timestep / 8760

    # Reminder of x format: P_nuc, P_PV, P_wind_offshore, P_ESS_1, P_ESS_2, P_ESS_3, dur_ESS_1, dur_ESS_2, dur_ESS_3,
    # Calculate balance of power that storage and OCGT must respond to (demand is converted from MW to GW)
    power_balance_hourly = t_data["nuclear_norm"] * x[0] \
        + t_data["PV_norm"] * x[1] + t_data["offshore_wind_norm"] * x[2] + x[3] - t_data["demand"]/1000
    simulation_years = len(power_balance_hourly)/8760
    #power_balance_hourly = power_balance_hourly.loc[0:7700]
    timestep = 1  # Timestep in h
    #print(power_balance_hourly.iloc[:,0])
    P_ESS_log = [[] for i in range(len(ess_dict))]  # Log individual ESS outputs
    SOC_ESS_log = [[] for i in range((len(ess_dict)))]  # Log individual ESS SOC
    P_ESS_tot_log = []  # Log combined EES output
    p_ocgt_log = []  # Log of OCGT hours for fuel cost and CO2 emission calculations
    deficit_log = []  # Log of unmet power deficit for use in % demand met calc
    margin_log = []  # Log of % margin as deficit/demand, e.g. a deficit is worse if it's on top of a low demand.
    for t in range(len(power_balance_hourly)):
        p_ess_tot = 0  # Combined ESS output counter
        if power_balance_hourly[t] > 0:
            p_surp = power_balance_hourly[t]
            for i in range(len(ess_dict)):  # For each ESS in the mix
                """Attempt to store surplus by charging ESS"""
                E_ESS = x[i+4] * x[i+9]  # P * duration gives energy capacity
                SOC_ESS = ess_dict[i][2]
                RT_ESS = ess_dict[i][1]
                p_soc_lim = E_ESS * (1 - SOC_ESS) / (math.sqrt(RT_ESS) * timestep)  # Charge power limit imposed by SOC remaining
                p_ess = min(p_surp, p_soc_lim, x[i+4])
                p_surp = p_surp - p_ess  # Update surplus after each storage is dispatched
                P_ESS_log[i] += [p_ess]
                p_ess_tot += p_ess
                ess_dict[i][2] += p_ess * math.sqrt(RT_ESS) * timestep * 1/E_ESS
                SOC_ESS_log[i] += [ess_dict[i][2]]
            deficit_log += [0]
            margin_log += [0]
            P_ESS_tot_log += [p_ess_tot]
            p_ocgt_log += [0]

            # param_dict = SOC_ESS and Eff_ESS
        elif power_balance_hourly[t] == 0:
            print("P=0 case")
            for i in range(len(ess_dict)):  # For each ESS in the mix
                # print('balanced')
                P_ESS_log[i] += [0]
                SOC_ESS_log[i] += [ess_dict[i][2]]
            P_ESS_tot_log += [0]
            deficit_log += [0]
            margin_log += [0]
            p_ocgt_log += [0]

        elif power_balance_hourly[t] < 0:
            #print('Energy deficit on grid')
            p_def = power_balance_hourly[t]
            for i in range(len(ess_dict)):  # For each ESS in the mix (first 3 vars are gen)
                """Attempt to meet deficit by discharging ESS"""
                E_ESS = x[i + 4] * x[i + 9]  # P * duration gives energy capacity
                SOC_ESS = ess_dict[i][2]
                RT_ESS = ess_dict[i][1]
                p_soc_lim = E_ESS * SOC_ESS * math.sqrt(RT_ESS) / timestep  # Discharge power limit imposed by SOC remaining
                p_ess = max(p_def, -p_soc_lim, -x[i + 4])  # Yields -ve value as convention for discharge
                p_def = p_def - p_ess  # Update surplus after each storage is dispatched
                P_ESS_log[i] += [p_ess]
                p_ess_tot += p_ess
                ess_dict[i][2] += p_ess * timestep * 1 / (E_ESS * math.sqrt(RT_ESS))
                SOC_ESS_log[i] += [ess_dict[i][2]]
            # Dispatch of fossil fuel plant
            if p_def < 0:
                p_ocgt = min(-p_def, x[8])  # Whichever is lesser of OCGT capacity and deficit
                p_def = p_def + p_ocgt
                p_ocgt_log += [p_ocgt]
            else:
                p_ocgt_log += [0]
            deficit_log += [p_def]
            margin_log += [100*p_def/(t_data["demand"][t]/1000)]  # Deficit as % of demand
            P_ESS_tot_log += [p_ess_tot]
    if graph:
        year_idx = [2017 + i / 8670 for i in range(len(power_balance_hourly))]
        fig_surp_def, axs1 = plt.subplots(1, 1, figsize=(6, 2), sharex=True)
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
        axs1.stackplot(year_idx, surplus, deficit, colors = ['b', 'r'])
        axs1.set_ylabel('Power surplus (GW)')

        fig_soc, axs2 = plt.subplots(1, 1, figsize=(6, 2), sharex=True)
        for i in range(len(ess_dict)):
            # Only plot SOC of storage that has been allocated a non-zero capacity
            if x[i+4] * x[i+9] > 1:
                axs2.plot(year_idx, [100*i for i in SOC_ESS_log[i]], label=ess_dict[i][0])
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
        # for i in range(len(ess_dict)):
        #     t_data = t_data.join(pd.DataFrame({"P_ESS_" + str(i): P_ESS_log[i]}))
        # for i in range(len(ess_dict)):
        #     t_data = t_data.join(pd.DataFrame({"SOC_ESS_" + str(i): SOC_ESS_log[i]}))
        # t_data = t_data.join(pd.DataFrame({"P_deficit_": deficit_log}))
        # t_data = t_data.join(pd.DataFrame({"Power_balance_exc_ESS": power_balance_hourly}))
        # t_data = t_data.join(pd.DataFrame({"P-OCGT": p_ocgt_log}))
        # t_data.to_csv('verbose_output.csv')

    """First resilience objective: % of demand met over whole period."""
    demand_met = (t_data["demand"].iloc[1:].sum()/1000 + sum(deficit_log) * timestep)  # GWh
    percentage_demand_met = 100 * demand_met / (t_data["demand"].iloc[1:].sum()/1000)
    """Second resilience objective: worst deficit"""
    worst_deficit = min(margin_log)  # %
    """Cost objective: total cost per MWh delivered (excludes surplus energy)."""
    gas_cost = sum(p_ocgt_log) * 1000 * timestep * ocgt_dict["£_ng_per_MWh"]  # MW * h * £/MWh = £
    beccs_cost = x[3] * 1000 * len(t_data) * timestep * beccs_dict["£_per_MWh"]  # MW * h * £/MWh = £
    total_cost = (gas_cost + beccs_cost + capex)/(demand_met * 1000)  # £/MWh
    """Environmental objective: CO2 emissions"""
    ocgt_emissions = (sum(p_ocgt_log) * 1000 * timestep * ocgt_dict["kg_CO2_per_MWh"])  # MW * h * kgCO2/MWh = kgCO2
    beccs_emissions = x[3] * 1000 * len(t_data) * timestep * beccs_dict["kg_CO2_per_MWh"]  # MW * h * kgCO2/MWh = kgCO2
    total_emissions = (ocgt_emissions + beccs_emissions) / (demand_met * 1000)  # kgCO2/MWh
    # -ve terms below are ones that are to be maximised
    return -percentage_demand_met, -worst_deficit, total_cost, total_emissions
