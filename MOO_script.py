import numpy as np
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from output_data_handling import export_csv
import params
import objective_functions as obj_funcs
####################
# Time series data #
####################
t_data = pd.read_csv("data/direct_input_to_grid_MOO/all_temporal_data_for_input.csv")
###########################
# System level parameters #
###########################
case_study = "UKES_2024"
demand_scaling = 1  # I'm fixing demand at current levels, no point scaling it as it will also change shape
# These are unchanging portfolio parameters used in the UKES_2024 analysis
trunk_dict = {"P_Nuclear": 5,
             "BECCS": 0}
class GridMOOProblem(ElementwiseProblem):
    case_study ="UKES_2024"
    def __init__(self, **kwargs):
        if case_study == "Full":
            """This is the full variable set"""
            # Variable key, showing order for matching cost/performance params to the variable array:
            # Ones that are not dispatchable, just get added to the supply/deficit balance automatically
            # idx_0: P_nuclear, idx_1: P_PV, idx_2: P_wind_offshore, idx_3: P_BECCS
            # Dispatchable generation, in order of dispatch (most efficient storage through to most emitting back-up)
            # idx_4: P_ESS_1, idx_5: P_ESS_2, idx_6: P_ESS_3, idx_7: P_ESS_4, idx_8: P_OCGT
            # Storage duration variables:
            # idx_9: dur_ESS_1, idx_10: dur_ESS_2, idx_11: dur_ESS_3, idx_12: dur_ESS_4
            super().__init__(n_var=13,
                             n_obj=4,
                             n_ieq_constr=3,
                             xl=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                             xu=np.array([100, 100, 200, 5, 100, 10, 100, 100, 55, 24, 1000, 1000, 1000]), **kwargs)
        elif case_study == "UKES_2024":
            """UKES_2024 case study, """
            # Variable key, showing order for matching cost/performance params to the variable array:
            # Ones that are not dispatchable, just get added to the supply/deficit balance automatically
            # idx_0: P_PV, idx_1: P_wind_onshore, idx_2: P_wind_offshore
            # Dispatchable generation, in order of dispatch (most efficient storage through to most emitting back-up)
            # idx_3: P_storage, idx_4: dur_storage (h), idx_5: P_OCGT
            # If multiple storage deployed, vars go between offshore wind and OCGT and be in format
            # P1, P2, P3..., dur1, dur2, dur3...

            super().__init__(n_var=6,
                             n_obj=4,
                             n_ieq_constr=1,
                             xl=np.array([50, 20, 50, 20, 300, 0]),
                             xu=np.array([91, 20, 100, 50, 1000, 55]), **kwargs)
    def _evaluate(self, x, out, *args, **kwargs):
        case_study = "UKES_2024"
        # Dispatch function returns fuel cost (£), demand met (%) and CO2 emissions (kg/MWh).
        if case_study == "Full":
            f1, f2, f3, f4 = obj_funcs.dispatch_v2(t_data, x, params.CAPEX_dict, params.ESS_dict_full, params.OCGT_dict,
                                                   params.BECCS_dict, graph=False)
            # Constraints, in format < 0
            g1 = x[5] * x[10] - 700  # PHS Energy rating less than 700Gwh (with power < 10GW set in bounds above)
            g2 = x[4] + x[5] + x[6] + x[7] - 100  # Total storage power < 100GW
            #  Total dispatchable generation > peak demand
            g3 = -x[0] - x[1] - x[2] - x[3] - x[4] - x[5] - x[6] - x[7] - x[8] - x[9] + max(t_data["demand"]) / 1000
            out["G"] = [g1, g2, g3]
        elif case_study == "UKES_2024":
            f1, f2, f3, f4 = \
                obj_funcs.dispatch_UKES_2024(t_data, x, trunk_dict,  params.CAPEX_dict, params.ESS_dict_UKES_2024,
                                             params.OCGT_dict, params.BECCS_dict, graph=False)
            # Constraint: enough dispatchable generation to cover peak demand
            g1 = -trunk_dict["P_Nuclear"] - trunk_dict["BECCS"] - x[3] - x[5] + max(t_data["demand"]) / 1000
            out["G"] = [g1]
        print("Objectives", -f1, -f2, f3, f4)  # -ve sign is for maximising
        out["F"] = [f1, f2, f3, f4]

problem = GridMOOProblem()

algorithm = NSGA2(pop_size=200)

res = minimize(problem,
               algorithm,
               ("n_gen", 20),
               verbose=True,
               return_least_infeasible=True)
print("execution time", res.exec_time)
export_csv(res, trunk_dict, params.ESS_dict_UKES_2024)
