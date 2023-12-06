import objective_functions as obj_funcs
import pandas as pd
from params import CAPEX_dict, OCGT_dict, ESS_dict, BECCS_dict
####################
# Time series data #
####################
t_data = pd.read_csv("data/generator_profiles_idealised_nuclear.csv")
###########################
# System level parameters #
###########################
# Key to variable list X, showing order for matching cost/performance params to the variable array:
# Non-dispatchable generation (GW), just get added to the supply/deficit balance automatically
# idx_0: P_nuclear, idx_1: P_PV, idx_2: P_wind_offshore, idx_3: P_BECCS
# Dispatchable generation variables (GW), in order of dispatch (most efficient storage through to most emitting back-up)
# idx_4: P_ESS_1, idx_5: P_ESS_2, idx_6: P_ESS_3, idx_7: P_ESS_4, idx_8: P_OCGT
# Storage duration variables (h):
# idx_9: dur_ESS_1, idx_10: dur_ESS_2, idx_11: dur_ESS_3, idx_12: dur_ESS_4
X = [14, 23, 92, 5, 23, 16, 0.4, 12, 18, 3.5, 54, 290, 534]
f1,f2,f3,f4 = obj_funcs.dispatch_v2(t_data, X, CAPEX_dict, ESS_dict, OCGT_dict, BECCS_dict, graph=False)
print("f_1, %demand_met", -f1)
print("Worst deficit (GW)", -f2)
print("f_3, Cost (£/MWh)", f3)
print("f_4, CO2 emissions (g/kWh)", f4)
