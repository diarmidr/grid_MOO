import objective_functions as obj_funcs
import pandas as pd
from params import CAPEX_dict, OCGT_dict, ESS_dict, BECCS_dict
t_data = pd.read_csv("data/generator_profiles.csv")[0:168]

X = [90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
f1,f2,f3,f4 = obj_funcs.dispatch_v2(t_data, X, CAPEX_dict, ESS_dict, OCGT_dict, BECCS_dict, graph=False)
print("f_1, %demand_met", f1)
print("f_2, Min. Margin (%)", -f2)
print("f_3, Cost (£/MWh)", f4)
print("f_4, CO2 emissions (g/kWh)", f4)