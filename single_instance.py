import objective_functions as obj_funcs
import pandas as pd
import params
####################
# Time series data #
####################
t_data = pd.read_csv("data/direct_input_to_grid_MOO/all_temporal_data_for_input.csv")
###########################
# System level parameters #
###########################
trunk_dict = {"P_Nuclear": 5,
             "BECCS": 0}  # Params that we want to fix (these are GW).
# Variable key, showing order for matching cost/performance params to the variable array:
# Ones that are not dispatchable, just get added to the supply/deficit balance automatically
# idx_0: P_PV, idx_1: P_wind_onshore, idx_2: P_wind_offshore
# Dispatchable generation, in order of dispatch (most efficient storage through to most emitting back-up)
# idx_3: P_storage, idx_4: dur_storage (h), idx_5: P_OCGT
# If multiple storage deployed, vars go between offshore wind and OCGT and be in format
# P1, P2, P3..., dur1, dur2, dur3...
X = [40, 20, 60, 30, 600, 40]
# Run the simulation
f1, f2, f3, f4 = obj_funcs.dispatch_UKES_2024(t_data, X, trunk_dict,  params.CAPEX_dict, params.ESS_dict_UKES_2024,
                                                 params.OCGT_dict, params.BECCS_dict, graph=False)

print("f_1, %demand_met", -f1)
print("Worst deficit (GW)", -f2)
print("f_3, Cost (£/MWh)", f3)
print("f_4, CO2 emissions (g/kWh)", f4)
