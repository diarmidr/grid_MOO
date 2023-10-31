import objective_functions as obj_funcs
import pandas as pd
from params import CAPEX_dict, OCGT_dict, ESS_dict
t_data = pd.read_csv("data/generator_profiles.csv")

X = [0,0,0,0,0,0,0,0,0,0,0,60]
f1 = obj_funcs.annualised_capex(X, CAPEX_dict) + \
     obj_funcs.dispatch_v2(t_data, X, ESS_dict, OCGT_dict, graph=False, metric="fuel_cost")
f2 = obj_funcs.dispatch_v2(t_data, X, ESS_dict, OCGT_dict, graph=False, metric="demand_met")
f3 = obj_funcs.dispatch_v2(t_data, X, ESS_dict, OCGT_dict, graph=False, metric="CO2_emissions")
print("f_1, total cost (£/year)", f1)
print("f_2, %demand_met", f2)
print("f_3, CO2 emissions (g/kWh)", f3)